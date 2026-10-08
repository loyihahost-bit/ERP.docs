# Settings and Business Configuration UI

**Document ID:** FA-21
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend architecture and UI behavior for:

* Business Settings;
* Branch Settings;
* Business Configuration;
* Branch Configuration;
* Operational Configuration;
* Feature Configuration;
* Notification Configuration;
* POS Configuration;
* Cash Register Configuration;
* Printer Configuration;
* Order Configuration;
* Payroll Configuration;
* Inventory Configuration;
* Menu-related configuration;
* Configuration versions;
* Configuration approval;
* Configuration effective dates;
* Configuration conflicts;
* Configuration history;
* Configuration access control;
* Offline configuration;
* Configuration synchronization.

The frontend must provide a centralized and understandable configuration experience while preserving the system's security, historical integrity and multi-Branch isolation.

---

## 2. Core Principles

The frontend must follow these principles:

1. Business configuration is Business-scoped.
2. Branch configuration is Branch-scoped.
3. Configuration must never cross Business boundaries.
4. Branch configuration must never accidentally affect another Branch.
5. Backend remains authoritative.
6. Frontend configuration state is not a security boundary.
7. Important configuration changes are versioned.
8. Historical configuration must remain reconstructable.
9. Configuration changes must be attributable.
10. Configuration approval must be explicit where required.
11. Effective configuration must have a deterministic activation point.
12. Stale configuration updates must not silently overwrite newer changes.
13. Configuration changes must respect permissions.
14. Subscription entitlement must be respected.
15. Read-only subscription state blocks modifying configuration.
16. Offline configuration must use the latest valid authorized configuration.
17. Configuration synchronization must not rewrite historical transactions.
18. POS configuration must remain fast and simple.
19. Complex configuration must not unnecessarily complicate daily POS workflows.
20. Important configuration changes must integrate with Audit/History.

---

## 3. Configuration Hierarchy

The frontend should represent configuration using the following hierarchy:

```text id="cfgh01"
Platform
   ↓
Business
   ↓
Branch
   ↓
Operational Context
```

Examples:

```text id="cfgh02"
Business
 ├── General Settings
 ├── Menu Settings
 ├── Pricing Settings
 ├── Inventory Settings
 ├── Payroll Settings
 ├── Notification Settings
 └── Order Settings

Branch
 ├── Local Menu
 ├── Local Pricing
 ├── POS Settings
 ├── Printer Settings
 ├── Cash Register Settings
 └── Branch Operational Settings
```

---

## 4. Settings Center

Business users should have a centralized Settings area.

Suggested structure:

```text id="set01"
Settings

├── Business
├── Branches
├── Employees & Permissions
├── POS
├── Orders
├── Menu & Pricing
├── Inventory
├── Payroll
├── Notifications
├── Printers
├── Devices
├── Subscription
├── Audit & History
└── Advanced
```

The exact navigation depends on the employee's permissions and subscription entitlements.

---

## 5. Business Settings

Business-level settings may include:

* Business name;
* business contact information;
* timezone;
* currency;
* default operational settings;
* default notification preferences;
* default order behavior;
* business-level configuration;
* selected dashboard defaults.

Only authorized users may modify Business settings.

---

## 6. Branch Settings

Branch settings belong to a specific Branch.

Example:

```text id="branch01"
Branch A

General
POS
Cash Register
Printers
Menu
Pricing
Inventory
Notifications
Operational Settings
```

A Branch configuration change must affect only the selected Branch.

---

## 7. Branch Context

When a user enters Branch settings, the active Branch must be clearly visible.

Example:

```text id="branch02"
Settings
Branch: Chilanzar Branch
```

The frontend must not rely on hidden Branch context.

---

## 8. Branch Switching

When Branch changes:

1. current configuration context is cleared;
2. new Branch context is loaded;
3. permissions are recalculated;
4. Branch configuration is refreshed;
5. Branch-specific menu/pricing state is refreshed;
6. stale Branch data is not displayed.

---

## 9. Business Switching

If multiple Business contexts are supported for the current user:

```text id="business01"
Business A
Business B
Business C
```

switching Business must reset:

* configuration state;
* Branch context;
* permission state;
* entitlement state;
* cached settings;
* unsaved Business-specific configuration state.

Data from the previous Business must never remain visible.

---

## 10. Configuration Categories

Frontend configuration should distinguish:

### Business Configuration

Applies across the Business.

### Branch Configuration

Applies only to a Branch.

### Employee Configuration

Applies to an Employee.

### Device Configuration

Applies to a trusted device.

### Operational Configuration

