# Subscription and Entitlement UI

**Document ID:** FA-19
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend architecture and UI behavior for:

* Subscription;
* Tariff;
* Entitlement;
* Feature availability;
* Usage limits;
* Subscription status;
* Read-only mode;
* Expiry warnings;
* Deletion lifecycle;
* Upgrade/downgrade visibility;
* Business-level subscription management;
* Super Admin subscription management.

The frontend must clearly communicate what functionality is currently available to the user without allowing the UI to become the authoritative source of subscription authorization.

The backend remains authoritative for all subscription and entitlement decisions.

---

## 2. Core Principles

The frontend must follow these principles:

1. Backend is authoritative.
2. UI must never grant access by itself.
3. Hidden UI is not a security mechanism.
4. Unauthorized operations must be rejected by the backend.
5. Subscription state must be visible where relevant.
6. Entitlement restrictions must be understandable.
7. Read-only mode must be clearly communicated.
8. Expired subscriptions must not silently appear as normal active subscriptions.
9. Usage limits must be understandable before the user reaches them where possible.
10. Historical data must remain viewable according to lifecycle rules.
11. Offline devices must not bypass subscription restrictions.
12. Subscription-related UI must respect Business isolation.
13. Super Admin subscription management is separate from Business operational UI.
14. Subscription state changes must be auditable.
15. UI must not duplicate complex subscription business rules.

---

## 3. Subscription Context

Subscription belongs to the Business.

The basic hierarchy is:

```text
Platform
   ↓
Business
   ↓
Subscription
   ↓
Tariff
   ↓
Entitlements
   ↓
Usage Limits
   ↓
Available Features
```

A Branch does not own an independent subscription.

Branch-level functionality is determined by the Business subscription and the user's permissions.

---

## 4. Subscription Status

The frontend must support the authoritative subscription lifecycle.

Possible states include:

```text
ACTIVE
   ↓
EXPIRING
   ↓
EXPIRED / READ_ONLY
   ↓
DELETION_ELIGIBLE
   ↓
DELETING
   ↓
DELETED
```

Exact state names are backend-defined.

The frontend must use server-provided state rather than calculating subscription status independently.

---

## 5. Active Subscription

When the subscription is active:

* normal permitted features are available;
* modifying operations may be performed according to permissions;
* usage limits are enforced;
* subscription information remains accessible;
* expiry information may be displayed.

The UI should not repeatedly interrupt normal POS operation with subscription information.

---

## 6. Expiring Subscription

When the subscription is approaching expiry, the frontend may display:

* banner;
* dashboard warning;
* notification;
* subscription status indicator.

Example:

```text
Subscription expires in 7 days.
```

The exact warning thresholds are controlled by backend configuration.

Warnings must not block normal operations unless the backend has changed the Business state.

---

## 7. Expired Subscription

After subscription expiry, the Business enters the applicable server-defined restricted state.

The frontend must reflect the authoritative state.

Typical behavior:

```text
View existing data       → Allowed
Reports                  → Allowed
Excel export             → Allowed
History                  → Allowed
Configuration changes    → Blocked
New modifying operations → Blocked
```

The exact allowed/blocked operations are determined by backend authorization.

---

## 8. Read-Only Mode

Read-only mode is a first-class frontend state.

The UI must clearly communicate:

```text
Your subscription has expired.
Your existing data is still available for viewing and export.
Editing and new modifying operations are currently unavailable.
```

The user should not need to discover the restriction only after clicking multiple buttons.

---

## 9. Read-Only UI Behavior

In read-only mode:

* edit buttons may be hidden or disabled;
* create buttons may be disabled;
* delete/archive actions may be disabled;
* configuration forms become read-only;
* POS modifying operations are blocked;
* reports remain accessible if entitled;
* history remains accessible if entitled;
* exports remain available if entitled.

Disabled controls should explain the reason when useful.

Example:

```text
Edit Product
Unavailable because the Business subscription is read-only.
```

---

## 10. Backend Enforcement

Frontend restrictions are only UX behavior.

Every modifying API request must still be validated by the backend.

For example:

```text
Frontend:
[Edit Product] disabled

        ↓

Backend:
Subscription entitlement validation
        ↓

Modification rejected
```

A user must never be able to bypass subscription restrictions by:

* browser developer tools;
* direct API requests;
* modified frontend state;
* offline requests;
* replayed requests.

---

## 11. Entitlement Model

