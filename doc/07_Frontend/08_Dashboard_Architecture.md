# Dashboard Architecture

**Document ID:** FA-08
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `07_Business_and_Branch_Context.md`
**Next Document:** `09_POS_Frontend_Architecture.md`

---

# 1. Purpose

This document defines the Frontend architecture and behavior of the FastFood ERP Dashboard.

The Dashboard provides users with a fast overview of the operational state relevant to their:

* Business;
* Branch;
* role;
* permissions;
* subscription;
* employee scope.

The Dashboard must prioritize useful information over visual complexity.

The primary principle is:

> Dashboard is an operational overview, not a replacement for detailed business modules.

---

# 2. Dashboard Goals

The Dashboard should allow an authorized user to quickly understand:

* current sales;
* order activity;
* cash status;
* inventory status;
* Branch performance;
* employee-related alerts;
* important operational warnings;
* subscription state;
* pending actions.

The exact information depends on the user's role and permissions.

---

# 3. Dashboard Context

Dashboard data must always have an explicit scope.

Possible scopes:

```text id="dsh482"
Current Branch
All Authorized Branches
Business
Selected Period
```

Example:

```text
Business: FastFood Demo
Branch: Chilanzar
Date: 06 October 2026
```

The Dashboard must never combine incompatible Branch contexts.

---

# 4. Dashboard Types

The system may provide several logical Dashboard views:

```text id="dsb719"
1. Business Dashboard
2. Branch Dashboard
3. Operational Dashboard
4. Financial Dashboard
5. Inventory Dashboard
6. Employee Dashboard
```

These are logical views and do not necessarily require separate frontend applications.

---

# 5. Default Dashboard

The default Dashboard depends on the user's effective access.

Examples:

```text id="dsh103"
Owner / authorized Manager
→ Business or Branch Dashboard

Cashier
→ POS-oriented operational dashboard or POS

Inventory employee
→ Inventory-oriented dashboard

Other employee
→ First relevant authorized operational area
```

The exact default route is configurable.

---

# 6. Dashboard Personalization

The Owner may customize Dashboard layout.

Customization may include:

* widget visibility;
* widget order;
* default sections;
* selected KPI cards;
* preferred Branch scope;
* preferred date range where supported.

Customization must not change authorization.

---

# 7. Default Widget Configuration

The system may define default widgets.

Example:

```text id="wgt318"
Sales Today
Orders Today
Cash Status
Low Stock
Out of Stock
Pending Corrections
Branch Performance
Recent Alerts
```

The actual default set may differ by role.

---

# 8. Widget Architecture

A Dashboard widget should be treated as a reusable frontend component.

Conceptually:

```text id="wgt742"
Widget Definition
├── widget_id
├── title
├── description
├── required_permissions
├── supported_scopes
├── supported_roles
├── data_source
├── refresh_policy
└── presentation
```

The Backend remains authoritative for the data.

---

# 9. Widget Categories

Recommended widget categories:

```text id="wgt905"
Sales
Orders
Cash
Inventory
Employees
Payroll
Reports
Notifications
Subscription
Operations
```

---

# 10. Widget Permission Model

A widget may require specific permissions.

Example:

```text id="wgt611"
Inventory Low Stock
Required:
inventory.view
```

If the user lacks the required permission, the widget should not expose protected data.

---

# 11. Widget Visibility

The Frontend may decide widget visibility based on:

* authentication;
* Business context;
* Branch context;
* effective permissions;
* subscription entitlement;
* widget configuration.

The Backend remains authoritative for protected data.

---

# 12. Widget Subscription Rules

If a widget depends on a subscription feature:

```text id="wgt827"
Permission:
reports.view = Yes

Subscription:
Advanced Dashboard = Disabled
```

The widget may be:

* hidden;
* disabled;
* shown with limited information;

according to product policy.

---

# 13. Dashboard Read-Only Mode