Controls operational behavior.

### Feature Configuration

Controls configurable product features.

### Presentation Configuration

Controls user interface preferences.

These categories should not be mixed unnecessarily.

---

## 11. Configuration Scope Indicator

Every configuration screen should communicate its scope.

Example:

```text id="scope01"
Business-wide setting
```

or:

```text id="scope02"
Branch-specific setting
Branch: Chilanzar
```

This reduces accidental cross-Branch modifications.

---

## 12. Configuration Inheritance

Where a Branch uses Business defaults, the UI may show:

```text id="inherit01"
Using Business default
```

Example:

```text id="inherit02"
Receipt Footer
Business default

[Override for this Branch]
```

The frontend should clearly distinguish inherited values from explicit Branch overrides.

---

## 13. Branch Override

A Branch may override a Business-level configuration where the backend permits it.

Example:

```text id="override01"
Business:
Currency = UZS

Branch:
Using Business default
```

or:

```text id="override02"
Branch:
Custom receipt footer enabled
```

Branch overrides must remain Branch-scoped.

---

## 14. Configuration Precedence

The effective configuration should conceptually follow:

```text id="precedence01"
Business Default
       ↓
Branch Override
       ↓
Employee/Device Context
       ↓
Effective Operational Configuration
```

Exact precedence is defined by the relevant backend/domain rules.

The frontend must not invent precedence rules.

---

## 15. Configuration Read State

Every settings page should support:

* loading;
* loaded;
* saving;
* saved;
* validation error;
* authorization error;
* conflict;
* read-only;
* unavailable;
* system error.

---

## 16. Read-Only Settings

If the Business subscription is read-only:

* settings remain viewable where authorized;
* modifying controls are disabled or hidden;
* current configuration remains visible;
* historical configuration remains accessible where permitted.

Example:

```text id="readonly01"
Business settings are currently read-only
because the subscription has expired.
```

---

## 17. Permission Control

Settings access must respect:

```text id="perm01"
Employee
+
Role
+
Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

The frontend should use centralized permission gates.

---

## 18. Unauthorized Settings

If the user opens an unauthorized settings route directly:

```text id="unauth01"
Access unavailable

You do not have permission to manage this configuration.
```

The frontend must not expose sensitive configuration values merely because the user can access the route.

---

## 19. Configuration Entitlement

Some configuration sections may require subscription entitlements.

Example:

```text id="ent01"
Payroll Settings
LOCKED

Reason:
Payroll is not included in the current subscription.
```

Feature entitlement and employee permission remain separate checks.

---

## 20. Settings Navigation

Settings navigation should display only relevant sections.

Possible behavior:

```text id="nav01"
Visible
Locked
Hidden
```

Locked sections may be shown when upgrading would make the feature available.

---

## 21. Configuration Form Design

Configuration forms should:

* use clear labels;
* group related settings;
* show current value;
* explain important constraints;
* validate locally where safe;
* validate authoritatively on server;
* prevent accidental destructive changes;
* show save status.

Forms should avoid exposing unnecessary technical fields.

---

## 22. Draft vs Effective Configuration

Where configuration changes require approval or scheduled activation, the frontend should distinguish:

```text id="draft01"
Current Effective Configuration
```

from:

```text id="draft02"
Pending Configuration
```

Example:

```text id="draft03"
Current:
Price = 30,000

Pending:
Price = 32,000

Effective:
Next Cash Session
```

---

## 23. Configuration Save Workflow

Normal configuration workflow:

```text id="save01"
Edit
 ↓
Local Validation
 ↓
Permission/Entitlement Check
 ↓
Submit
 ↓
Server Validation
 ↓
Version Check
 ↓
Save
 ↓
Audit
 ↓
Effective/Scheduled State
 ↓
UI Refresh
```

The frontend must not assume success before the authoritative response.

---

## 24. Configuration Version

Important configuration changes should display version information where useful.

Example:

```text id="ver01"
Configuration Version
v42
```

The frontend should use version identifiers for optimistic concurrency.

---

## 25. Optimistic Concurrency

When a configuration is edited:

```text id="conc01"
Loaded Version = 42
```

The save request must include the expected version where required.

If another user changes the configuration:

```text id="conc02"
Server Version = 43
```

the frontend must show a conflict.

---

## 26. Configuration Conflict UI

Example:

```text id="conf01"
Configuration changed

Another user updated this setting while
you were editing it.

Your changes were not applied.

