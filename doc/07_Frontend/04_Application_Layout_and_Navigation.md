# Application Layout and Navigation

**Document ID:** FA-04
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `03_Design_System_and_UI_Principles.md`
**Next Document:** `05_Authentication_and_Session_UI.md`

---

# 1. Purpose

This document defines the application shell, layout, navigation and routing architecture for FastFood ERP.

The goal is to provide a consistent application structure while keeping operational workflows, especially POS, fast and easy to use.

The layout must support:

* multiple Business branches;
* role-based navigation;
* permission-aware navigation;
* subscription-aware UI;
* POS workflows;
* administrative workflows;
* responsive behavior;
* offline state;
* synchronization state;
* notifications;
* accessibility;
* future frontend expansion.

---

# 2. Application Shell

The application shell is the persistent UI structure surrounding feature pages.

Conceptually:

```text id="2qpx3d"
┌──────────────────────────────────────────────────────────────┐
│ Header                                                       │
│ Business | Branch | Session | Notifications | Employee      │
├────────────────┬─────────────────────────────────────────────┤
│                │                                             │
│ Navigation     │ Main Content                                │
│                │                                             │
│                │                                             │
│                │                                             │
└────────────────┴─────────────────────────────────────────────┘
```

The shell should remain stable while users navigate between normal application areas.

---

# 3. Shell Responsibilities

The Application Shell is responsible for:

* primary navigation;
* current Business context;
* current Branch context;
* employee/session context;
* notification access;
* synchronization status;
* offline status;
* global actions;
* global error handling;
* responsive navigation.

Feature-specific business logic must remain outside the shell.

---

# 4. Shell Structure

Recommended structure:

```text id="q0k2jj"
src/app/shell/
├── AppShell.*
├── Header.*
├── Sidebar.*
├── MainContent.*
├── MobileNavigation.*
├── ContextBar.*
├── GlobalStatusBar.*
└── index.*
```

The exact component breakdown may change during implementation, but responsibilities must remain separated.

---

# 5. Header

The Header contains high-level operational context.

Recommended information:

```text id="jq3a5r"
Business
Branch
Cashier / Employee
Cash Session
Notifications
Offline / Sync Status
User Menu
```

Not every element must be visible at all times.

The Header should prioritize information that affects the user's current operation.

---

# 6. Business Context

The current Business must be clearly identifiable.

Example:

```text id="c5n6p9"
FastFood Group
```

The user must never be uncertain about which Business context they are operating within.

The Backend remains authoritative for Business identity.

The frontend must not trust a client-provided Business ID without server validation.

---

# 7. Branch Context

The active Branch must be clearly visible.

Example:

```text id="w1f6g2"
Branch: Chilanzar
```

Branch switching is an important context operation.

When Branch changes, the application must recalculate or reload:

* permissions;
* menu;
* pricing;
* operational configuration;
* Branch-scoped data;
* cash context;
* offline context where applicable.

---

# 8. Branch Switcher

The Branch selector should display only Branches the employee is authorized to access.

Example:

```text id="y8f5t3"
Select Branch

● Chilanzar
○ Yunusabad
○ Sergeli
```

The user must not be able to use the UI to switch into an unauthorized Branch.

Backend validation remains mandatory.

---

# 9. Branch Switching Workflow

The conceptual workflow is:

```text id="qz1h0s"
User selects Branch
        ↓
Validate selection
        ↓
Update active context
        ↓
Reload Branch permissions
        ↓
Reload Branch configuration
        ↓
Reload menu/pricing
        ↓
Reload operational data
        ↓
Update navigation
        ↓
Render Branch context
```

The application must prevent stale Branch data from appearing as if it belonged to the new Branch.

---

# 10. Active Branch Indicator

The active Branch should have a strong visual indication.

For example:

```text id="uwqv73"
Branch: Yunusabad
```

The active Branch must not be confused with:

* available Branches;
* previously used Branch;
* default Branch;
* selected filter Branch.

---

# 11. Cash Session Context

For users working with cash operations, the UI should communicate current session state.

Example:

```text id="3nqz4a"
Cash Session
Open
Cashier: Employee
Register: Register 1
```

If no Cash Session is active:

```text id="0d7q3n"
Cash Session
Not Open
```

The exact workflow is defined in the Cash UI document.

---

# 12. Employee Context

The current employee identity should be available through the user menu or header.

Example:

```text id="c2kzv5"
Employee Name
Cashier
Branch: Chilanzar
```

The UI should not expose unnecessary sensitive information.