When the Business subscription is READ_ONLY:

The Dashboard may remain available for viewing.

Modification controls should be unavailable.

Example:

```text id="dsh510"
Read-only mode

Business data can be viewed and exported,
but modifying operations are unavailable.
```

---

# 14. Dashboard Scope Selector

Where authorized, the Dashboard may allow:

```text id="dsh624"
Scope
[ Current Branch ▼ ]
```

Options may include:

* Current Branch;
* All authorized Branches;
* selected Branches.

Unauthorized Branches must never appear.

---

# 15. Date Range

Dashboard widgets may support date filters.

Recommended options:

```text id="dsh731"
Today
Yesterday
This Week
This Month
Custom Range
```

Custom ranges must respect Backend query limits.

---

# 16. Default Date

The default operational Dashboard should normally use the current Business/Branch date.

The UI must not blindly use the browser's local calendar date when it differs from the Business/Branch timezone.

---

# 17. Business Timezone

Dashboard dates and times must use the configured Business/Branch timezone where applicable.

Example:

```text id="dsh846"
Business timezone:
Asia/Tashkent

Dashboard date:
06 October 2026
```

---

# 18. KPI Cards

KPI cards should communicate one important metric each.

Example:

```text id="kpi214"
Sales Today
1,240,000 UZS

Orders
84

Average Order
14,762 UZS
```

The exact financial values come from authoritative Backend/report data.

---

# 19. KPI Design

KPI cards should contain:

* title;
* current value;
* relevant unit;
* optional comparison;
* optional status;
* optional timestamp.

Avoid unnecessary decorative information.

---

# 20. KPI Comparison

A KPI may include a comparison:

```text id="kpi532"
Sales Today
1,240,000 UZS

vs yesterday
+8.4%
```

The comparison must clearly identify:

* comparison period;
* calculation basis;
* whether the value is exact or estimated.

---

# 21. Financial Data Integrity

Dashboard financial figures must not be independently recalculated in the Frontend when authoritative Backend/report values are available.

The Frontend should consume:

* report snapshots;
* authoritative aggregates;
* financial API responses.

It must not reinterpret historical financial transactions.

---

# 22. Sales Widget

A Sales widget may display:

* sales total;
* order count;
* average order value;
* comparison period;
* payment distribution where authorized.

Example:

```text id="dsh214"
Sales Today
1,240,000 UZS

Orders
84

Average Order
14,762 UZS
```

---

# 23. Orders Widget

The Orders widget may show:

```text id="dsh327"
New       8
Preparing 12
Ready     5
Completed 54
Cancelled 5
```

Statuses should follow the Business's configured Order lifecycle.

The Frontend must not hard-code unsupported statuses.

---

# 24. Order Status Visibility

Users may have different visibility permissions.

Example:

```text id="dsh438"
Cashier:
Orders visible

Cook:
Kitchen-relevant statuses

Owner:
Full permitted status overview
```

The Dashboard must respect permission-based visibility.

---

# 25. Cash Widget

Authorized users may see:

* active Cash Session;
* expected cash;
* current session status;
* discrepancy warnings;
* cashier;
* register.

Sensitive cash data must remain permission-controlled.

---

# 26. Cash Session Status

Example:

```text id="dsh551"
Cash Session
Open

Cashier:
Ali

Register:
Register 1

Status:
Active
```

The Dashboard must not assume that a Cash Session exists.

---

# 27. Cash Discrepancy Alert

If the Backend reports a discrepancy:

```text id="dsh673"
Cash discrepancy

Expected:
1,200,000 UZS

Actual:
1,190,000 UZS

Difference:
-10,000 UZS
```

The Frontend displays authoritative values.

---

# 28. Inventory Widget

Inventory widgets may show:

```text id="dsh784"
Low Stock
12 items

Out of Stock
4 items

Inventory Variance
2 pending
```

Inventory data must respect Branch scope.

---

# 29. Inventory Availability