[Reload Current]
[View Changes]
```

The frontend must not silently overwrite version 43.

---

## 27. Conflict Resolution

Where supported, the UI may provide:

```text id="conf02"
Current Server Value
Your Value
Previous Value
```

The user may then intentionally submit a new version.

The frontend must not automatically merge critical business configuration.

---

## 28. Atomic Configuration Changes

Where a configuration operation contains multiple related fields, the UI should submit them as one logical command where backend supports atomicity.

Example:

```text id="atomic01"
Receipt Header
Receipt Footer
Printer
```

must not leave the configuration in an unintended partial state.

---

## 29. Configuration Approval

If approval is required:

```text id="approval01"
Draft
  ↓
Submitted
  ↓
Pending Approval
  ↓
Approved
  ↓
Effective
```

The frontend should display the current state.

---

## 30. Approval Permissions

Only authorized users may approve configuration.

A user must not approve their own change when the business rule requires separation of duties.

The exact rule is backend-defined.

---

## 31. Scheduled Configuration

Some configuration may become effective at a future operational boundary.

Example:

```text id="scheduled01"
Status:
Scheduled

Effective:
Next Cash Session
```

The frontend must display:

* current configuration;
* pending configuration;
* effective condition.

---

## 32. Cash Session Boundary

Menu and pricing changes follow the accepted rule:

**New configuration becomes operational from the next Cash Session.**

The frontend must clearly communicate this behavior where relevant.

Example:

```text id="cashboundary01"
Price change saved.

It will become active from the next Cash Session.
```

---

## 33. Active Cash Session

The frontend must not imply that a newly configured price is already active if the current Cash Session continues using the previous configuration.

This distinction is particularly important for POS users.

---

## 34. Configuration History

Settings should provide access to relevant history where authorized.

History may show:

* old value;
* new value;
* actor;
* timestamp;
* Branch;
* device;
* version;
* reason;
* effective point.

History is read-only.

---

## 35. Audit Integration

Important configuration changes must appear in Audit/History.

Examples:

* Business settings;
* Branch settings;
* POS settings;
* pricing;
* menu availability;
* printer routing;
* payroll configuration;
* notification thresholds;
* device settings;
* permission configuration.

---

## 36. Configuration Detail

For an important configuration event, the frontend may show:

```text id="detail01"
Configuration Changed

Business: Example Restaurant
Branch: Chilanzar

Changed by:
Employee A

Previous:
...

New:
...

Version:
42

Effective:
Next Cash Session