An entitlement represents permission to use a specific capability under the Business subscription.

Examples:

```text
BRANCH_LIMIT
EMPLOYEE_LIMIT
OWNER_LIMIT
MENU_MANAGEMENT
ADVANCED_REPORTS
PAYROLL
INVENTORY
RECIPE_MANAGEMENT
EXPORT
AUDIT_HISTORY
```

The exact entitlement identifiers are backend-defined.

Frontend code should not contain a second independent subscription rule engine.

---

## 12. Entitlement Resolution

Effective feature availability may depend on:

```text
Subscription
      +
Tariff
      +
Entitlement
      +
Business State
      +
Employee Permission
      +
Branch Scope
      +
Operational Rule
```

The frontend should consume an authoritative entitlement representation from the backend.

---

## 13. Permission vs Entitlement

Permission and subscription entitlement are different concepts.

Example:

```text
User has permission:
MANAGE_PAYROLL

Business entitlement:
PAYROLL = false
```

The feature remains unavailable.

Conversely:

```text
Business entitlement:
PAYROLL = true

User permission:
MANAGE_PAYROLL = false
```

The feature is still unavailable to that employee.

Therefore:

```text
Feature Access =
Entitlement
AND
Permission
AND
Operational Rules
```

The frontend may use this information for UI presentation, but the backend must perform the authoritative decision.

---

## 14. Feature Visibility

A feature may be represented in one of several UI states:

```text
AVAILABLE
LOCKED_BY_ENTITLEMENT
LOCKED_BY_PERMISSION
LOCKED_BY_SUBSCRIPTION_STATE
UNAVAILABLE_BY_OPERATIONAL_RULE
HIDDEN
```

The frontend should distinguish these where doing so improves user understanding.

---

## 15. Hidden vs Disabled Features

A feature may be completely hidden when:

* the user should never know about the feature;
* the tariff intentionally does not expose the feature;
* the feature is not relevant to the current role.

A feature should be visibly locked or disabled when:

* the user may benefit from knowing that it exists;
* upgrading the subscription would enable it;
* the restriction is temporary;
* the user needs to understand why an action is unavailable.

The decision should be consistent across the application.

---

## 16. Entitlement-Gated Navigation

Navigation must respect effective entitlement.

For example:

```text
Dashboard
POS
Orders
Inventory
Payroll
Reports
Audit
Subscription
```

If Payroll is unavailable because of subscription entitlement, the navigation may show:

```text
Payroll 🔒
```

or hide it according to the configured UI policy.

The frontend must not assume that a visible navigation item guarantees backend access.

---

## 17. Feature Gate Component

A shared frontend feature-gating mechanism should be used.

Conceptually:

```text
<FeatureGate entitlement="PAYROLL">
    Payroll UI
</FeatureGate>
```

The implementation must remain centralized.

Feature checks should not be duplicated across dozens of components.

---

## 18. Permission Gate and Entitlement Gate

The frontend should distinguish:

```text
PermissionGate
FeatureGate
SubscriptionStateGate
```

Example:

```text
FeatureGate(PAYROLL)
        ↓
PermissionGate(MANAGE_PAYROLL)
        ↓
Payroll UI
```

This improves consistency and reduces duplicated logic.

---

## 19. Usage Limits

Some entitlements represent numeric limits rather than simple feature access.

Examples:

```text
Maximum Branches
Maximum Employees
Maximum Owners
Maximum Devices
Maximum Storage
```

The frontend may display:

```text
Branches
8 / 10 used
```

or:

```text
Employees
42 / 50 used
```

The displayed values must come from authoritative backend data.

---

## 20. Limit Reached State

When a limit is reached:

```text
Current Usage = Limit
```

the relevant creation operation should become unavailable.

Example:

```text
Branches
10 / 10

[Add Branch] disabled
```

The UI should explain:

```text
Your current tariff allows up to 10 branches.
```

---

## 21. Limit Nearing Threshold

The frontend may show a warning when usage approaches the limit.

Example:

```text
9 / 10 branches used
1 branch remaining
```

This is informational and must not replace backend validation.

---

## 22. Limit Race Condition

Two users may attempt to consume the final available entitlement simultaneously.

The frontend must not assume that a displayed value guarantees availability.

Example:

```text
Owner A → creates Branch
Owner B → creates Branch
```

The backend determines which request succeeds.

The frontend must correctly handle:

```text
409 Conflict
```

or the appropriate entitlement-limit error.