A product may be:

* menu-active but out of stock;
* menu-inactive with stock;
* temporarily unavailable;
* operationally unavailable due to equipment.

Dashboard indicators should not collapse these states into a single misleading "inactive" status.

---

# 30. Low Stock Threshold

The Dashboard should use Backend-defined inventory thresholds.

The Frontend must not independently determine the authoritative low-stock state.

---

# 31. Employee Widget

Where authorized, the Dashboard may display:

* employee count;
* attendance;
* active shifts;
* pending payroll;
* employee alerts.

Sensitive employee information must remain permission-controlled.

---

# 32. Payroll Widget

Authorized users may see:

```text id="dsh895"
Payroll Due
2,400,000 UZS

Employees Pending
6
```

Payroll values must come from authoritative Backend calculations.

---

# 33. Attendance Widget

Attendance may show:

```text id="dsh906"
Present
18

Absent
3

Late
2
```

The exact metrics depend on the Attendance system.

---

# 34. Branch Performance Widget

Business-level users may compare Branch performance.

Example:

```text id="dsh102"
Branch       Sales
Chilanzar    12.4M
Yunusabad    10.8M
Sergeli       8.9M
```

Only authorized Branches may appear.

---

# 35. Cross-Branch Comparison

Cross-Branch widgets must clearly identify:

* Branch;
* period;
* metric;
* scope.

The UI must not imply that a Branch comparison includes unauthorized Branches.

---

# 36. Notifications Widget

Dashboard may include recent important notifications.

Example:

```text id="dsh248"
Important

Low stock: Chicken
Branch: Chilanzar

Cash discrepancy
Branch: Yunusabad
```

Notifications must respect scope and recipient authorization.

---

# 37. Subscription Widget

Owner-level users may see subscription information:

```text id="dsh369"
Subscription

Plan:
Professional

Status:
Active

Expires:
30 November 2026
```

The exact data is authoritative from the subscription system.

---

# 38. Subscription Warning

When expiration is approaching:

```text id="dsh470"
Subscription expires soon.

Some modifying functions may become unavailable after expiration.
```

The exact warning threshold follows Business/Subscription configuration.

---

# 39. Read-Only Subscription Widget

If the Business is READ_ONLY:

```text id="dsh581"
Subscription expired

Business is currently in read-only mode.

View and export remain available.
```

The Dashboard must not provide misleading active-operation controls.

---

# 40. Alert Priority

Dashboard alerts should use severity:

```text id="dsh692"
INFO
WARNING
IMPORTANT
CRITICAL
```

The visual treatment must follow the Design System.

---

# 41. Alert Examples

Examples:

```text id="dsh703"
WARNING
Low stock

IMPORTANT
Large refund

CRITICAL
Security alert

WARNING
Subscription expires soon
```

Color must not be the only indicator.

---

# 42. Alert Deduplication

The Frontend should avoid displaying duplicate identical alerts when the Backend provides stable notification identity.

The notification system remains authoritative.

---

# 43. Real-Time Updates

Dashboard data may be updated through:

* polling;
* server-sent events;
* WebSocket;
* event-driven refresh;
* manual refresh.

The initial architecture should prefer the simplest reliable mechanism.

Real-time behavior should be introduced only where it materially improves operations.

---

# 44. POS-Critical vs Dashboard Updates

POS operations have higher priority than Dashboard refresh.

A Dashboard refresh must not block:

* Order creation;
* payment;
* Cash Session;
* inventory transaction;
* synchronization.

---

# 45. Refresh Policy

Each widget may have a refresh policy.

Example:

```text id="dsh814"
Cash Session
→ frequent

Orders
→ frequent

Sales KPI
→ moderate

Monthly report
→ on demand

Historical report
→ manual refresh
```

The Frontend should avoid refreshing all widgets simultaneously.

---

# 46. Manual Refresh

A Dashboard may provide:

```text id="dsh925"
[Refresh]
```

The refresh should:

* preserve current scope;
* preserve date filters;
* preserve widget layout;
* show loading state;
* avoid duplicate requests.

---

# 47. Partial Refresh

A widget should be refreshable independently where practical.

If the Inventory widget fails:

```text id="dsh036"
Inventory

Unable to load current inventory.

[Retry]
```

Other widgets should remain usable.

---

# 48. Dashboard Loading State

Initial Dashboard loading may use skeletons.

Example:

```text id="dsh147"
Sales      ███████
Orders     ███████
Inventory  ███████
```

Skeletons should approximate final layout.

---

# 49. Widget Loading State

A single widget should not block the entire Dashboard.

Each widget should have an independent loading state where practical.

---

# 50. Empty State

If there is no data:

```text id="dsh258"
No sales data for this period.
```

Empty data must not be treated as an error.

---

# 51. Error State

If a widget fails:

```text id="dsh369"
Unable to load Sales.

[Retry]
```

The Dashboard should remain functional.

---

# 52. Stale Data

If cached data is shown:

```text id="dsh470"
Last updated:
14:32
```

Where useful, the UI should indicate that the displayed data is not necessarily real-time.

---

# 53. Offline Dashboard

Offline Dashboard behavior should distinguish:

```text id="dsh581"
Available Offline
Not Available Offline
Cached
Stale
```

The Frontend must not present cached information as authoritative real-time data.

---

# 54. Offline KPI

Only metrics safely available from local authorized state should be displayed offline.

Example:

```text id="dsh692"
Today's locally recorded Orders
42

Status:
Offline
```

The exact availability depends on local data.

---

# 55. Offline Dashboard Warning

Example:

```text id="dsh703"
Offline mode

Some dashboard information may be delayed until synchronization completes.
```

This should be concise and non-disruptive.

---

# 56. Synchronization Indicator

The Dashboard may show:

```text id="dsh814"
Synced
3 pending
Syncing…
Conflict
```

The synchronization indicator must follow the central synchronization state.

---

# 57. Dashboard Customization

Authorized users may customize widgets.

Possible operations:

```text id="dsh925"
Add Widget
Remove Widget
Move Widget
Reset Layout
```

The exact controls depend on user role and Business configuration.

---

# 58. Widget Availability

The Add Widget dialog should show only widgets the user is allowed to use.

Example:

```text id="dsh036"
Available Widgets

✓ Sales
✓ Orders
✓ Inventory
✗ Payroll
```

Payroll may be unavailable because of permission.

---

# 59. Widget Removal

Removing a widget changes the user's presentation preference.

It does not remove the underlying Business data or feature.

---

# 60. Widget Reset

A Reset action may restore the default Dashboard:

```text id="dsh147"
Restore default Dashboard?

Your personal Dashboard layout will be reset.
```

This should not modify Business-level configuration unless explicitly designed to do so.

---

# 61. Owner Default Configuration

The Owner may configure default Dashboard widgets for Business users where permitted.

This differs from an individual employee's personal layout.

The system should distinguish:

```text id="dsh258"
Business Default
        ↓
Employee Personal Preference
        ↓
Effective Layout
```

---

# 62. Layout Priority

Recommended priority:

```text id="dsh369"
System Default
      ↓
Business Default
      ↓
Employee Personal Layout
```

The exact rule should be centralized.

---

# 63. Widget Order

Widgets may be reordered using:

* drag and drop;
* keyboard controls;
* move up/down buttons.

Drag-and-drop must not be the only available method.

---

# 64. Responsive Dashboard

Desktop:

```text id="dsh470"
┌────────┬────────┬────────┐
│ KPI    │ KPI    │ KPI    │
├────────┴────────┼────────┤
│ Sales Chart     │ Alerts │
├─────────────────┴────────┤
│ Inventory / Operations   │
└──────────────────────────┘
```

Mobile:

```text id="dsh581"
KPI
KPI
KPI
Sales
Alerts
Inventory
Operations
```

The layout should reflow rather than force desktop-width content.

---

# 65. POS Hardware

Dashboard UI should remain usable on ordinary office/POS hardware.

Avoid:

* unnecessary animations;
* large background effects;
* excessive chart rendering;
* continuous expensive polling.

---

# 66. Charts

Charts should be used only when they improve understanding.

Suitable examples:

* sales trend;
* order volume;
* Branch comparison;
* inventory movement.

Avoid decorative charts that communicate no operational value.

---

# 67. Chart Data Integrity

Charts must use authoritative API/report data.

The Frontend must not silently interpolate or invent missing financial values.

If values are estimated:

```text id="dsh692"
Estimated
```

must be explicitly indicated.

---

# 68. Dashboard Filters

Filters should be centralized where multiple widgets share them.

Example:

```text id="dsh703"
Branch: Chilanzar
Period: This Month
```

All compatible widgets should react consistently.

---

# 69. Filter Scope

Not every widget must support every filter.

Unsupported combinations should be prevented.

Example:

```text id="dsh814"
Payroll
Branch filter: Supported

Subscription
Branch filter: Not applicable
```

---

# 70. Filter Persistence

The Frontend may persist dashboard filter preferences locally.

However:

* preferences are not authoritative;
* Business/Branch authorization is revalidated;
* invalid persisted filters are discarded.

---

# 71. Dashboard Deep Links

A widget may link to a detailed module.

Example:

```text id="dsh925"
Low Stock: 12
[View Inventory]
```

The destination must preserve valid Business/Branch context.

---

# 72. Dashboard Action Boundaries

Dashboard actions should normally navigate to the authoritative feature module.

For example:

```text id="dsh036"
Cash discrepancy
[View Cash Session]
```

The Dashboard should not duplicate complex Cash correction logic.

---

# 73. Dashboard and Audit

Viewing a Dashboard normally does not require business audit events for every widget render.

Security-sensitive or export operations remain auditable according to Backend policy.

---

# 74. Dashboard and Reports

Dashboard KPI values and Reports must have a defined relationship.

Where possible:

```text id="dsh147"
Dashboard KPI
     ↓
Report / aggregate
     ↓
Authoritative data
```

The Dashboard must not create an independent financial truth.

---

# 75. Report Version Awareness

When a Dashboard uses a versioned report:

* the report version identity may be retained;
* historical values must remain stable;
* corrections may produce a new report version.

The UI must not overwrite historical report values with current values.

---

# 76. Performance Strategy

Dashboard performance should use:

* lazy widget loading;
* bounded requests;
* shared query results where appropriate;
* cached reference data;
* independent widget refresh;
* pagination for large lists;
* deferred non-critical widgets.

---

# 77. Dashboard SLOs

Target frontend SLOs:

| Metric                              |                         Target |
| ----------------------------------- | -----------------------------: |
| Dashboard shell interactive         |                     p75 ≤2.0 s |
| First useful KPI display            |                     p75 ≤1.5 s |
| Cached Dashboard navigation         |                    p95 ≤300 ms |
| Normal widget render after response |                    p95 ≤500 ms |
| Dashboard filter response           |     p95 ≤500 ms after response |
| Widget refresh interaction          |                    p95 ≤100 ms |
| Critical alert UI update            | ≤2 s after authoritative event |
| Fatal Dashboard error rate          |                 <0.1% sessions |

These targets assume normal hardware and network conditions.

---

# 78. Dashboard API Strategy

The Frontend should avoid making dozens of independent API requests when a consolidated Dashboard endpoint or efficient aggregate queries are available.

However, one giant Dashboard API response should not become a bottleneck.

A balanced strategy is:

```text id="dsh258"
Dashboard Shell
      ↓
Critical Summary API
      ↓
Independent Widget/Feature Queries
      ↓
Deferred Secondary Widgets
```