Time:
2026-10-05 14:20
```

---

## 37. Business General Settings

Business General Settings may include:

* Business display name;
* legal/display information where applicable;
* contact information;
* timezone;
* currency;
* default language;
* default operational preferences.

The exact fields are determined by Business requirements.

---

## 38. Timezone

Business timezone is important for:

* reports;
* Cash Sessions;
* attendance;
* payroll;
* notifications;
* effective dates.

Frontend should display timezone explicitly when changing it.

Example:

```text id="tz01"
Business timezone
Asia/Tashkent
```

Changing timezone is a high-impact configuration operation and should require appropriate authorization.

---

## 39. Currency

Currency configuration affects financial presentation.

The frontend must not silently convert historical amounts because the current currency setting changed.

Historical transactions retain their original financial context.

---

## 40. Language

Language preference may be:

* Business default;
* Employee preference;
* Device preference.

The exact precedence is defined by the application architecture.

Language changes should not modify business data.

---

## 41. POS Settings

POS configuration may include:

* default order type;
* visible order stages;
* product visibility;
* receipt behavior;
* table behavior;
* operational defaults;
* permitted local POS options.

The frontend should keep POS settings separate from core security permissions.

---

## 42. Order Settings

Order configuration may include:

* enabled order types;
* status/stage configuration;
* item visibility;
* order numbering presentation;
* cancellation behavior;
* operational workflow settings.

Backend validates all business rules.

---

## 43. Order Status Configuration

Owner or authorized employees may configure permitted order statuses.

Example:

```text id="status01"
New
Preparing
Ready
Completed
Cancelled
```

The frontend should support:

* enable/disable;
* ordering where supported;
* label configuration where allowed;
* item-level visibility where configured.

---

## 44. Kitchen Workflow Configuration

Kitchen workflow settings may define:

* stages;
* product routing;
* printer routing;
* item visibility.

These settings should not be confused with actual order state.

Configuration changes must not rewrite historical orders.

---

## 45. Printer Settings

Printer configuration may include:

* printer name;
* printer type;
* routing;
* Branch;
* enabled/disabled;
* print destination;
* retry behavior where configurable.

Printer failure must not be presented as Order failure.

---

## 46. Printer Configuration Security

Only authorized users may modify printer configuration.

The frontend must not expose unnecessary network/device credentials.

Sensitive configuration values should be masked.

---

## 47. Cash Register Settings

Cash register settings may include:

* register name;
* Branch association;
* operational status;
* receipt configuration;
* permitted printer routing.

The current system assumes one register per Branch, while architecture should not unnecessarily block future multiple registers.

---

## 48. Cash Session Configuration

Cash Session behavior is controlled by the business/system rules.

The frontend should not allow arbitrary changes to historical Cash Sessions through Settings.

Historical sessions remain immutable after closure except through correction mechanisms.

---

## 49. Inventory Settings

Inventory configuration may include:

* low-stock thresholds;
* inventory display preferences;
* warehouse configuration;
* variance behavior;
* operational alerts.

The frontend must distinguish configuration from actual Inventory Transactions.

---

## 50. Recipe Settings

Recipe-related settings may include:

* approval behavior;
* visibility;
* permissions;
* version behavior.

Recipe modification must respect the established approval and permission model.

---

## 51. Menu Settings

Menu configuration may include:

* categories;
* Product visibility;
* Business menu;
* Branch availability;
* pricing.

Detailed Menu/Pricing behavior remains defined in:

`14_Menu_and_Pricing_UI.md`

and related backend/system documents.

---

## 52. Payroll Settings

Payroll configuration may include:

* salary calculation method;
* shift-based rules;
* percentage rules;
* daily rules;
* bonus configuration;
* payroll period settings.

Payroll settings require appropriate permission and subscription entitlement.

---

## 53. Attendance Settings

Attendance-related configuration may include:

* attendance behavior;
* shift configuration;
* lateness rules;
* attendance visibility.

The frontend must not modify historical attendance records through configuration screens.

---

## 54. Notification Settings

Business/Branch notification configuration may include:

* low-stock threshold;
* alert severity;
* enabled notification types;
* recipient configuration where permitted.

Notification configuration must not grant permissions.

---

## 55. Dashboard Configuration

Owners may configure dashboard presentation where supported:

* widgets;
* default sections;
* visible cards;
* layout preferences.

Dashboard configuration is presentation configuration unless explicitly defined otherwise.

It must not modify Business operational data.

---

## 56. Employee Settings

Employee-specific configuration may include:

* role;
* permissions;
* Branch assignments;
* notification preferences;
* UI preferences.

Permission management must use the dedicated access-control architecture.

---

## 57. Device Settings

Trusted device settings may include:

* device display name;
* Branch association;
* device status;
* trusted state information.

Device trust must never be granted purely through a frontend setting.

---

## 58. Subscription Settings

Subscription configuration is handled through:

`19_Subscription_and_Entitlement_UI.md`

The Settings Center may link to subscription management.

The frontend must not duplicate subscription administration logic.

---

## 59. Offline Configuration

When offline:

* existing configuration remains available;
* editing configuration should be limited to operations explicitly supported offline;
* latest valid local configuration is used;
* configuration changes are not assumed to be server-effective;
* synchronization occurs after reconnect.

The frontend must clearly identify offline configuration state.

---

## 60. Offline Configuration Indicator

Example:

```text id="offcfg01"
Using offline configuration

Last synchronized:
10:32

Configuration may be outdated.
```

This should be available where configuration freshness matters.

---

## 61. Offline Configuration Modification

By default, complex Business configuration should require online server validation.

If a specific configuration operation is permitted offline, it must:

* have explicit offline authorization;
* have operation UUID;
* be locally persisted;
* synchronize later;
* preserve configuration version;
* handle conflicts explicitly.

The frontend must not assume all settings are offline-editable.

---

## 62. Configuration Synchronization

After reconnect:

```text id="cfgsync01"
Pending Transactions
        ↓
Configuration Validation
        ↓
Configuration Synchronization
        ↓
Latest Effective Configuration
        ↓
UI Refresh
```

Transaction synchronization retains priority.

---

## 63. Configuration Cache

Configuration may be cached for performance.

However:

* cache is not authoritative;
* Business and Branch scope must be included;
* version identifiers must be retained;
* invalidation must occur after authoritative changes;
* stale configuration must not grant unauthorized access.

---

## 64. Unsaved Changes

The frontend should protect users from accidentally losing configuration changes.

When navigating away:

```text id="unsaved01"
You have unsaved changes.