---

## 23. Subscription Information Page

The Business subscription page should provide:

* current tariff;
* subscription status;
* start date;
* expiry date;
* remaining time where applicable;
* enabled features;
* usage limits;
* current usage;
* read-only state;
* deletion warning where applicable.

The page should be understandable without technical knowledge.

---

## 24. Subscription Summary Widget

A compact subscription summary may appear in the Business settings area.

Example:

```text
Professional

Active
Expires: 30 Nov 2026

Branches      8 / 10
Employees    42 / 50
Owners        2 / 3
```

The dashboard should not become overloaded with subscription information.

---

## 25. Expiry Countdown

The frontend may display:

```text
29 days remaining
```

However, the backend remains authoritative.

The client must not rely solely on local clock calculations for authorization.

When accurate state matters, the frontend should use the server-provided expiry/status information.

---

## 26. Subscription Renewal

If renewal functionality exists in the current deployment, the frontend may provide:

```text
Renew Subscription
```

The payment or renewal workflow must be handled by the appropriate backend/integration layer.

The frontend must not mark a subscription as active before authoritative confirmation.

---

## 27. Subscription State Refresh

After a renewal or administrative change:

1. backend updates subscription;
2. authoritative response is returned;
3. frontend refreshes subscription state;
4. entitlement cache is invalidated;
5. relevant UI updates.

The frontend must not require a full browser restart.

---

## 28. Upgrade

If upgrade is supported, the UI may show:

```text
Current Plan
Upgrade
```

Upgrade information should clearly communicate:

* new tariff;
* additional limits;
* newly available features;
* effective time;
* pricing information where applicable.

The frontend must not infer entitlement from the selected plan before backend confirmation.

---

## 29. Downgrade

Downgrade requires special handling when current usage exceeds the target tariff.

Example:

```text
Current:
8 branches

Target tariff:
5 branches
```

The frontend should clearly explain that the downgrade cannot immediately satisfy current usage constraints unless the backend defines a valid transition behavior.

Possible backend-defined states may include:

```text
Downgrade Available
Downgrade Scheduled
Downgrade Blocked
Downgrade Requires Action
```

The frontend must display the authoritative state.

---

## 30. Tariff Comparison

If tariff comparison is exposed to Business users, the UI should focus on meaningful differences:

| Capability       | Current | Higher |
| ---------------- | ------- | ------ |
| Branches         | 10      | 25     |
| Employees        | 50      | 150    |
| Payroll          | Yes     | Yes    |
| Advanced Reports | No      | Yes    |

The table must be generated from backend tariff metadata where possible.

Hard-coded feature matrices should be avoided.

---

## 31. Super Admin Subscription UI

Super Admin has a separate subscription management experience.

Super Admin may manage:

* Businesses;
* tariffs;
* subscription periods;
* entitlement configuration;
* limits;
* subscription state;
* lifecycle state.

Business employees must not receive access to Super Admin subscription administration.

---

## 32. Tariff Management

Super Admin tariff management UI may contain:

```text
Tariff Name
Description
Price
Billing Period
Feature Entitlements
Numeric Limits
Status
```

Changing a tariff must not silently rewrite historical subscription records.

---

## 33. Tariff Versioning

If tariff configuration affects historical interpretation, the system must preserve the applicable version.

Frontend should display version/context where necessary for administrative history.

Historical reports must not be reinterpreted using today's tariff configuration.

---

## 34. Subscription History

Subscription history should show:

* previous tariff;
* new tariff;
* effective time;
* actor;
* source;
* reason where applicable;
* status transition.

Example:

```text
01 Sep
Basic → Professional
Changed by Super Admin

01 Oct
Professional → Read Only
Subscription expired
```

History is read-only.

---

## 35. Subscription Audit

Important subscription changes must integrate with the Audit/History UI.

Examples:

* tariff assignment;
* tariff change;
* subscription activation;
* renewal;
* expiry;
* entitlement change;
* limit change;
* read-only transition;
* deletion eligibility;
* deletion;
* administrative override.

The frontend must display the authoritative audit record.

---

## 36. Deletion Eligibility

After the defined subscription retention period, the Business may enter:

```text
DELETION_ELIGIBLE
```

The frontend must display a clear warning.

Example:

```text
Your subscription has expired.

Your Business data is scheduled for permanent deletion
if the subscription is not reactivated before the deadline.

Deletion date: 30 Dec 2026
```