---

# 13. Navigation Architecture

Navigation is divided into:

```text id="v0n8b6"
Primary Navigation
Secondary Navigation
Contextual Navigation
Feature Navigation
```

### Primary Navigation

Main business areas.

### Secondary Navigation

Less frequently used administrative areas.

### Contextual Navigation

Actions related to the current page.

### Feature Navigation

Navigation inside a complex feature.

---

# 14. Primary Navigation

Recommended primary areas:

```text id="d1j4w0"
Dashboard
POS
Orders
Cash
Inventory
Products
Menu
Reports
```

The exact visible list depends on:

* employee permissions;
* role;
* Branch scope;
* subscription;
* feature availability.

---

# 15. Administrative Navigation

Administrative functions may include:

```text id="x1o3m6"
Employees
Roles & Permissions
Attendance
Payroll
Pricing
Recipes
Sets
Notifications
Configuration
Audit / History
```

These areas may be grouped to prevent the primary navigation from becoming excessively long.

---

# 16. Navigation Groups

A conceptual navigation structure:

```text id="b4r1n7"
Operations
├── POS
├── Orders
├── Cash
└── Tables

Inventory
├── Inventory
├── Products
├── Recipes
└── Sets

Menu
├── Menu
└── Pricing

People
├── Employees
├── Attendance
└── Payroll

Reports
├── Dashboard
├── Reports
└── Audit / History

Administration
├── Roles & Permissions
├── Notifications
└── Configuration
```

The actual grouping may be adjusted during UX implementation.

---

# 17. Navigation Visibility

Navigation should be permission-aware.

A user should not normally see features they cannot use.

However, hidden navigation is not a security mechanism.

The Backend must still reject unauthorized requests.

---

# 18. Permission-Based Navigation

Example:

```text id="y3z4g7"
Employee has:
orders.view
orders.create
payments.create

Navigation:
✓ Orders
✓ POS

Employee does not have:
payroll.view

Navigation:
Payroll hidden
```

The exact permission model follows the Backend authorization architecture.

---

# 19. Disabled Navigation

A feature may be shown as disabled rather than hidden when:

* the user understands the feature;
* the feature exists but is temporarily unavailable;
* subscription state blocks modification;
* a required setup step is missing.

Example:

```text id="z1t7xc"
Payroll
Disabled

Reason:
Payroll module is unavailable under the current subscription.
```

The UX decision should be consistent across the application.

---

# 20. Subscription-Aware Navigation

Subscription state can affect navigation.

When the Business becomes read-only:

```text id="x7q2jm"
View → Available
Export → Available where permitted
Modify → Blocked
```

The navigation must not suggest that blocked modification functions are available.

---

# 21. Read-Only Mode

Read-only mode should be visually identifiable.

A global indicator may appear in the Header:

```text id="f3h5d1"
READ-ONLY
Subscription expired
```

Users should still be able to:

* view allowed data;
* navigate historical records;
* export permitted reports.

Modification actions must be blocked.

---

# 22. Navigation and Business Lifecycle

Navigation must reflect Business lifecycle.

Examples:

```text id="j7v8p0"
ACTIVE
→ normal operation

READ_ONLY
→ view/export

DELETION_ELIGIBLE
→ restricted lifecycle UI

DELETING
→ restricted system state
```

The Frontend must not provide normal operational controls for a Business that is no longer operationally active.

---

# 23. Route Architecture

Routes should correspond to user-facing application capabilities.

Conceptual route map:

```text id="l7a4v3"
/login

/dashboard
/pos
/orders
/orders/:orderId

/cash
/cash/sessions
/cash/sessions/:sessionId

/inventory
/inventory/products

/products
/products/:productId

/recipes
/recipes/:recipeId

/sets
/sets/:setId

/menu
/pricing

/attendance
/payroll

/reports
/reports/:reportId

/notifications

/administration
/administration/employees
/administration/roles
/administration/configuration
```

The exact URL structure may be refined during API/frontend implementation.

---

# 24. Route Naming

Routes should be:

* predictable;
* resource-oriented;
* stable;
* readable.

Avoid unnecessary abbreviations.

Prefer:

```text id="9f6a2r"
/inventory/products
```

over:

```text id="7b4n1s"
/inv/prd
```

unless there is a strong technical reason.

---

# 25. Route Parameters

Route parameters should represent stable resource identity.

Example:

```text id="f6d1y3"
/orders/:orderId
```

The Frontend must not treat a route parameter as authorization proof.

The Backend must validate:

* Business;
* Branch;
* employee permission;
* resource access.

---

# 26. Route Guards

Routes may use guards such as:

```text id="k4t8c9"
Authentication Guard
Business Guard
Branch Guard
Permission Guard
Subscription Guard
Device Guard
```

Example:

```text id="s3k2p8"
Authenticated
   ↓
Business Context
   ↓
Branch Context
   ↓
Permission
   ↓
Subscription
   ↓
Route
```

---

# 27. Authentication Guard

Unauthenticated users should be redirected to the authentication flow.

Authenticated users should not unnecessarily return to the login page during normal navigation.

Session expiration must be handled consistently.

---

# 28. Permission Guard

Permission guards should prevent obviously unauthorized navigation.

Example:

```text id="m8y4x1"
Employee
  ↓
roles.manage
  ↓
/administration/roles
```

If the permission is absent, the route should not be presented as available.

Backend authorization remains authoritative.

---

# 29. Not Found vs Unauthorized

The Frontend should distinguish:

```text id="p8w4d2"
404
Resource does not exist

403
Resource exists but access is forbidden
```

However, the Backend may intentionally avoid revealing resource existence in certain security-sensitive cases.

The frontend must respect the API contract.

---

# 30. Navigation State

The active navigation item should reflect the current route.

Example:

```text id="h4m9q6"
Inventory
  ├── Products
  ├── Stock
  └── Warehouses
```

When the user is inside `/inventory/products`, the Inventory section remains visibly active.

---

# 31. Breadcrumbs

Breadcrumbs should be used when they improve orientation.

Example:

```text id="e3p7k2"
Products
→ Burger
→ Recipe
→ Version 4
```

Breadcrumbs are less important in POS and may be omitted there.

---

# 32. POS Navigation

POS should have a simplified navigation model.

The POS screen should minimize distractions from the sales workflow.

Conceptually:

```text id="k5r2w8"
POS
├── Products
├── Current Order
├── Tables
├── Delivery
└── Payment
```

The user should not need to navigate through multiple administrative pages to complete a sale.

---

# 33. POS Exit

Leaving POS should be intentional but not unnecessarily difficult.

If there is an unsaved/local order state, the UI should warn appropriately.

The exact behavior depends on whether the state is safely persisted locally.

---

# 34. Mobile Navigation

On narrow screens, the sidebar may become:

* drawer;
* bottom navigation;
* compact menu.

The navigation mechanism must preserve:

* active state;
* accessibility;
* permission filtering;
* Branch context.

---

# 35. Sidebar Behavior

Desktop sidebar may support:

```text id="7r0z1m"
Expanded
Collapsed
```

Collapsed mode should still provide accessible tooltips/labels.

The application should remember UI preference when appropriate.

---

# 36. Header Behavior

The Header should remain stable across normal pages.

It may contain:

```text id="u2m7p1"
Business
Branch
Cash Session
Notifications
Sync
Offline
Employee
```

The Header should not become an overloaded dashboard.

---

# 37. Global Status Bar

A small global status area may communicate:

```text id="q8d4f3"
Online
Offline
Syncing
Conflict
Read-only
```

Only relevant statuses should be displayed.

Normal operation should not fill the UI with persistent technical information.

---

# 38. Offline Indicator

Offline mode should be visible.

Example:

```text id="a7c1e4"
Offline
Last sync: 14:32
```

The indicator should not block POS interaction unless the current operation cannot safely continue.

---

# 39. Synchronization Indicator

When synchronization is active:

```text id="v9m3c7"
Syncing…
8 operations remaining
```

After successful synchronization:

```text id="k4d2r8"
Synced
```

The UI should avoid excessive animation or constant status changes.

---

# 40. Conflict Indicator

A synchronization conflict should be more prominent than ordinary synchronization activity.

Example:

```text id="r5w8n2"
Sync conflict
1 item requires attention
```

The user should be able to reach the conflict resolution workflow.

---

# 41. Notification Access

Notifications should be globally accessible.

The Header may contain:

```text id="m1j5x8"
🔔 3
```

The actual notification design should remain accessible without relying only on the icon.

Critical notifications may require stronger visual emphasis.

---

# 42. User Menu

The user menu may contain:

```text id="y6q2v4"
Profile
Current Role
Current Branch
Session Information
Device Information where appropriate
Settings
Sign Out
```

Sensitive technical information should not be exposed unnecessarily.

---

# 43. Logout

Logout should terminate the authentication session.

Logout must not automatically:

* close Cash Session;
* finalize Order;
* discard synchronized data.

If operational state remains open, the UI may warn the user where required.

---

# 44. Page Layout

Standard administrative pages should follow a predictable structure:

```text id="p6t3y9"
Page Header
├── Title
├── Description / Context
└── Primary Actions

Filters / Toolbar

Main Content

Pagination / Footer
```

Not every page requires every section.

---

# 45. Page Header

Page headers should provide:

* clear title;
* optional short description;
* primary action;
* contextual information.

Example:

```text id="f2k8x5"
Products
Manage products, recipes and availability.

[+ Add Product]
```

---

# 46. Toolbar

A toolbar may contain:

* search;
* filters;
* sort;
* export;
* refresh;
* view options.

The toolbar should prioritize the most frequently used actions.

---

# 47. Contextual Actions

Actions related to one record should normally appear:

* within the row;
* within a detail panel;
* within a contextual menu.

Do not overload the global page header with record-specific operations.

---

# 48. Detail Pages

A detail page should prioritize the most important information.

Example:

```text id="u7k4m1"
Product
├── Overview
├── Pricing
├── Branch Availability
├── Recipe
├── History
└── Audit
```

Historical and technical details may be secondary tabs or panels.

---

# 49. Tabs

Tabs should be used when sections represent closely related information.

Avoid using tabs for unrelated workflows.

Tabs should preserve:

* active state;
* accessibility;
* route state where appropriate.

---

# 50. Deep Linking

Important pages should support direct navigation through URLs.

Examples:

```text id="b8v4n6"
/orders/ORD-123

/products/PROD-456

/reports/daily/2026-10-05
```

Deep links must still validate authorization.

---

# 51. Browser Back/Forward

The application should behave predictably with browser navigation.

Back/forward navigation should not unexpectedly:

* duplicate mutations;
* lose safe state;
* switch Branch;
* submit forms.

---

# 52. Unsaved Changes

For forms containing unsaved changes, navigation away may require a warning.

Example:

```text id="c3n8y2"
You have unsaved changes.

[Stay] [Leave]
```

This should only be used when losing the state would be meaningful.

---

# 53. Route Loading

Lazy-loaded routes should provide a lightweight loading state.

The global shell should remain available where possible.

Avoid replacing the entire application with a blank screen while loading one feature.

---

# 54. Route Error Handling

If a route fails to load:

```text id="w7p4z1"
Unable to load this page.

[Retry]
```

The user should still be able to navigate to other safe application areas when possible.

---

# 55. Permission Changes During Session

Permissions may change while a user is logged in.

The frontend should refresh authorization context according to the Backend/session policy.

If access is revoked:

```text id="x2m6q8"
Access changed

Your permission to use this section is no longer available.
```

The user must not continue operating on stale permissions.

---

# 56. Branch Context Changes During Session

If Branch access changes while the session is active, the application must not continue using stale Branch permissions.

The active context should be revalidated.

---

# 57. Device Context

Where device identity is relevant, the shell may display limited device information.

The frontend must not allow users to manually impersonate another device.

Device identity remains Backend-controlled.

---

# 58. Layout Persistence

Non-critical UI preferences may be persisted locally.

Examples:

* sidebar collapsed state;
* table column preferences;
* theme;
* page density.

These preferences must not affect business correctness.

---

# 59. Navigation Performance

Navigation should be fast.

Targets include:

| Metric                               |       Target |
| ------------------------------------ | -----------: |
| Cached route transition              | p95 ≤ 300 ms |
| Main authenticated route interactive |  p75 ≤ 2.0 s |
| POS initial screen interactive       |  p75 ≤ 2.0 s |

Heavy features should be lazy-loaded when beneficial.

---

# 60. Navigation Accessibility

Navigation must support:

* keyboard access;
* visible focus;
* semantic links/buttons;
* current route indication;
* screen-reader labels;
* mobile accessibility.

The current navigation item should expose appropriate accessibility state.

---

# 61. Responsive Layout Rules

At narrow widths:

* sidebar must collapse or transform;
* tables may become horizontally scrollable or responsive;
* action groups may wrap;
* page headers may stack;
* filters may move into a drawer.

The application must avoid page-level horizontal scrolling caused by the shell.

---

# 62. Navigation Density

The navigation should remain manageable as features grow.

If the number of features increases significantly, use:

* groups;
* collapsible sections;
* search;
* role-specific navigation;
* contextual navigation.

Do not simply add more top-level navigation items indefinitely.

---

# 63. Searchable Navigation