Leave without saving?
```

Options:

```text
Stay
Discard
```

The frontend must not silently discard important configuration changes.

---

## 65. Auto-Save

Auto-save should be used only where appropriate.

Critical business configuration should generally use explicit save/submit behavior.

Auto-save must not create uncontrolled configuration versions.

---

## 66. Validation

Frontend validation should provide immediate feedback for obvious errors.

Examples:

* invalid number;
* missing required field;
* invalid percentage;
* invalid range;
* incompatible values.

Server validation remains authoritative.

---

## 67. Validation Error

Example:

```text id="val01"
Invalid value

Markup must be between 0% and 100%.
```

The frontend should associate errors with the relevant field.

---

## 68. Business Rule Error

Some errors cannot be validated locally.

Example:

```text id="rule01"
This configuration cannot be activated
because another required configuration is missing.
```

The server response should be mapped to a clear business-level message.

---

## 69. Configuration Loading Performance

Settings pages should remain responsive.

Targets:

| Operation                             |          Target |
| ------------------------------------- | --------------: |
| Settings page initial interactive     |     p75 ≤ 1.5 s |
| Configuration read after API response |    p95 ≤ 300 ms |
| Local form validation                 |     p95 ≤ 50 ms |
| Save button response after request    |    p95 ≤ 300 ms |
| Configuration conflict display        |    p95 ≤ 300 ms |
| Local settings navigation             |    p95 ≤ 100 ms |
| Configuration cache lookup            |     p95 ≤ 20 ms |
| Settings fatal UI error rate          | < 0.1% sessions |

Heavy historical configuration queries should not block normal settings interaction.

---

## 70. POS Performance Protection

Settings architecture must not add unnecessary overhead to POS.

Configuration reads required for POS should use:

* efficient endpoints;
* lightweight DTOs;
* cached effective configuration;
* bounded payloads.

The POS must not load the entire Settings dataset.

---

## 71. Configuration State Store

A centralized configuration state model may contain:

```text id="store01"
ConfigurationStore
├── business
├── branch
├── effective
├── pending
├── versions
├── permissions
├── entitlements
└── synchronization
```

Individual settings pages should not independently maintain conflicting versions of the same configuration.

---

## 72. Effective Configuration

The frontend may consume a server-provided effective configuration representation.

Example:

```text id="effective01"
Effective POS Configuration
Effective Menu
Effective Pricing
Effective Notifications
```

This is preferable to requiring every component to independently reconstruct configuration precedence.

---

## 73. Configuration Refresh

After a successful configuration change:

1. server returns authoritative result;
2. configuration cache is invalidated;
3. configuration store is updated;
4. affected screens refresh;
5. dependent UI updates;
6. Audit/History receives the event.

---

## 74. Dependent Configuration

Some settings depend on other settings.

Example:

```text id="dep01"
Payroll enabled
        ↓
Payroll settings available
```

or:

```text id="dep02"
Printer routing enabled
        ↓
Printer configuration available
```

The frontend may guide the user through dependencies, but the backend remains authoritative.

---

## 75. Configuration Deactivation

When a configuration option is disabled:

* existing historical records remain;
* historical transactions remain;
* previous versions remain;
* new operations use the new effective configuration.

The frontend must communicate impact where significant.

---

## 76. Destructive Configuration Changes

Changes that can significantly affect operations should require stronger confirmation.

Examples:

* disabling an order type;
* disabling a critical printer;
* changing Business timezone;
* changing important payroll settings;
* removing a Branch configuration;
* disabling a major workflow.

Confirmation should explain the operational impact.

---

## 77. Dangerous Change Confirmation

Example:

```text id="danger01"
Disable Phone Delivery?

New phone delivery orders will no longer be available
after this configuration becomes effective.

Existing orders are not changed.

[Cancel]
[Confirm]
```

The frontend should not use generic "Are you sure?" dialogs for high-impact configuration.

---

## 78. Configuration Rollback

The frontend must not implement rollback by deleting or overwriting history.

Rollback means:

```text id="rollback01"
Previous configuration
        ↓
Create new configuration state
        ↓
New version
        ↓
Effective according to rules
```

Historical versions remain intact.

---

## 79. Configuration Version History UI

Example:

```text id="verhist01"
Version 43
Effective: Next Cash Session
Created by: Owner

Version 42
Effective: Previous Cash Session
Created by: Manager

Version 41
Effective: Previous
Created by: Owner
```

Version history is read-only.

---

## 80. Configuration Comparison

Where useful, authorized users may compare versions.

Example:

```text id="compare01"
Version 42
Price: 30,000