The actual deadline must come from the backend.

---

## 37. Deletion Countdown

If the backend provides a deletion deadline, the frontend may display:

```text
23 days remaining before permanent deletion
```

The frontend must not independently calculate whether deletion should occur.

The backend lifecycle state remains authoritative.

---

## 38. Deleting State

When the Business enters:

```text
DELETING
```

the frontend should show an appropriate lifecycle state.

Example:

```text
Data deletion is in progress.

This operation cannot be reversed from the application.
```

Normal operational modification UI should not remain available.

---

## 39. Deleted State

Once the Business is:

```text
DELETED
```

normal Business application access must no longer be available.

The frontend should not attempt to reconstruct or display deleted Business data from stale cache.

---

## 40. Offline Behavior

Offline devices must not bypass subscription restrictions.

The offline authorization must include the authoritative subscription/lifecycle constraints required for offline operation.

When offline authorization expires:

```text
Offline operation → blocked
```

The frontend must clearly communicate the reason.

---

## 41. Offline Read-Only State

If the Business is already restricted while the device is offline, the device must respect the latest valid authorization state.

The frontend must not assume:

```text
No internet = subscription still active
```

This is prohibited.

---

## 42. Synchronization After Subscription Change

When subscription state changes while a device is offline:

```text
Device has old state
        ↓
Reconnect
        ↓
Sync authentication
        ↓
Server validates subscription
        ↓
Latest state received
        ↓
Frontend updates
```

The server remains authoritative.

---

## 43. Subscription Conflict

A subscription-related conflict may occur when:

* device has stale entitlement state;
* subscription changed while offline;
* tariff changed;
* Business entered read-only mode;
* device attempts a prohibited modification.

The frontend should present a clear conflict/restriction state instead of a generic error.

---

## 44. Error Handling

Subscription-related errors should map to understandable UI states.

Examples:

```text
401 Unauthorized
→ Please sign in again.

403 Forbidden
→ You do not have permission for this action.

409 Conflict
→ Subscription or entitlement state has changed. Refresh and try again.

Subscription Read Only
→ Editing is unavailable because the subscription has expired.

Limit Reached
→ Your current tariff limit has been reached.
```

Backend error codes should be mapped centrally.

---

## 45. Global Subscription Banner

A global banner may be used for important subscription states.

Example:

```text
Your subscription expires in 5 days.
```

or:

```text
Your Business is currently in read-only mode.
```

The banner must not block POS operation unnecessarily.

Critical operational UI should remain usable when permitted.

---

## 46. POS Subscription Behavior

POS requires special treatment because performance and operational continuity are important.

Subscription UI must not introduce:

* repeated blocking dialogs;
* unnecessary API calls;
* slow entitlement checks;
* heavy rendering;
* repeated subscription queries.

The POS should use lightweight authoritative entitlement state.

---

## 47. Subscription State Caching

Subscription/entitlement information may be cached.

However:

* cache is not authoritative;
* TTL must be bounded;
* state changes must invalidate relevant cache;
* server response overrides stale client state.

Critical modifying operations still require backend authorization.

---

## 48. Entitlement Cache Invalidation

When subscription changes:

```text
Subscription updated
        ↓
Entitlement cache invalidated
        ↓
Business UI refreshed
        ↓
Affected feature states updated
```

Online invalidation should normally propagate within the platform's defined entitlement invalidation SLO.

---

## 49. Feature Gate Loading State

When entitlement information is loading, the frontend should avoid briefly showing unauthorized controls as available.

Preferred behavior:

```text
Unknown entitlement
        ↓
Loading / skeleton / conservative state
        ↓
Resolved entitlement
        ↓
Render allowed UI
```

For sensitive operations, fail closed.

---

## 50. Avoiding UI Flicker

The frontend should retain previously validated entitlement state when appropriate while refreshing it.

Example:

```text
Known:
PAYROLL = enabled

Refresh:
loading...

Temporary UI:
Payroll remains visible

Server:
PAYROLL = disabled

UI:
Payroll becomes locked/hidden
```

The implementation must prevent misleading interactive states.

---

## 51. Subscription Context Store

Subscription state should be managed centrally.

Conceptually:

```text
SubscriptionStore
├── status
├── tariff
├── expiry
├── entitlements
├── limits
├── usage
├── lifecycle
└── lastValidatedAt
```

Individual pages should not independently fetch and reinterpret subscription state.

---

## 52. Entitlement Context