---

# 79. Request Prioritization

Recommended:

```text id="dsh369"
Priority 1
Authentication / Context

Priority 2
Critical KPI / Operational State

Priority 3
Alerts / Orders / Cash

Priority 4
Charts / Analytics

Priority 5
Secondary / Historical Widgets
```

---

# 80. Dashboard Cache

Dashboard cache may be used for:

* reference data;
* configuration;
* non-sensitive aggregate results where appropriate;
* expensive read-only queries.

Cache must not replace authoritative Backend state.

---

# 81. Business/Branch Cache Isolation

Cache keys must include relevant scope.

Example:

```text id="dsh470"
dashboard:
business:{business_id}:
branch:{branch_id}:
period:{period}:
widget:{widget_id}
```

Exact key structure is implementation-defined.

Cross-Business or cross-Branch cache leakage is prohibited.

---

# 82. Cache Invalidation

Dashboard caches should be invalidated or refreshed after relevant changes.

Examples:

* Order accepted;
* Payment completed;
* Cash Session changed;
* Inventory adjusted;
* Employee attendance changed;
* configuration changed.

Not every event requires synchronous Dashboard recalculation.

---

# 83. Eventual Consistency

Dashboard analytics may be eventually consistent when explicitly designed that way.

The UI should not imply transactional immediacy for delayed aggregates.

Example:

```text id="dsh581"
Sales analytics updated 30 seconds ago.
```

Operational transaction screens remain authoritative.

---

# 84. Dashboard Security

The Dashboard must protect:

* financial data;
* payroll data;
* employee information;
* inventory information;
* Branch performance;
* audit/security information.

Permission checks must exist at both:

* widget visibility;
* Backend data access.

---

# 85. Screenshot / Privacy Consideration

Sensitive Dashboard information should not be unnecessarily exposed through:

* browser titles;
* URLs;
* logs;
* analytics;
* debug output.

---

# 86. Accessibility

Dashboard must support:

* keyboard navigation;
* semantic headings;
* accessible KPI labels;
* screen-reader-friendly chart summaries;
* non-color status indicators;
* visible focus;
* reduced motion.

Charts should provide textual summaries where required.

---

# 87. Reduced Motion

Dashboard animations must respect:

```text id="dsh692"
prefers-reduced-motion
```

No critical information should depend on animation.

---

# 88. Error Recovery

Dashboard recovery should be local where possible.

If one widget fails:

```text id="dsh703"
Sales
Unable to load.

[Retry]
```

The rest of the Dashboard remains operational.

---

# 89. Dashboard Initialization Failure

If the entire Dashboard cannot initialize:

```text id="dsh814"
Dashboard unavailable.

Your account is still signed in.

[Retry]
[Go to another available module]
```

The user should retain access to other authorized features where possible.

---

# 90. Permission Changes

If a user's permissions change while the Dashboard is open:

* affected widgets are removed or restricted;
* protected data is no longer requested;
* navigation is recalculated;
* Backend 403 responses are handled centrally.

---

# 91. Branch Change

When Branch changes:

```text id="dsh925"
Switching Branch
      ↓
Clear Branch-scoped widgets
      ↓
Load new Branch data
      ↓
Recalculate permissions
      ↓
Render Dashboard
```

Branch A data must never remain visible under Branch B context.

---

# 92. Business Change

When Business changes:

```text id="dsh036"
Switch Business
      ↓
Clear Business-scoped widgets
      ↓
Load Business
      ↓
Load Branches
      ↓
Load Permissions
      ↓
Load Dashboard
```

---

# 93. Dashboard and Offline State

The Dashboard should clearly indicate:

```text id="dsh147"
Online
Offline
Syncing
Pending
Conflict
```

The status must be consistent with the centralized synchronization state.

---

# 94. Dashboard and Device State

If the trusted device becomes revoked:

The Dashboard must transition according to authentication/device policy.

It must not continue presenting the application as fully operational merely because the page is already open.

---

# 95. Dashboard and Subscription Expiry

When subscription expires:

```text id="dsh258"
Subscription expired

Dashboard remains available in read-only mode.
```

Modification widgets/actions must respect entitlement state.

---

# 96. Widget Lifecycle

A widget may have:

```text id="dsh369"
Available
Loading
Ready
Stale
Empty
Error
Unavailable
```

The UI must distinguish these states.

---

# 97. Widget Registry

A centralized registry is recommended.

Conceptually:

```text id="dsh470"
Widget Registry
├── widget definition
├── permission requirements
├── entitlement requirements
├── supported scopes
├── component
├── data loader
├── refresh policy
└── layout metadata
```

This avoids scattered Dashboard permission logic.

---

# 98. Feature Module Ownership

Dashboard widgets should not duplicate business logic from feature modules.

Example:

```text id="dsh581"
Inventory Widget
    ↓
Inventory Query/Read Model
    ↓
Inventory Domain/Application Logic
```

The widget is a presentation/read layer.

---

# 99. State Management

Dashboard state should be separated into:

```text id="dsh692"
Context State
Filter State
Layout State
Widget Data State
Loading State
Error State
Refresh State
```

Global session state should not contain every widget's data.

---

# 100. Testing

Dashboard testing should cover:

### Functional

* widget visibility;
* permissions;
* Branch scope;
* Business scope;
* filters;
* layout customization;
* navigation;
* refresh.

### Security

* unauthorized widget access;
* cross-Business leakage;
* cross-Branch leakage;
* subscription restrictions;
* employee deactivation.

### Offline

* cached Dashboard;
* stale data;
* offline indicator;
* reconnect;
* synchronization.

### Performance

* initial render;
* widget rendering;
* filter changes;
* Branch switching;
* Business switching;
* large Branch lists.

---

# 101. AI-Agent Dashboard Rules

AI agents modifying Dashboard code must:

1. Read Dashboard architecture before changes.
2. Read Business/Branch context rules.
3. Read permission architecture.
4. Read subscription behavior.
5. Reuse centralized context state.
6. Avoid duplicating business calculations.
7. Avoid creating independent authorization logic.
8. Preserve Business isolation.
9. Preserve Branch isolation.
10. Preserve financial historical integrity.
11. Preserve report version semantics.
12. Preserve offline behavior.
13. Preserve synchronization state.
14. Preserve widget loading/error/empty states.
15. Preserve responsive behavior.
16. Preserve accessibility.
17. Preserve performance SLOs.
18. Avoid unnecessary polling.
19. Avoid blocking POS operations.
20. Document new widgets and their permissions.

---

# 102. Dashboard Invariants

The following invariants are mandatory:

1. Dashboard always operates within a valid Business context.
2. Branch-specific Dashboard data always has a valid Branch context.
3. Backend data is authoritative.
4. Frontend widget visibility is not a security boundary.
5. Protected widget data requires Backend authorization.
6. Business-scoped data cannot leak across Businesses.
7. Branch-scoped data cannot leak across Branches.
8. Unauthorized Branches cannot appear in Branch selectors.
9. Dashboard scope is always identifiable.
10. Business-wide views explicitly indicate their wider scope.
11. Branch-specific views identify the Branch.
12. Dashboard respects employee status.
13. Dashboard respects permissions.
14. Dashboard respects subscription entitlement.
15. READ_ONLY Businesses remain viewable where allowed.
16. READ_ONLY state blocks modifying operations.
17. Dashboard does not rewrite historical financial data.
18. Dashboard does not independently redefine financial truth.
19. Historical report versions remain immutable.
20. Dashboard aggregates use authoritative data sources.
21. Widget permissions are centrally defined.
22. Widget configuration does not grant permissions.
23. Widget visibility cannot bypass Backend authorization.
24. Widget loading is independent where practical.
25. One widget failure does not necessarily fail the Dashboard.
26. Empty data is distinct from an error.
27. Stale data is distinguishable where important.
28. Cached data is not treated as authoritative real-time data.
29. Cache keys preserve Business/Branch isolation.
30. Dashboard refresh must not duplicate operations.
31. Manual refresh preserves scope and filters.
32. Automatic refresh is bounded.
33. POS operations have higher priority than Dashboard refresh.
34. Dashboard must not block payment.
35. Dashboard must not block Cash Session operations.
36. Dashboard must not block inventory transactions.
37. Dashboard must not block synchronization.
38. Date calculations respect Business/Branch timezone.
39. Dashboard filters respect authorization scope.
40. Unsupported filter combinations are prevented.
41. Widget links preserve valid context.
42. Branch switching clears Branch-scoped widget state.
43. Business switching clears Business-scoped widget state.
44. Stale Branch data must not appear under another Branch.
45. Stale Business data must not appear under another Business.
46. Permission changes update Dashboard state.
47. Subscription changes update Dashboard state.
48. Device revocation affects Dashboard availability.
49. Offline Dashboard explicitly indicates offline state.
50. Offline data is not presented as guaranteed current.
51. Offline Dashboard uses only valid local authorized state.
52. Offline authorization cannot be extended by the Dashboard.
53. Synchronization state is centralized.
54. Transaction synchronization has priority over configuration synchronization.
55. Dashboard layout customization does not alter business data.
56. Personal layout is separate from Business default layout.
57. Business default layout is separate from personal preference.
58. Widget removal does not remove the underlying feature.
59. Widget reset does not delete Business configuration.
60. Drag-and-drop is not the only layout-control mechanism.
61. Sensitive KPI data remains permission-controlled.
62. Payroll data remains restricted.
63. Cash data remains restricted.
64. Audit/security information remains restricted.
65. Dashboard URLs do not grant authorization.
66. Dashboard deep links validate context.
67. Browser navigation cannot bypass access control.
68. Authentication state is established before Dashboard data loading.
69. Business context is established before Business Dashboard data loading.
70. Branch context is established before Branch Dashboard data loading.
71. Permission state is established before protected widgets render.
72. Dashboard initialization failures are recoverable where possible.
73. Widget failures are locally recoverable where possible.
74. Authentication failure does not silently become authorized offline mode.
75. Device trust requirements cannot be bypassed.
76. Dashboard does not create authoritative audit records for ordinary widget rendering.
77. Security-sensitive operations remain auditable.
78. Charts must not invent missing data.
79. Estimates must be explicitly identified.
80. Dashboard charts remain accessible.
81. Color is not the only status indicator.
82. Reduced motion is respected.
83. Keyboard navigation is supported.
84. Screen readers can understand KPI and status information.
85. Dashboard remains usable on ordinary POS/office hardware.
86. Dashboard avoids unnecessary heavy rendering.
87. Dashboard uses bounded network activity.
88. Dashboard state is separated from global session state.
89. Feature modules remain owners of their business logic.
90. Dashboard components remain presentation/read-oriented.
91. Context switching remains explicit.
92. Dashboard remains responsive during context switching.
93. Dashboard must not silently fall back to another Branch.
94. Dashboard must not silently substitute another Business.
95. Dashboard state remains reconstructable from authoritative context and data.
96. Dashboard changes must preserve historical integrity.
97. Dashboard changes must preserve security boundaries.
98. Dashboard changes must preserve offline continuity.
99. Dashboard changes must preserve subscription enforcement.
100. Dashboard architecture must remain scalable without requiring unnecessary infrastructure.

---

# 103. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_Caching_and_Performance.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`

---

# 104. Status

**Document:** `08_Dashboard_Architecture.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `07_Business_and_Branch_Context.md`

**Next Document:** `09_POS_Frontend_Architecture.md`