Version 43
Price: 32,000
```

Comparison should clearly identify:

* added;
* removed;
* changed;
* unchanged.

---

## 81. Configuration Search

Large Settings areas should support search/filtering.

Search may include:

* setting name;
* category;
* Branch;
* status;
* effective state.

Search must remain permission-aware.

---

## 82. Configuration Export

If configuration export is supported:

* export must be authorized;
* Business scope must be enforced;
* sensitive fields must be excluded or masked;
* export should be audited;
* large exports should use background jobs.

Configuration export must not expose another Business's configuration.

---

## 83. Configuration Import

If configuration import is supported in future:

* uploaded data must be validated;
* Business scope must be enforced;
* permissions must be checked;
* conflicts must be handled;
* import must be auditable;
* preview/validation should occur before activation.

Import must not silently overwrite current configuration.

---

## 84. Settings Notifications

The UI may notify users when:

* configuration was approved;
* configuration became effective;
* configuration conflict occurred;
* another user changed the configuration;
* a required configuration is missing;
* subscription prevents modification.

---

## 85. Audit Notification Example

```text id="auditnotif01"
Configuration changed

A Manager changed Branch POS settings.
[View Change]
```

The notification should respect the user's permissions.

---

## 86. Accessibility

Settings UI must support:

* keyboard navigation;
* visible focus;
* semantic form labels;
* accessible validation errors;
* screen-reader-friendly status;
* accessible confirmation dialogs;
* accessible disabled-state explanations;
* sufficient contrast;
* no color-only meaning.

---

## 87. Responsive Design

Settings must work on:

* desktop;
* laptop;
* tablet;
* narrow screens where supported.

A complex settings sidebar may collapse into:

```text id="responsive01"
Settings
[Select category ▼]
```

on narrow screens.

---

## 88. Loading and Skeletons

Settings pages should use:

* section skeletons;
* field loading states;
* disabled save while loading;
* retry state.

The UI must not show default values as authoritative configuration before loading completes.

---

## 89. Empty State

If a configuration category has no configurable values:

```text id="empty01"
No configurable settings are available for your account.
```

This must be distinguished from:

* loading;
* unauthorized;
* unavailable entitlement;
* server error.

---

## 90. Error Recovery

For configuration read failures:

1. preserve safe previously validated state where appropriate;
2. display an error;
3. provide retry;
4. do not allow uncertain modification;
5. do not silently fall back to arbitrary defaults.

---

## 91. Security Requirements

The frontend must not:

* expose secrets;
* expose hidden Business configuration;
* expose another Branch's configuration;
* trust client-side permission state;
* trust client-side entitlement state;
* grant device trust locally;
* bypass read-only state;
* bypass configuration approval;
* bypass version checks.

---

## 92. Sensitive Configuration

Sensitive configuration values should be:

* masked;
* minimally exposed;
* role-restricted;
* excluded from unnecessary logs;
* excluded from analytics.

Examples may include:

* integration credentials;
* internal device configuration;
* security settings;
* private endpoint configuration.

---

## 93. Configuration Telemetry

Frontend telemetry may track:

* settings page load;
* configuration save success/failure;
* conflict frequency;
* validation failures;
* authorization failures;
* configuration loading latency;
* stale configuration events.

Sensitive configuration values must never be sent to telemetry.

---

## 94. Testing Requirements

Frontend tests must cover:

### Business Context

* Business switching;
* Business isolation;
* configuration reset.

### Branch Context

* Branch switching;
* Branch isolation;
* Branch override.

### Permissions

* Owner access;
* Manager limited access;
* unauthorized access;
* permission changes.

### Subscription

* active;
* read-only;
* entitlement disabled;
* limit reached.

### Configuration

* load;
* edit;
* save;
* validation;
* version conflict;
* approval;
* scheduled activation;
* rollback as new version.

### Offline

* cached configuration;
* stale configuration;
* offline read-only;
* configuration synchronization;
* conflict handling.

### Historical Integrity

* old configuration remains visible;
* current configuration does not rewrite history;
* historical transaction context remains unchanged.

---

## 95. AI-Agent Development Rules

AI-generated frontend code must follow these rules:

1. Never place Business configuration in Branch-only state.
2. Never place Branch configuration in global Business state.
3. Never trust client-side authorization.
4. Never hard-code subscription authorization into settings components.
5. Use centralized permission and entitlement gates.
6. Preserve configuration version identifiers.
7. Use optimistic concurrency where required.
8. Never silently overwrite newer configuration.
9. Never implement silent last-write-wins for important configuration.
10. Never delete historical configuration during rollback.
11. Rollback must create a new version/state.
12. Keep current and historical configuration separate.
13. Keep effective and pending configuration separate.
14. Respect Cash Session effective boundaries.
15. Do not modify historical transactions from Settings UI.
16. Do not allow offline configuration changes unless explicitly supported.
17. Preserve Business and Branch context during synchronization.
18. Keep sensitive settings out of logs and telemetry.
19. Use typed configuration models.
20. Centralize configuration API access.
21. Add tests for configuration conflicts.
22. Add tests for Business/Branch isolation.
23. Add tests for subscription restrictions.
24. Add tests for read-only state.
25. Update this document when configuration architecture changes.

---

## 96. Recommended Frontend Structure

Recommended structure:

```text id="struct01"
frontend/
└── src/
    └── features/
        └── settings/
            ├── pages/
            │   ├── SettingsPage
            │   ├── BusinessSettingsPage
            │   ├── BranchSettingsPage
            │   └── ConfigurationHistoryPage
            │
            ├── components/
            │   ├── SettingsNavigation
            │   ├── SettingsSection
            │   ├── ConfigurationForm
            │   ├── ConfigurationStatus
            │   ├── PendingConfiguration
            │   ├── VersionBadge
            │   ├── ConflictDialog
            │   └── UnsavedChangesDialog
            │
            ├── categories/
            │   ├── business/
            │   ├── branch/
            │   ├── pos/
            │   ├── orders/
            │   ├── inventory/
            │   ├── payroll/
            │   ├── notifications/
            │   ├── printers/
            │   └── devices/
            │
            ├── queries/
            │   └── configurationQueries
            │
            ├── mutations/
            │   └── configurationMutations
            │
            ├── store/
            │   └── configurationStore
            │
            ├── history/
            │   ├── configurationHistory
            │   └── configurationComparison
            │
            ├── validation/
            │   └── configurationValidators
            │
            ├── services/
            │   └── configurationService
            │
            └── types/
                ├── configuration.ts
                ├── versions.ts
                └── scopes.ts