A shared entitlement context may expose:

```text
hasFeature()
hasPermission()
hasLimit()
isReadOnly()
isExpired()
isNearExpiry()
canModify()
```

These helpers are presentation utilities only.

They must not replace backend authorization.

---

## 53. Subscription Refresh Strategy

Subscription state should be refreshed:

* on Business context initialization;
* after login where relevant;
* after branch/business context changes when required;
* after subscription-related mutations;
* after reconnect;
* after synchronization;
* periodically according to configured policy;
* when a backend response indicates stale entitlement state.

Refresh frequency must be balanced against performance.

---

## 54. Business Context Integration

Subscription belongs to the Business context.

When switching Business:

```text
Current Business
      ↓
Business switch
      ↓
Subscription context reset
      ↓
New Business subscription loaded
      ↓
Entitlements recalculated
```

Data from the previous Business must never remain visible through stale frontend state.

---

## 55. Branch Context Integration

Most subscription entitlements are Business-scoped.

However, Branch-specific permissions still apply.

When Branch changes:

```text
Business entitlement
        +
Branch permission
        ↓
Effective UI access
```

A Branch switch must not accidentally inherit another Branch's permission state.

---

## 56. Employee Context Integration

The frontend must combine:

```text
Employee
+
Role
+
Employee Overrides
+
Branch Scope
+
Subscription Entitlement
```

Example:

```text
Payroll entitlement = enabled

Employee permission = disabled

Result:
Payroll unavailable
```

---

## 57. Subscription Settings Permissions

Business subscription information may be visible to appropriate Business users.

Modification of subscription configuration must require the appropriate authority.

For example:

```text
Owner → may view subscription
Owner → may initiate allowed subscription action

Manager → normally view-only or unavailable
Cashier → unavailable
Waiter → unavailable
Cook → unavailable
```

Exact permissions are backend-defined.

---

## 58. Access Denied Page

When a user directly navigates to an unavailable route, the frontend should show a clear state.

Example:

```text
Feature unavailable

This feature is not available under the current subscription
or you do not have the required permission.
```

Where appropriate, the UI should distinguish:

```text
Subscription restriction
Permission restriction
```

without exposing sensitive authorization details.

---

## 59. Deep-Link Protection

Direct URLs must not bypass entitlement checks.

Example:

```text
/app/payroll
```

must still validate effective access.

The frontend route guard is a UX layer.

The backend API remains authoritative.

---

## 60. Subscription State and Browser Refresh

After browser refresh:

* subscription state must be restored from authoritative application state;
* stale cached state must not grant access;
* Business context must be revalidated;
* entitlement state must be safely restored.

---

## 61. Multi-Tab Behavior

Multiple browser tabs may hold the same Business context.

When subscription state changes:

```text
Tab A → subscription renewed
Tab B → old state
```

The frontend should update other tabs where practical.

The implementation may use browser-supported coordination mechanisms.

Backend authorization remains the final authority.

---

## 62. Accessibility

Subscription restrictions must be accessible.

Requirements include:

* readable status messages;
* keyboard-accessible controls;
* visible focus states;
* meaningful disabled-state explanations;
* sufficient contrast;
* screen-reader-friendly status;
* no reliance on color alone;
* accessible warning banners.

Critical lifecycle warnings must be announced appropriately without excessive interruption.

---

## 63. Responsive Design

Subscription UI must work on:

* desktop;
* laptop;
* tablet;
* narrow screens where supported.

Tables should transform into cards or horizontally scrollable regions when required.

Critical subscription status must remain visible without requiring complex navigation.

---

## 64. Loading States

Subscription pages must provide:

* skeleton/loading state;
* retry state;
* stale-state indicator where applicable;
* empty state;
* permission-restricted state;
* read-only state;
* lifecycle state.

Loading UI must not imply that the subscription is active before authoritative data is loaded.

---

## 65. Empty States

Possible empty states include:

```text
No active subscription
```

or:

```text
No tariff information available
```

These states must be distinguished from loading and authorization failures.

---

## 66. Error Recovery

When subscription information cannot be loaded:

1. preserve safe previously validated state where appropriate;
2. show a non-destructive error;
3. allow retry;
4. do not grant new modifying access based on uncertainty;
5. avoid unnecessarily logging the user out.

Security-sensitive decisions fail closed.

---

## 67. Notification Integration

Subscription lifecycle events may generate notifications:

```text
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_EXPIRED
SUBSCRIPTION_RENEWED
SUBSCRIPTION_READ_ONLY
SUBSCRIPTION_DELETION_WARNING
```

Notifications must link to the relevant subscription or settings page when the user has access.

---

## 68. Dashboard Integration

The Dashboard may show:

```text
Subscription
Professional
Active
23 days remaining
```

or:

```text
Subscription
Read Only
Renewal required
```

The dashboard widget should remain compact.

---

## 69. Reports Integration

Reports that remain available during read-only mode must continue to work according to entitlement.

Report generation must still be authorized by the backend.

The frontend must not assume that read-only means every report is available.

---

## 70. Export Integration

If Excel export remains allowed after expiry:

```text
[Export Excel]
```

should remain available.

Export requests must still validate:

* subscription state;
* entitlement;
* permission;
* Business scope;
* report access.

Export operations should be audited.

---

## 71. Subscription and Audit Integration

Subscription changes must appear in the Audit/History UI where the current user has access.

Example:

```text
Subscription Changed

Business: Example Restaurant
Previous: Basic
New: Professional
Actor: Super Admin
Time: 2026-10-05 14:20
```

The frontend must not allow editing historical subscription events.

---

## 72. Subscription and Notifications

Notification actions should not become a second subscription-management system.

The notification may contain:

```text
Subscription expires in 7 days.
[View Subscription]
```

The target page performs the authoritative loading.

---

## 73. Security Requirements

The frontend must not:

* store secret subscription credentials;
* expose Super Admin-only data to Business users;
* trust client-side entitlement values for security;
* expose another Business's subscription;
* allow modification through hidden API calls;
* store sensitive billing data unnecessarily;
* bypass read-only restrictions through offline mode.

---

## 74. Sensitive Subscription Data

The frontend should display only data required for the current role.

Examples of data that may require restricted visibility:

* internal billing metadata;
* administrative identifiers;
* internal entitlement configuration;
* Super Admin notes;
* platform-level controls.

---

## 75. Performance Requirements

Subscription UI must not noticeably affect ordinary ERP usage.

Target budgets:

| Operation                                                |          Target |
| -------------------------------------------------------- | --------------: |
| Subscription state retrieval                             |    p95 ≤ 300 ms |
| Entitlement state retrieval                              |    p95 ≤ 300 ms |
| Subscription summary render after API response           |    p95 ≤ 300 ms |
| Feature gate evaluation                                  |      p95 ≤ 5 ms |
| Local entitlement lookup                                 |      p95 ≤ 1 ms |
| Subscription page initial interactive                    |     p75 ≤ 1.5 s |
| Read-only state application after authoritative response |    p95 ≤ 300 ms |
| Entitlement invalidation propagation                     |   ≤ 30 s online |
| Subscription critical notification visibility            |          ≤ 60 s |
| Fatal subscription UI error rate                         | < 0.1% sessions |

These are frontend targets and should remain consistent with backend SLOs.

---

## 76. Offline Performance

Offline POS must not repeatedly calculate or request subscription state.

The trusted device should use its authorized offline context.

The UI should display the last validated state when appropriate:

```text
Subscription status
Last validated: 14:32
Offline
```

If offline authorization is expired, modification must be blocked.

---

## 77. Subscription State Telemetry

Frontend telemetry may track:

* subscription page load;
* entitlement loading failures;
* feature-gate errors;
* read-only state rendering failures;
* stale subscription state;
* subscription refresh failures;
* limit conflict responses;
* upgrade/renewal workflow failures.

Telemetry must not expose sensitive billing or authentication information.

---

## 78. Testing Requirements

Frontend tests must cover:

### Subscription State

* active;
* expiring;
* expired;
* read-only;
* deletion eligible;
* deleting;
* deleted.

### Entitlements

* enabled feature;
* disabled feature;
* permission + entitlement combination;
* limit reached;
* limit available;
* stale entitlement.

### Business Isolation

* Business A subscription cannot appear in Business B;
* switching Business resets subscription state;
* cached entitlement cannot cross Business boundaries.

### Branch Isolation

* Branch permissions are recalculated;
* Branch A state does not leak into Branch B.

### Offline

* valid offline authorization;
* expired offline authorization;
* subscription restriction after reconnect;
* stale entitlement handling.

### Security

* direct route access;
* direct API attempt;
* modified client state;
* unauthorized feature access.

---

## 79. AI-Agent Development Rules