If the application eventually contains many administrative functions, a navigation search may be introduced.

It should return only features the employee can access.

Example:

```text id="d7p2v5"
Search navigation...

Products
Recipes
Payroll
Reports
```

---

# 64. Feature Flags

Navigation may respond to feature flags.

However:

```text id="m4q8x1"
Feature Flag
≠
Permission
≠
Subscription
```

These concepts must remain separate.

A feature flag controls application availability.

Permission controls user authorization.

Subscription controls Business entitlement.

---

# 65. Navigation and Offline

Offline navigation should expose only features that can safely operate offline.

Example:

```text id="g2w6k4"
POS
✓ Available

Live Reports
! Requires connection

Administration
! Limited while offline
```

Offline availability must follow Backend and Frontend offline architecture.

---

# 66. Navigation and Read-Only

In read-only mode, navigation may remain available for:

* historical data;
* reports;
* permitted exports;
* configuration viewing.

Modification workflows must be blocked or clearly marked.

---

# 67. Error Recovery from Navigation

If a user navigates to an unavailable feature:

```text id="z5m8c2"
This section is currently unavailable.

Reason:
Subscription restriction / Permission / Connection

[Return to Dashboard]
```

The user should not encounter unexplained blank screens.

---

# 68. Application Exit

The application should not provide unnecessary browser-level exit behavior.

If the product is installed as a PWA, application close behavior remains platform-controlled.

The application should focus on safe session and operational state handling.

---

# 69. AI-Agent Navigation Rules

AI agents modifying navigation must:

1. Read this document first.
2. Check existing route conventions.
3. Reuse existing shell components.
4. Reuse existing navigation groups.
5. Avoid creating duplicate navigation systems.
6. Respect Business scope.
7. Respect Branch scope.
8. Respect permissions.
9. Respect subscription state.
10. Respect offline restrictions.
11. Preserve route accessibility.
12. Preserve deep-link behavior.
13. Preserve browser back/forward behavior.
14. Avoid unnecessary global navigation changes.
15. Update route documentation when introducing major routes.

---

# 70. Navigation Invariants

The following rules are mandatory:

1. The Application Shell provides global application structure.
2. Feature business logic remains outside the shell.
3. Business context is always identifiable.
4. Branch context is always identifiable during Branch-scoped operation.
5. Branch switching recalculates relevant context.
6. Unauthorized Branches are not offered for selection.
7. Backend remains authoritative for Branch access.
8. Navigation is permission-aware.
9. Navigation is not a security boundary.
10. Subscription state influences available operations.
11. Read-only mode is visible.
12. POS navigation is optimized for speed.
13. POS does not depend on heavy administrative modules.
14. Route names are predictable.
15. Route parameters do not establish authorization.
16. Authentication guards protect authenticated routes.
17. Permission guards protect obvious unauthorized navigation.
18. Subscription restrictions are reflected in UI.
19. 403 and 404 states are handled appropriately.
20. Active navigation state is visible.
21. Breadcrumbs are used when useful.
22. Navigation supports keyboard access.
23. Navigation supports responsive layouts.
24. Sidebar may collapse on desktop.
25. Mobile navigation must remain accessible.
26. Global status is visible when operationally important.
27. Offline state is visible.
28. Synchronization state is visible when relevant.
29. Conflicts are more prominent than normal synchronization.
30. Notifications are globally accessible.
31. Logout does not automatically close operational sessions.
32. Unsaved changes are protected where necessary.
33. Deep links remain authorization-protected.
34. Browser navigation remains predictable.
35. Route loading does not unnecessarily block the shell.
36. Route failures provide recovery.
37. Permission changes must not remain stale indefinitely.
38. Branch permission changes must not leave stale Branch access.
39. Device identity cannot be spoofed through UI.
40. Layout preferences cannot alter business correctness.
41. Navigation performance targets must be respected.
42. Accessibility is part of navigation architecture.
43. Feature flags remain separate from permission.
44. Permission remains separate from subscription.
45. Offline availability remains explicit.
46. Read-only state does not imply data deletion.
47. Navigation must not expose inaccessible functionality as available.
48. Navigation groups must remain manageable as the system grows.
49. AI agents must reuse existing navigation patterns.
50. Major navigation changes must be documented.

---

# 71. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`

### Backend

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

---

# 72. Status

**Document:** `04_Application_Layout_and_Navigation.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `03_Design_System_and_UI_Principles.md`

**Next Document:** `05_Authentication_and_Session_UI.md`