```

Feature-specific settings may remain close to their feature while shared configuration infrastructure remains centralized.

---

## 97. Configuration State Model

The frontend should conceptually maintain:

```text id="state01"
Configuration State
│
├── Current Effective
│
├── Draft
│
├── Pending Approval
│
├── Scheduled
│
├── Superseded
│
└── Historical
```

Only backend-authoritative state should determine operational behavior.

---

## 98. Effective Configuration Store

The application may maintain:

```text id="effective02"
EffectiveConfigurationStore
├── business
├── branch
├── pos
├── menu
├── pricing
├── inventory
├── payroll
├── notifications
└── devices
```

The store must always retain Business/Branch context.

---

## 99. Configuration Dependency Graph

Some configuration relationships can be represented as:

```text id="graph01"
Business Settings
      │
      ├── Branch Defaults
      │       │
      │       ├── POS
      │       ├── Printers
      │       └── Notifications
      │
      ├── Menu
      │       └── Pricing
      │
      └── Payroll
              └── Attendance
```

The frontend should use this structure only for presentation and navigation.

Business rules remain in the backend/domain layer.

---

## 100. System Invariants

The following invariants apply to Settings and Business Configuration UI:

1. Business settings are Business-scoped.
2. Branch settings are Branch-scoped.
3. Configuration cannot cross Business boundaries.
4. Branch configuration cannot affect another Branch unintentionally.
5. Backend remains authoritative.
6. Frontend is not a security boundary.
7. Every important configuration change is attributable.
8. Important configuration changes are versioned.
9. Historical configuration remains immutable.
10. Configuration history is read-only.
11. Rollback creates a new configuration state/version.
12. Current configuration never overwrites historical configuration.
13. Effective configuration is distinguishable from pending configuration.
14. Draft configuration is distinguishable from effective configuration.
15. Scheduled configuration has an identifiable effective point.
16. Configuration approval is explicit where required.
17. Approval requires appropriate permission.
18. Required separation of duties is respected.
19. Stale configuration updates are rejected as conflicts.
20. Silent last-write-wins is prohibited for important configuration.
21. Version identifiers are preserved.
22. Save requests use expected version where required.
23. Configuration conflict is explicitly communicated.
24. Configuration conflict does not silently discard server state.
25. Business switching resets configuration context.
26. Branch switching resets Branch configuration context.
27. Previous Business data cannot remain visible after Business switching.
28. Previous Branch data cannot remain visible after Branch switching.
29. Business defaults are distinguishable from Branch overrides.
30. Branch overrides affect only the selected Branch.
31. Effective configuration follows backend-defined precedence.
32. Frontend does not invent configuration precedence.
33. Subscription entitlement is checked.
34. Employee permission is checked.
35. Branch scope is checked.
36. Read-only subscription blocks modifying configuration.
37. Unauthorized users cannot modify configuration.
38. Hidden UI does not constitute authorization.
39. Disabled UI does not constitute authorization.
40. Direct API access cannot bypass configuration authorization.
41. Offline state cannot bypass configuration restrictions.
42. Complex configuration is not assumed to be offline-editable.
43. Offline configuration uses latest valid authorized state.
44. Configuration synchronization is authoritative.
45. Transaction synchronization retains priority over configuration synchronization.
46. Stale configuration is identifiable.
47. Cached configuration is not authoritative.
48. Cache is Business/Branch isolated.
49. Cache invalidation follows authoritative changes.
50. Configuration changes are reflected in Audit/History.
51. Audit records are immutable.
52. Historical transactions are not rewritten by configuration changes.
53. Historical prices are not rewritten.
54. Historical recipes are not rewritten.
55. Historical Set configurations are not rewritten.
56. Historical inventory deductions are not rewritten.
57. Cash Session boundaries are respected.
58. Price changes become effective according to defined session rules.
59. Active Cash Sessions do not silently change operational configuration.
60. New Cash Sessions use the latest effective configuration.
61. Existing Orders retain their historical snapshots.
62. Configuration UI does not modify historical Orders.
63. Configuration UI does not modify closed Cash Sessions directly.
64. Destructive changes require appropriate confirmation.
65. Confirmation explains significant operational impact.
66. Configuration forms validate obvious local errors.
67. Server validation remains authoritative.
68. Validation errors are distinguishable from authorization errors.
69. Business rule violations are distinguishable from validation errors.
70. Configuration errors are recoverable where possible.
71. Unknown configuration state does not grant modification access.
72. Loading state does not imply default authoritative values.
73. Unsaved changes are protected.
74. Critical configuration should not use uncontrolled auto-save.
75. Configuration versions are centrally represented.
76. Configuration state is centrally managed.
77. Individual pages do not maintain conflicting configuration state.
78. Effective configuration can be consumed centrally.
79. Configuration refresh updates affected UI.
80. Configuration refresh does not rewrite historical state.
81. Sensitive configuration values are protected.
82. Secrets are not exposed in normal settings UI.
83. Sensitive configuration is not sent to telemetry.
84. Printer configuration is separate from Order state.
85. Printer failure does not imply Order failure.
86. Cash Register configuration is Branch-scoped.
87. Future multi-register support is not blocked by current one-register assumptions.
88. Payroll configuration is entitlement-aware.
89. Inventory configuration is separate from inventory transaction state.
90. Recipe configuration is permission-aware.
91. Menu configuration follows Menu/Pricing architecture.
92. Notification configuration does not grant permissions.
93. Dashboard configuration does not modify Business operational state.
94. Device trust cannot be granted from ordinary Settings UI.
95. Subscription administration remains separate.
96. Configuration export is permission-aware.
97. Configuration import cannot silently overwrite active configuration.
98. Configuration import must preserve auditability.
99. Configuration search respects authorization.
100. Configuration history respects authorization.
101. Configuration comparison is read-only.
102. Configuration UI is responsive.
103. Configuration UI is accessible.
104. Configuration UI does not rely on color alone.
105. Settings navigation remains usable on narrow screens.
106. Settings performance does not degrade POS performance.
107. Heavy historical configuration queries do not block normal settings interaction.
108. Configuration API payloads remain bounded.
109. Configuration state is observable.
110. Configuration latency is measurable.
111. Configuration changes remain attributable to actor and context.
112. Device context is retained where required.
113. Business context is retained.
114. Branch context is retained.
115. Configuration changes are idempotent where retry is possible.
116. Duplicate configuration requests do not create duplicate versions.
117. Configuration approval requests are idempotent.
118. Configuration synchronization is idempotent.
119. Configuration state remains reconstructable.
120. Historical integrity has priority over UI convenience.

---

## 101. Related Documents

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/13_Products_Recipes_and_Sets_UI.md`
* `docs/04_Architecture/07_Frontend/14_Menu_and_Pricing_UI.md`
* `docs/04_Architecture/07_Frontend/19_Subscription_and_Entitlement_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database Architecture

* `docs/04_Architecture/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/04_Architecture/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/04_Architecture/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/29_Database_Security.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/13_Menu_and_Pricing.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 102. Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `21_Settings_and_Business_Configuration_UI.md`

**Previous Document:** `20_Offline_Mode_and_Synchronization_UI.md`

**Next Document:** `22_Frontend_State_Management_and_Data_Flow.md`