AI-generated frontend code must follow these rules:

1. Never implement subscription authorization only in the frontend.
2. Never hard-code tariff permissions into individual components.
3. Use centralized feature/entitlement gates.
4. Use server-provided entitlement data.
5. Preserve Business and Branch isolation.
6. Never reuse another Business's subscription state.
7. Never silently treat expired state as active.
8. Never allow offline mode to bypass subscription restrictions.
9. Do not duplicate backend subscription rules unnecessarily.
10. Keep subscription state separate from ordinary employee permissions.
11. Use typed subscription and entitlement models.
12. Handle unknown/loading states conservatively.
13. Preserve historical subscription information.
14. Do not modify audit/history data from the frontend.
15. Add tests when entitlement behavior changes.
16. Update this document when subscription UI architecture changes.

---

## 80. Recommended Frontend Structure

Recommended feature structure:

```text
frontend/
└── src/
    └── features/
        └── subscription/
            ├── pages/
            │   ├── SubscriptionPage
            │   ├── SubscriptionHistoryPage
            │   └── TariffComparisonPage
            │
            ├── components/
            │   ├── SubscriptionSummary
            │   ├── SubscriptionStatus
            │   ├── ExpiryBanner
            │   ├── UsageLimitCard
            │   ├── EntitlementList
            │   ├── ReadOnlyBanner
            │   └── DeletionWarning
            │
            ├── gates/
            │   ├── FeatureGate
            │   ├── EntitlementGate
            │   └── SubscriptionStateGate
            │
            ├── store/
            │   └── subscriptionStore
            │
            ├── queries/
            │   ├── subscriptionQueries
            │   └── entitlementQueries
            │
            ├── services/
            │   └── subscriptionService
            │
            ├── types/
            │   ├── subscription.ts
            │   ├── entitlement.ts
            │   └── limits.ts
            │
            └── utils/
                └── subscriptionPresentation.ts
```

Super Admin subscription administration should remain separated from Business-facing subscription UI.

---

## 81. State Model

Frontend subscription state should conceptually follow:

```text
UNKNOWN
   ↓
LOADING
   ↓
RESOLVED
   ├── ACTIVE
   ├── EXPIRING
   ├── READ_ONLY
   ├── DELETION_ELIGIBLE
   ├── DELETING
   └── DELETED
```

Error state must remain separate from subscription lifecycle state.

For example:

```text
Subscription State = ACTIVE
Request State = ERROR
```

must not be interpreted as:

```text
Subscription = EXPIRED
```

---

## 82. Effective UI Access

The frontend should conceptually calculate presentation state as:

```text
Effective UI Access
=
Subscription Entitlement
+
Employee Permission
+
Branch Scope
+
Business State
+
Operational State
```

This calculation determines what should be shown or enabled.

The backend remains authoritative for actual execution.

---

## 83. Historical Integrity

The frontend must never reinterpret historical data using current subscription configuration.

For example:

* historical reports retain their report version;
* historical audit records retain their original subscription context;
* historical usage records remain historical;
* previous tariff assignments remain visible in history.

Current subscription state must not overwrite historical state.

---

## 84. Subscription Lifecycle and Data Deletion

The frontend must distinguish:

```text
Expired
```

from:

```text
Scheduled for Deletion
```

and:

```text
Deletion in Progress
```

Users must receive clear lifecycle information before permanent deletion where required by the system.

After deletion, stale browser cache must not continue presenting the Business as operational.

---

## 85. System Invariants

The following invariants apply to Subscription and Entitlement UI:

1. Backend is authoritative for subscription state.
2. Backend is authoritative for entitlement state.
3. Frontend feature gates are not security boundaries.
4. Hidden UI does not constitute authorization.
5. Disabled UI does not constitute authorization.
6. Every modifying request remains backend-authorized.
7. Subscription belongs to Business.
8. Branches do not own independent subscriptions.
9. Business subscription state cannot cross Business boundaries.
10. Employee permission does not replace subscription entitlement.
11. Subscription entitlement does not replace employee permission.
12. Branch scope remains effective.
13. Read-only state is represented explicitly.
14. Expired subscription does not appear as active.
15. Offline mode cannot bypass subscription restrictions.
16. Offline authorization must respect subscription constraints.
17. Server state overrides stale client state.
18. Subscription state is centrally managed.
19. Entitlement state is centrally managed.
20. Feature-gating logic is not duplicated unnecessarily.
21. Numeric limits are server-authoritative.
22. Displayed usage values are server-derived.
23. Limit races are resolved by the backend.
24. Frontend handles entitlement conflicts explicitly.
25. Direct route access cannot bypass backend authorization.
26. Direct API access cannot bypass subscription authorization.
27. Modified client state cannot grant access.
28. Business switching resets subscription context safely.
29. Branch switching recalculates effective access where required.
30. Employee switching recalculates effective access.
31. Stale subscription data must not grant new modifying access.
32. Unknown entitlement state must be handled conservatively.
33. Critical authorization decisions fail closed.
34. Subscription refresh must not unnecessarily block POS.
35. Subscription state must not create unnecessary POS latency.
36. Subscription cache is non-authoritative.
37. Cache invalidation occurs after authoritative changes.
38. Entitlement invalidation must propagate within the defined SLO.
39. Historical subscription state remains immutable.
40. Historical tariff assignments are not rewritten.
41. Historical reports are not reinterpreted using current subscription state.
42. Historical audit records are not modified.
43. Read-only users may access only permitted view operations.
44. Excel export remains subject to authorization.
45. Report access remains subject to entitlement and permission.
46. Audit access remains subject to permission.
47. Subscription administration is separated from ordinary Business operations.
48. Super Admin subscription controls are not exposed to Business employees.
49. Sensitive subscription metadata is role-restricted.
50. Subscription notifications do not grant authorization.
51. Subscription banners do not become a second authorization system.
52. Upgrade does not become effective until backend confirmation.
53. Renewal does not become effective until backend confirmation.
54. Downgrade state is backend-authoritative.
55. Tariff comparison should use authoritative metadata where possible.
56. Hard-coded tariff matrices should be avoided.
57. Deletion eligibility is backend-authoritative.
58. Deletion deadlines are backend-authoritative.
59. Deleting state must block ordinary Business operations.
60. Deleted Business data must not be restored from stale frontend cache.
61. Browser refresh cannot bypass subscription restrictions.
62. Multi-tab synchronization must not grant unauthorized access.
63. Subscription errors must not be interpreted as lifecycle changes.
64. Authentication errors remain distinct from subscription errors.
65. Permission errors remain distinct from entitlement errors where possible.
66. Subscription UI must support responsive layouts.
67. Subscription restrictions must remain accessible.
68. Color alone must not communicate lifecycle state.
69. Critical lifecycle warnings must be understandable.
70. Subscription UI must remain performant.
71. Subscription state loading must not imply active authorization.
72. Previously validated state may be displayed during refresh when safe.
73. Newly granted access requires authoritative confirmation.
74. Newly revoked access must take effect after authoritative state is received.
75. Subscription state must remain attributable to the current Business context.
76. Feature state must not leak between Business contexts.
77. Branch-specific permission state must not leak between Branch contexts.
78. Offline cached subscription state must be bounded by authorization validity.
79. Offline synchronization must revalidate subscription state.
80. Subscription conflicts must be visible to the user where action is required.
81. Subscription changes must integrate with Audit/History.
82. Subscription lifecycle events may integrate with Notifications.
83. Subscription status may integrate with Dashboard.
84. Subscription state may integrate with global application banners.
85. Subscription configuration must not be modified from ordinary read-only UI.
86. Entitlement changes must not silently modify historical data.
87. Subscription cache failures must not grant access.
88. Subscription service failures must not silently convert restricted state into active state.
89. Feature-gate helpers are presentation utilities only.
90. Frontend subscription logic must remain aligned with backend contracts.
91. Subscription API contracts must be typed.
92. Entitlement identifiers must be centrally defined.
93. UI must handle unknown future entitlements safely.
94. Unsupported entitlement values must not accidentally grant access.
95. Numeric limit values must be validated before display.
96. Invalid subscription responses must not create active state.
97. Subscription history is read-only.
98. Tariff history is read-only.
99. Deletion history is read-only.
100. Subscription UI changes must preserve auditability and historical integrity.

---

## 86. Related Documents

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/07_Frontend/18_Audit_and_History_UI.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database Architecture

* `docs/04_Architecture/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/05_Database/29_Database_Security.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/03_Subscription_and_Tariffs.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

---

## 87. Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `19_Subscription_and_Entitlement_UI.md`

**Previous Document:** `18_Audit_and_History_UI.md`

**Next Document:** `20_Offline_Mode_and_Synchronization_UI.md`

