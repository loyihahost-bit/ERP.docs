# Reports and Dashboard UI

**Document ID:** FA-16
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

## 1. Purpose

This document defines the Frontend architecture and user interface behavior for Reports and Dashboard functionality in FastFood ERP.

The Frontend must provide a clear, fast and permission-aware interface for viewing:

* Business performance;
* Branch performance;
* sales;
* orders;
* payments;
* cash sessions;
* discrepancies;
* corrections;
* inventory;
* employees;
* attendance;
* payroll;
* operational metrics;
* notifications;
* subscription state.

The Frontend must not become the authoritative source for financial, inventory, payroll or historical calculations.

Backend-generated data remains authoritative.

---

## 2. Scope

This document covers:

* Dashboard UI;
* report navigation;
* report categories;
* Business and Branch report scope;
* date and period selection;
* filters;
* sorting;
* pagination;
* report detail;
* report versioning;
* immutable report versions;
* report generation;
* report loading states;
* report freshness;
* historical report integrity;
* XLSX export;
* export status;
* permissions;
* subscription restrictions;
* offline behavior;
* synchronization;
* audit visibility;
* dashboard widgets;
* charts;
* KPI cards;
* report comparison;
* empty reports;
* error handling;
* performance;
* accessibility;
* responsive behavior;
* testing;
* observability.

---

# 3. Design Principles

Reports and Dashboard UI must follow these principles:

1. Clarity over visual complexity.
2. Backend remains authoritative.
3. Historical reports must remain reproducible.
4. Current configuration must not rewrite historical data.
5. Business and Branch scope must always be explicit.
6. Permission restrictions must be respected.
7. Financial values must not be independently recalculated by the Frontend.
8. Large reports must not block the UI.
9. Export generation must be asynchronous where required.
10. Offline data must be clearly identified as cached or stale.
11. Dashboard is primarily a read-oriented interface.
12. POS and operational workflows have higher performance priority than dashboards.
13. Charts must communicate information rather than decorate the page.
14. Empty data is a valid state.
15. Historical report versions are immutable.
16. UI convenience must never compromise historical integrity.

---

# 4. Report Hierarchy

Reports are organized according to:

```text
Business
   ↓
Report Scope
   ├── Business
   ├── All Authorized Branches
   ├── Selected Branch
   └── Current Branch
        ↓
Report Category
        ↓
Report
        ↓
Report Version
        ↓
Report Data
```

The exact available scopes depend on:

* employee permissions;
* Branch assignment;
* Business role;
* subscription entitlement;
* report type.

---

# 5. Dashboard vs Report

Dashboard and Report are separate concepts.

### Dashboard

Dashboard provides:

* KPIs;
* summaries;
* charts;
* alerts;
* operational indicators;
* quick navigation.

Dashboard data may be eventually consistent where explicitly indicated.

### Report

Report provides:

* defined period;
* defined scope;
* structured data;
* reproducible result;
* report version;
* historical state where applicable.

Reports are intended for operational, financial and analytical review.

---

# 6. Dashboard Scope

Dashboard may operate in:

* Current Branch;
* Selected Branch;
* All Authorized Branches;
* Business scope.

The available scope depends on permissions.

Example:

```text
Owner
 ├── Business Dashboard
 ├── All Branches
 └── Individual Branch

Manager
 └── Authorized Branches

Cashier
 └── Operational Branch Dashboard where permitted
```

The Frontend must not display unauthorized scope options.

---

# 7. Dashboard Date Range

Dashboard may support:

* Today;
* Yesterday;
* This Week;
* Last Week;
* This Month;
* Last Month;
* Custom Period.

The available ranges may depend on the selected widget or report.

Date selection must use Business/Branch timezone rules.

---

# 8. Report Categories

The Frontend should organize reports into logical categories.

### 8.1. Sales

* sales summary;
* sales by Product;
* sales by category;
* sales by Branch;
* sales by period.

### 8.2. Orders

* order count;
* order type;
* order status;
* item status;
* cancelled orders;
* corrected orders.

### 8.3. Payments

* payment summary;
* payment methods;
* refunds;
* payment discrepancies.

### 8.4. Cash

* cash sessions;
* cashier reports;
* cash discrepancies;
* handover;
* corrections.

### 8.5. Inventory

* stock;
* inventory movement;
* purchases;
* exits;
* adjustments;
* discrepancies;
* low stock;
* out of stock.

### 8.6. Employees

* employee activity;
* attendance;
* Branch activity;
* employee performance where permitted.

### 8.7. Payroll

* payroll periods;
* salary calculation;
* bonuses;
* corrections;
* payment status.

### 8.8. Audit

* audit history;
* configuration changes;
* financial corrections;
* security events where permitted.

### 8.9. Operational

* Branch performance;
* equipment availability;
* order processing;
* kitchen-related operational information.

---

# 9. Report Registry

Reports should be represented through a centralized registry.

A report definition may contain:

```text
report_id
title
category
required_permissions
supported_scopes
supported_periods
supports_export
supports_versioning
supports_comparison
data_source
```

The registry controls UI availability.

The registry must not become a replacement for Backend authorization.

Backend remains authoritative.

---

# 10. Report Navigation

Reports should be accessible through predictable navigation.

Example:

```text
Reports
├── Overview
├── Sales
├── Orders
├── Payments
├── Cash
├── Inventory
├── Employees
├── Payroll
├── Audit
└── Operational
```

Unavailable report categories should not be shown when their visibility is permission-controlled.

---

# 11. Report Page Layout

A standard report page should contain:

```text
Page Header
    ↓
Report Title
    ↓
Scope Selector
    ↓
Period Selector
    ↓
Filters
    ↓
Actions / Export
    ↓
Summary
    ↓
Main Report
    ↓
Pagination
    ↓
Report Metadata
```

The exact layout may differ for specialized reports.

---

# 12. Report Scope Selector

Scope selector must clearly display the active scope.

Examples:

```text
Business: Main Restaurant Group
Scope: All Branches
```

or:

```text
Business: Main Restaurant Group
Branch: Chilanzar
```

Changing scope must reload the report.

The previous Branch's data must not remain visible while the new scope is loading.

---

# 13. Branch Filtering

When multiple Branches are authorized, the user may select:

* one Branch;
* multiple Branches;
* all authorized Branches.

The Backend determines whether the requested combination is authorized.

The Frontend must not assume authorization from the selected values.

---

# 14. Period Filtering

Reports may support:

* predefined periods;
* custom start date;
* custom end date.

The Frontend must validate:

* start date;
* end date;
* valid range;
* supported report period.

Business/Branch timezone must be respected.

---

# 15. Filter State

Filter state should be explicit.

Example:

```text
Scope: Branch A
Period: 2026-10-01 → 2026-10-05
Category: Burgers
Payment: Cash
Status: Completed
```

Filter changes should produce a new query state.

The UI must not silently retain incompatible filters after changing report type.

---

# 16. Filter Reset

Every complex report should provide a clear reset mechanism.

Reset should return to the report's default filters.

Resetting filters must not modify saved historical report versions.

---

# 17. Search

Reports that contain large datasets may provide search.

Search may include:

* Product;
* Employee;
* Order number;
* Cash Session;
* Branch;
* transaction reference.

Search must use Backend-supported query behavior.

Frontend-side filtering may be used only for already loaded small datasets.

---

# 18. Sorting

Tables may support sorting by supported fields.

Example:

```text
Date
Amount
Order Count
Product
Employee
Branch
Status
```

Sorting must be explicit.

The Frontend must not assume that arbitrary fields are sortable.

---

# 19. Pagination

Large reports must use pagination.

Preferred method:

**Cursor pagination**

where supported.

Offset pagination may be used where appropriate.

The UI must display:

* current loading state;
* available continuation;
* total count only when provided;
* page/position where applicable.

---

# 20. Report Summary

A report may display summary values above the detailed table.

Example:

```text
Orders       1,245
Sales        84,500,000
Refunds       1,200,000
Net Sales    83,300,000
```

These values must come from authoritative Backend responses.

The Frontend must not independently reconstruct financial totals.

---

# 21. KPI Cards

Dashboard and reports may use KPI cards.

A KPI card may contain:

* title;
* value;
* unit;
* comparison;
* trend;
* timestamp;
* freshness state.

Example:

```text
Today's Sales
84,500,000 UZS
+8.4%
Updated 14:32
```

Comparison values must be explicitly identified as comparison values.

---

# 22. KPI Formatting

Financial values must use centralized formatting.

The Frontend must not independently decide:

* currency;
* decimal precision;
* rounding policy;
* financial calculation rules.

Backend/API contracts and shared formatting rules define authoritative display semantics.

---

# 23. Charts

Charts should be used only when they improve understanding.

Supported visualization types may include:

* line;
* bar;
* stacked bar;
* pie/donut where appropriate;
* area;
* comparison chart.

Charts must not replace precise tabular information when exact values are important.

---

# 24. Chart Accessibility

Every important chart should have:

* textual summary;
* accessible labels;
* table alternative where appropriate;
* meaningful units.

Color must not be the only way to communicate state.

---

# 25. Dashboard Widgets

Dashboard widgets may include:

### Sales

* today's sales;
* sales trend;
* sales by Branch;
* sales by category.

### Orders

* order count;
* order type;
* order status;
* average order value where provided by Backend.

### Cash

* current session;
* cash discrepancy;
* closed sessions.

### Inventory

* low stock;
* out of stock;
* inventory variance.

### Employees

* attendance;
* active employees;
* payroll status.

### Notifications

* critical alerts;
* unresolved issues.

### Subscription

* subscription status;
* expiry date;
* read-only state.

---

# 26. Widget Registry

Each widget should have:

```text
widget_id
title
required_permissions
supported_scopes
data_source
refresh_policy
presentation_type
```

Widget visibility must be evaluated against current:

* Business;
* Branch;
* Employee;
* permissions;
* subscription;
* device state.

---

# 27. Widget Refresh

Widgets may use:

* initial request;
* manual refresh;
* polling;
* server events;
* cached data.

The simplest reliable mechanism should be preferred.

Real-time mechanisms should be introduced only where operational value justifies their complexity.

---

# 28. Dashboard Refresh Priority

Refresh priority:

```text
POS
 ↓
Cash
 ↓
Inventory
 ↓
Orders
 ↓
Dashboard
 ↓
Reports
```

Dashboard refresh must never interfere with critical POS operations.

---

# 29. Widget Loading State

Each widget should have an independent loading state.

The whole dashboard must not become unusable because one widget is loading.

Example:

```text
Sales       Loaded
Orders      Loading
Inventory   Loaded
Payroll     Error
```

---

# 30. Widget Error State

If one widget fails:

* other widgets remain usable;
* the failed widget displays an error state;
* retry is available where appropriate;
* technical details are not exposed to ordinary users.

---

# 31. Widget Empty State

Empty data is not automatically an error.

Example:

```text
No sales recorded for the selected period.
```

The UI should distinguish:

* empty;
* loading;
* error;
* stale;
* unavailable due to permission.

---

# 32. Stale Data

Cached dashboard/report data must display a freshness indicator when required.

Example:

```text
Showing cached data
Last updated: 12:42
```

Stale data must never appear as live data.

---

# 33. Offline Dashboard

Offline dashboard behavior is limited.

The Frontend may show:

* cached KPI data;
* cached reports;
* last successful update time;
* offline indicator.

It must not imply that cached values represent current server state.

---

# 34. Offline Reports

Reports requiring authoritative server data should not be fabricated from incomplete local data.

When unavailable offline:

```text
This report requires an online connection.
```

Cached report versions may remain viewable if locally authorized and available.

---

# 35. Report Versioning

Reports may have immutable versions.

A report version contains conceptually:

```text
report_id
version_id
scope
period
created_at
created_by
creation_reason
data_state
```

The Frontend displays the version metadata supplied by Backend.

---

# 36. Immutable Report Version

An existing report version must be treated as read-only.

The UI must not expose:

* edit;
* overwrite;
* recalculation;
* delete

actions for immutable versions unless the Backend explicitly supports an administrative lifecycle operation.

---

# 37. Report Version History

Where permitted, users may view:

```text
Version 3
Created: 2026-10-05 23:59
Reason: Inventory correction

Version 2
Created: 2026-10-05 18:00
Reason: Daily report generation

Version 1
Created: 2026-10-05 09:00
Reason: Initial report
```

Older versions remain accessible according to permissions and lifecycle policy.

---

# 38. Report Version Comparison

Where supported, users may compare two report versions.

The UI must clearly identify:

```text
Version A
vs
Version B
```

Differences should be provided by Backend or an authoritative report comparison service.

The Frontend must not infer historical corrections by comparing arbitrary current data.

---

# 39. Report Creation

A report may be:

* automatically generated;
* manually generated;
* generated after relevant correction;
* generated by scheduled process.

The UI must display the creation source where relevant.

---

# 40. Automatic Reports

For reports generated automatically:

* generation status should be visible;
* creation time should be displayed;
* failed generation should be distinguishable from empty data;
* the user should not manually duplicate an automatic version unless permitted.

---

# 41. Manual Reports

Manual report generation may be available to authorized employees.

The Frontend must validate the basic request before submission.

Backend remains responsible for final validation.

---

# 42. Report Generation Status

Long-running reports should use asynchronous generation.

Possible states:

```text
REQUESTED
PROCESSING
READY
FAILED
CANCELLED
```

Exact states remain Backend-authoritative.

---

# 43. Report Generation UI

While a report is being generated:

```text
Generating report...
```

The user may navigate away if the operation is asynchronous.

The Frontend should not require the report page to remain open.

---

# 44. Report Failure

If report generation fails:

* show a clear error;
* preserve the user's filter context where safe;
* provide retry where appropriate;
* do not create a fake empty report.

---

# 45. XLSX Export

Reports support XLSX export where permitted.

Export may be:

* immediate for small datasets;
* asynchronous for large datasets.

The UI must not assume export completion immediately.

---

# 46. Export Status

Possible export states:

```text
REQUESTED
PROCESSING
READY
FAILED
EXPIRED
```

The exact Backend status is authoritative.

---

# 47. Export Download

A completed export should provide:

* file name;
* report name;
* version;
* creation time;
* expiry if applicable;
* download action.

The download action must verify current authorization.

---

# 48. Export Security

Export files may contain sensitive information.

The UI must respect:

* permission;
* Business scope;
* Branch scope;
* employee scope;
* subscription state.

A visible export button does not replace Backend authorization.

---

# 49. Export Audit

Export operations should be auditable.

The UI may show:

```text
Export requested
Export ready
Downloaded
```

Detailed audit records remain Backend responsibility.

---

# 50. Large Report Handling

Large reports must not block the main UI thread.

The Frontend should use:

* pagination;
* incremental rendering;
* asynchronous export;
* virtualized tables where required.

Large datasets must not be rendered entirely in memory when unnecessary.

---

# 51. Financial Reports

Financial reports may include:

* sales;
* payments;
* refunds;
* cash;
* discrepancies;
* expenses;
* payroll.

The Frontend must display Backend-provided authoritative values.

---

# 52. Financial Integrity

The Frontend must never use current Product prices to recalculate historical reports.

Historical reports use:

* Order snapshots;
* payment snapshots;
* refund snapshots;
* report versions;
* historical configuration.

---

# 53. Inventory Reports

Inventory reports may include:

* stock;
* purchases;
* exits;
* adjustments;
* FIFO information;
* discrepancies;
* recipe-related movement.

Inventory values must come from authoritative inventory transactions.

---

# 54. Payroll Reports

Payroll reports may include:

* employee;
* Branch;
* period;
* salary;
* bonuses;
* corrections;
* payment status.

Sensitive salary information must respect employee permissions.

---

# 55. Attendance Reports

Attendance reports may include:

* employee;
* Branch;
* date;
* check-in;
* check-out;
* correction;
* attendance status.

Attendance corrections must remain historically traceable.

---

# 56. Cashier Reports

Cashier reports may include:

* Cash Session;
* opening cash;
* sales;
* payments;
* refunds;
* expected cash;
* actual cash;
* discrepancy;
* handover.

The UI must clearly distinguish expected and actual amounts.

---

# 57. Branch Performance

Branch performance reports may include:

* sales;
* orders;
* inventory;
* cash;
* employees;
* payroll;
* operational indicators.

Only authorized Branches may appear.

---

# 58. Employee Performance

Employee reports are permission-controlled.

Sensitive employee information must not be exposed through aggregated reports if the user's permissions do not allow it.

---

# 59. Audit Reports

Audit reports may include:

* actor;
* action;
* entity;
* Branch;
* timestamp;
* result;
* operation UUID.

Audit data remains immutable.

---

# 60. Report Detail

A report detail page should expose:

* report name;
* scope;
* period;
* version;
* creation time;
* source;
* freshness;
* summary;
* detailed data;
* export actions;
* available historical versions.

---

# 61. Report Metadata

Metadata should be visually separated from report data.

Example:

```text
Report
Daily Sales

Scope
Branch A

Period
2026-10-05

Version
4

Created
2026-10-05 23:59

Status
Final
```

---

# 62. Report Status

Report status must be displayed when meaningful.

Possible states:

```text
DRAFT
GENERATING
READY
FINAL
SUPERSEDED
FAILED
```

Exact status values are Backend-authoritative.

---

# 63. Superseded Reports

When a new report version replaces an older version:

* older version remains accessible where permitted;
* older version is clearly marked as superseded;
* the UI must not present it as the current version.

---

# 64. Report Freshness

The UI should display freshness when the data source is eventually consistent.

Example:

```text
Data updated 2 minutes ago.
```

For immutable reports, creation/version timestamp is more important than live refresh time.

---

# 65. Dashboard Auto Refresh

Auto refresh must be configurable where appropriate.

It must:

* stop or reduce activity when the page is inactive;
* avoid excessive requests;
* respect Backend rate limits;
* not interfere with user interaction.

---

# 66. Dashboard Manual Refresh

A manual refresh action should:

* refresh supported widgets;
* preserve current filters;
* prevent duplicate concurrent requests;
* provide immediate local feedback.

---

# 67. Request Deduplication

Repeated dashboard/report requests should be deduplicated when possible.

The Frontend should prevent:

* duplicate clicks;
* duplicate export requests;
* duplicate report generation;
* unnecessary identical API calls.

This is a performance optimization, not the final idempotency mechanism.

---

# 68. Client Cache

Report/dashboard cache may be used for:

* recently viewed reports;
* reference data;
* dashboard widgets;
* filter metadata.

Cache must include scope and version context.

Example:

```text
Business
Branch
Report ID
Filter Hash
Version
```

---

# 69. Cache Authority

Cache is never authoritative.

If cached data conflicts with Backend data:

**Backend data wins.**

---

# 70. Cache Invalidation

Cache should be invalidated or refreshed after relevant authoritative changes.

Important events may include:

* payment;
* refund;
* inventory correction;
* cash correction;
* attendance correction;
* payroll correction;
* configuration change.

---

# 71. Permission-Aware Cache

Cached report data must not be reused across unauthorized contexts.

For example:

```text
Owner Branch A cache
```

must not become visible to:

```text
Manager Branch B
```

---

# 72. Business Isolation

The Frontend must never intentionally reuse report/dashboard data across Business contexts.

Changing Business context must reset or invalidate incompatible cached data.

---

# 73. Branch Isolation

Changing Branch context must invalidate or reload Branch-scoped dashboard/report data.

A previous Branch's data must never remain visible as if it belonged to the new Branch.

---

# 74. Permission Changes

If permissions change during an active session:

* unavailable reports disappear or become inaccessible;
* current report access is revalidated;
* cached sensitive data must not remain accessible through UI navigation.

Backend authorization remains authoritative.

---

# 75. Subscription Read-Only State

When subscription enters read-only mode:

Allowed:

* view dashboard;
* view reports;
* view historical versions;
* export allowed reports.

Blocked:

* configuration modifications;
* other subscription-restricted modifications.

The UI must clearly indicate read-only state.

---

# 76. Subscription Expiry

When subscription expires:

```text
Read-only mode
```

should be visible globally where relevant.

Report viewing should remain available according to subscription policy.

---

# 77. Data Lifecycle

If Business data enters deletion lifecycle:

* report access follows Backend lifecycle state;
* deleted data must not appear in normal UI;
* stale cached data must not resurrect deleted Business information.

---

# 78. Report Permissions

Each report must define required permissions.

Examples:

```text
reports.sales.view
reports.cash.view
reports.inventory.view
reports.payroll.view
reports.audit.view
reports.export
```

Actual permission names remain aligned with the centralized permission model.

---

# 79. Permission-Based Actions

Actions such as:

* Generate;
* Export;
* Compare;
* View historical version;
* View sensitive details

must be permission-aware.

The UI may hide or disable unavailable actions.

Backend remains authoritative.

---

# 80. Sensitive Reports

Sensitive reports may include:

* payroll;
* salary;
* profit;
* cash discrepancy;
* audit;
* security;
* financial corrections.

The UI should minimize exposure.

Examples:

* masked values;
* restricted detail;
* explicit permission indicators;
* limited export.

---

# 81. Report Filters and URL State

Safe report filters may be represented in the URL for deep linking.

However:

* URL values are not authorization;
* sensitive information must not be placed unnecessarily in URLs;
* Backend must validate scope and permission.

---

# 82. Browser Navigation

Reports should support:

* browser back;
* browser forward;
* deep links;
* refresh.

Returning to a report should restore safe filter state where possible.

---

# 83. Unsaved Report State

If the user has selected filters but has not generated a report:

* navigation should not silently discard meaningful work;
* confirmation may be used when appropriate.

No confirmation is needed for trivial navigation.

---

# 84. Report Comparison UI

When comparison is supported:

```text
Current Period
vs
Previous Period
```

or:

```text
Version 4
vs
Version 3
```

The comparison basis must be explicitly shown.

---

# 85. Trend Indicators

Trend indicators may display:

* increase;
* decrease;
* unchanged.

The Frontend must not infer business significance beyond the supplied data.

For example:

```text
+12%
```

must be accompanied by a clear comparison period.

---

# 86. Dashboard Customization

Owner may customize:

* widget visibility;
* widget order;
* default sections;
* preferred Branch;
* preferred date range;
* selected KPIs.

Customization is UI preference/configuration and must follow the Business configuration model where persistent Business-wide settings are involved.

---

# 87. Personal vs Business Dashboard

The system should distinguish:

### Personal preference

Only affects the current employee.

### Business default

Affects configured users according to permission.

The UI must not accidentally overwrite Business defaults when the user changes personal preferences.

---

# 88. Dashboard Layout Persistence

Dashboard layout may be persisted locally for fast restoration.

Server persistence may be used for cross-device preferences where supported.

Layout persistence must not affect financial correctness.

---

# 89. Responsive Dashboard

Desktop dashboard may use:

```text
2–4 column widget layout
```

depending on screen size.

Tablet/mobile may use:

```text
1–2 column layout
```

Widgets must remain readable without horizontal page scrolling.

---

# 90. Responsive Reports

Report tables may require:

* horizontal local scrolling;
* column prioritization;
* responsive detail drawer;
* mobile-specific compact presentation.

Page-level horizontal overflow should be avoided.

---

# 91. POS Hardware

Reports may be viewed on ordinary office/POS computers.

Report UI must not require:

* GPU acceleration;
* powerful dedicated hardware;
* high-memory browser environments.

Charts must remain lightweight.

---

# 92. Loading Strategy

The Frontend should load:

1. report shell;
2. filters;
3. primary summary;
4. detailed data;
5. secondary visualizations.

Non-critical visualizations may load later.

---

# 93. Progressive Rendering

Dashboard and report UI may progressively render independent sections.

Example:

```text
Shell        → Ready
Filters      → Ready
Summary      → Ready
Table        → Loading
Chart        → Loading
```

This improves perceived performance.

---

# 94. Error Recovery

Error recovery should preserve:

* selected scope;
* selected period;
* filters;
* report type.

Retry should avoid unnecessary duplication.

---

# 95. Network Failure

When network fails:

* show offline/network state;
* preserve current UI;
* keep cached safe data where available;
* prevent false success;
* retry only safe operations.

---

# 96. Unknown Result

If report generation/export request result is unknown:

The UI must not automatically create another request without checking operation status.

Example:

```text
Request submitted.
Checking status...
```

The Backend operation UUID should be used where supported.

---

# 97. Duplicate Export Prevention

The UI should disable or debounce export controls during submission.

Backend idempotency remains mandatory.

---

# 98. Background Report Jobs

Large report generation should use background jobs.

The UI interacts with:

```text
Report Request
    ↓
Job Status
    ↓
Ready Report
```

The browser must not maintain an open request for the entire generation process.

---

# 99. Export Job

Export follows:

```text
Report
   ↓
Export Request
   ↓
Background Job
   ↓
File Generation
   ↓
Ready
   ↓
Download
```

File generation is not part of the critical UI rendering path.

---

# 100. Notifications

Users may receive notifications for:

* report ready;
* export ready;
* report generation failed;
* scheduled report created;
* critical report discrepancy.

Notifications should link to the relevant report when authorized.

---

# 101. Notification Deep Link

A notification may contain:

```text
notification_id
report_id
version_id
```

The Frontend must revalidate access before opening the report.

---

# 102. Report Audit

Viewing, generating, exporting or downloading sensitive reports may require audit events according to Backend policy.

The Frontend should not attempt to create authoritative audit records itself.

---

# 103. Dashboard Audit

Ordinary dashboard viewing does not necessarily require a business audit event.

Sensitive actions remain auditable according to Backend policy.

---

# 104. Date and Time

All report timestamps must use centralized formatting.

The Frontend must distinguish:

* Business timezone;
* Branch timezone where applicable;
* UTC technical timestamps.

Users should not see unexplained timezone shifts.

---

# 105. Currency

Currency display must use centralized formatting.

Example:

```text
84 500 000 UZS
```

The exact formatting is controlled by shared Frontend formatting rules and API contract.

---

# 106. Decimal Precision

The Frontend must not arbitrarily round financial or inventory values.

Precision comes from the Backend/API contract.

---

# 107. Historical Values

Historical values must be displayed exactly according to the report version or transaction snapshot.

Current Product:

```text
Price = 35,000
```

must not alter a historical Order:

```text
Historical Price = 30,000
```

---

# 108. Report Reproducibility

A historical report version must be reproducible from its stored authoritative state.

The Frontend must identify the version instead of presenting a recalculated current result as the old report.

---

# 109. Report Metadata Integrity

The Frontend must not modify:

* report version;
* creation timestamp;
* creator;
* scope;
* creation reason;
* historical state.

These are Backend-authoritative.

---

# 110. Empty Report

A valid report with zero records remains a successful result.

Example:

```text
No orders were recorded during the selected period.
```

It must not be displayed as:

```text
Failed to load report.
```

---

# 111. Partial Data

If a report contains partial data due to an explicit Backend state:

```text
Data is partially available.
```

The UI must not silently treat partial data as complete.

---

# 112. Eventual Consistency

If dashboard data is eventually consistent:

The UI may display:

```text
Data may be delayed.
```

This must be distinguishable from a technical error.

---

# 113. Dashboard Data Source

Dashboard widgets may consume:

* dedicated dashboard API;
* report read models;
* aggregated Backend endpoints;
* cached read models.

The Frontend should not reconstruct large dashboard datasets from many unrelated endpoints unless necessary.

---

# 114. API Request Strategy

Report API requests should:

* send only required filters;
* avoid unnecessary repeated parameters;
* use pagination;
* use stable request identifiers where required;
* support cancellation for obsolete read requests.

---

# 115. Request Cancellation

If the user changes filters before a previous request completes:

The Frontend may cancel or ignore the obsolete request.

Only the latest valid request should update the current UI state.

---

# 116. Race Condition Prevention

Example:

```text
Request A → Branch A
Request B → Branch B

B completes first
A completes later
```

The Frontend must not allow Request A to overwrite the newer Branch B state.

---

# 117. State Management

Report state should distinguish:

* scope;
* filters;
* query state;
* report data;
* version;
* loading;
* error;
* freshness;
* export state.

UI state must not be mixed with authoritative financial state.

---

# 118. Server State

Server-provided report data should be managed as server state.

Examples:

* React Query/TanStack Query or equivalent;
* normalized server cache;
* query invalidation.

The exact library remains a project-level implementation decision.

---

# 119. Local UI State

Local state may contain:

* open panels;
* selected chart;
* table density;
* column visibility;
* temporary filters;
* widget layout.

Local UI state must not become business truth.

---

# 120. Report Cache Keys

Cache keys should include relevant dimensions.

Example:

```text
reports
business_id
branch_scope
report_id
period
filters
version
```

The actual implementation may use a serialized stable query key.

---

# 121. Security

Frontend reports must enforce defense-in-depth:

* permission-aware routes;
* permission-aware actions;
* Business context;
* Branch context;
* subscription state;
* safe cache;
* safe export handling;
* no sensitive data in logs.

Backend authorization remains authoritative.

---

# 122. Cross-Business Isolation

The UI must never intentionally display data from another Business.

Changing Business context must:

1. clear incompatible report state;
2. clear incompatible cache;
3. reload authorized report definitions;
4. reload dashboard scope.

---

# 123. Cross-Branch Isolation

Changing Branch must:

1. update Branch context;
2. invalidate incompatible report state;
3. reload Branch-specific widgets;
4. reload filters;
5. prevent stale Branch data from being shown as current.

---

# 124. Employee Deactivation

If the current employee becomes inactive:

* sensitive report actions must stop;
* existing report views may become unauthorized;
* navigation should update;
* Backend authorization remains final.

---

# 125. Accessibility

Reports must support:

* keyboard navigation;
* visible focus;
* semantic tables;
* accessible form labels;
* accessible filter controls;
* screen-reader-compatible status;
* chart alternatives;
* adequate contrast;
* reduced motion.

---

# 126. Keyboard Support

Keyboard users must be able to:

* open reports;
* change filters;
* navigate tables;
* export;
* move between dashboard widgets;
* activate actions.

---

# 127. Table Accessibility

Tables should provide:

* proper headers;
* row/column relationships;
* sortable state;
* pagination state;
* loading state;
* empty state.

---

# 128. Chart Alternative

Every important visual chart should have an equivalent textual or tabular representation when required for accessibility.

---

# 129. Performance Targets

The Frontend should target:

| Operation                               |                         Target |
| --------------------------------------- | -----------------------------: |
| Dashboard first useful KPI              |                     p75 ≤ 1.5s |
| Dashboard shell interactive             |                     p75 ≤ 2.0s |
| Report page interactive                 |                     p75 ≤ 2.0s |
| Cached report navigation                |                    p95 ≤ 300ms |
| Normal report render after API response |                    p95 ≤ 500ms |
| Report filter interaction               |     p95 ≤ 100ms local feedback |
| Dashboard widget render                 |                    p95 ≤ 500ms |
| Report table pagination                 | p95 ≤ 300ms after API response |
| Dashboard manual refresh feedback       |                    p95 ≤ 100ms |
| Export request acknowledgement          |                       p95 ≤ 1s |
| Report generation status update         | ≤ 2s after authoritative event |
| Critical dashboard notification update  |                           ≤ 2s |
| Fatal Reports/Dashboard UI error rate   |                < 0.1% sessions |

These targets are Frontend targets and do not replace Backend/API SLOs.

---

# 130. Performance Optimization

Performance work should prioritize:

1. API efficiency;
2. payload size;
3. pagination;
4. cache;
5. rendering;
6. virtualization;
7. chart optimization.

The Frontend must not solve slow Backend queries through uncontrolled client-side processing.

---

# 131. Large Table Optimization

Large tables may use:

* virtualization;
* pagination;
* incremental rendering;
* column virtualization where necessary.

Virtualization must not break:

* keyboard navigation;
* screen readers;
* row selection;
* accessibility.

---

# 132. Chart Optimization

Charts should:

* avoid unnecessary animation;
* limit expensive redraws;
* use simplified rendering for large datasets;
* respect reduced-motion preference.

---

# 133. Mobile Performance

Mobile dashboard/report pages must avoid:

* loading every widget simultaneously;
* unnecessary high-resolution charts;
* huge table payloads.

Critical content should load first.

---

# 134. Testing Strategy

Reports/Dashboard Frontend must include:

### Unit Tests

* filter transformation;
* formatting;
* query key creation;
* permission visibility;
* state transitions.

### Component Tests

* KPI;
* chart;
* table;
* filter;
* export;
* report version selector.

### Integration Tests

* scope switching;
* Branch switching;
* report loading;
* export flow;
* permission changes;
* subscription read-only.

### End-to-End Tests

* login → dashboard;
* Branch switch → dashboard;
* report filtering;
* report version viewing;
* XLSX export;
* failed report generation;
* offline behavior;
* recovery after reconnect.

---

# 135. Historical Integrity Tests

Tests must verify:

* current price does not rewrite historical report;
* correction creates new report version;
* old report remains unchanged;
* historical export matches the selected version.

---

# 136. Security Tests

Tests must verify:

* unauthorized report inaccessible;
* unauthorized Branch inaccessible;
* cross-Business report access impossible;
* restricted payroll hidden;
* restricted audit report hidden;
* export authorization enforced.

---

# 137. Cache Isolation Tests

Tests must verify:

```text
Business A cache
≠
Business B cache
```

and:

```text
Branch A cache
≠
Branch B cache
```

where data is Branch-scoped.

---

# 138. Race Condition Tests

Test:

```text
Branch A request
Branch B request
```

with completion in reverse order.

Only the current context should update.

---

# 139. Export Tests

Test:

* duplicate click;
* network timeout;
* unknown result;
* retry;
* export ready;
* export failed;
* expired export;
* unauthorized download.

---

# 140. Observability

Frontend should capture:

* report load duration;
* dashboard load duration;
* widget errors;
* export request errors;
* report generation status;
* API latency;
* cache hit/miss where available;
* fatal UI errors.

Logs must not contain sensitive payroll or financial data unnecessarily.

---

# 141. Error Classification

Frontend should distinguish:

```text
Validation Error
Authorization Error
Business Rule Violation
Conflict
Network Error
Timeout
Server Error
Unknown Result
```

User-facing messages should be understandable.

---

# 142. Retry Rules

Automatic retry is appropriate only for safe read operations or explicitly retryable requests.

Report generation/export retries must respect operation idempotency.

---

# 143. Offline Recovery

After reconnection:

1. refresh context;
2. validate permissions;
3. refresh stale dashboard data;
4. refresh report metadata;
5. preserve valid filters;
6. update freshness state.

---

# 144. Synchronization

Dashboard/report synchronization must not be confused with transactional synchronization.

POS/inventory/cash transaction synchronization remains higher priority.

Reports may update after transactional synchronization completes.

---

# 145. Conflict Display

If report data changes because of a correction:

The UI should identify that a newer report version exists.

Example:

```text
A newer report version is available.
View latest version
```

The old version remains immutable.

---

# 146. AI-Agent Development Rules

AI agents modifying Reports/Dashboard Frontend must:

1. read this document first;
2. read Frontend Architecture;
3. read Dashboard Architecture;
4. read Backend report architecture;
5. read report/database contracts;
6. identify affected feature module;
7. avoid changing shared components unnecessarily;
8. preserve Business/Branch isolation;
9. preserve historical integrity;
10. add tests;
11. update related documentation;
12. avoid inventing Backend behavior.

---

# 147. Forbidden Frontend Patterns

The following are prohibited:

* recalculating authoritative financial reports locally;
* trusting URL Branch IDs as authorization;
* displaying stale Branch data as current;
* exposing unauthorized payroll;
* using current prices for historical reports;
* modifying immutable report versions;
* treating empty reports as errors;
* silently replacing one report version with another;
* storing sensitive report data in unrestricted local storage;
* creating duplicate exports through repeated clicks;
* blocking the main UI for large report generation;
* loading unlimited rows into memory;
* using charts without accessible alternatives where required.

---

# 148. Recommended Feature Structure

Recommended initial structure:

```text
frontend/
└── src/
    └── features/
        ├── dashboard/
        │   ├── pages/
        │   ├── components/
        │   ├── widgets/
        │   ├── queries/
        │   ├── filters/
        │   ├── layout/
        │   └── types/
        │
        └── reports/
            ├── pages/
            ├── components/
            ├── queries/
            ├── mutations/
            ├── filters/
            ├── versions/
            ├── exports/
            ├── tables/
            ├── charts/
            └── types/
```

Shared report functionality may additionally exist under:

```text
frontend/
└── src/
    ├── api/
    ├── state/
    ├── synchronization/
    └── shared/
        ├── formatting/
        ├── tables/
        ├── charts/
        ├── filters/
        └── permissions/
```

---

# 149. Dependency Rules

Dashboard and Reports must follow:

```text
Pages
  ↓
Feature Components
  ↓
Queries / Mutations
  ↓
API Contracts
```

Shared UI must not contain Business-specific report logic.

Dashboard widgets should not directly manipulate unrelated feature state.

---

# 150. Dashboard Feature Boundary

Dashboard should primarily coordinate:

* widget layout;
* scope;
* filters;
* presentation;
* refresh.

Business logic remains in the corresponding Backend/domain feature.

---

# 151. Report Feature Boundary

Reports Frontend owns:

* report presentation;
* filters;
* query state;
* pagination;
* version navigation;
* export interaction;
* loading/error states.

Backend owns:

* report calculation;
* aggregation;
* historical truth;
* report version creation;
* financial calculations;
* authorization.

---

# 152. API Contract Discipline

Frontend report code must use explicit API contracts.

Avoid:

```text
any
unknown financial object
dynamic untyped response
```

where a stable contract is possible.

API changes must be coordinated with Backend API documentation.

---

# 153. Version Compatibility

Frontend must remain compatible with supported Backend report API versions.

A report API change must not silently corrupt:

* filters;
* financial values;
* version identity;
* export state.

---

# 154. Feature Flags

Feature flags may control:

* new chart;
* new report;
* new dashboard widget;
* new export flow.

Feature flags must not bypass:

* permissions;
* subscription;
* Business isolation;
* Branch isolation;
* security controls.

---

# 155. Configuration

Dashboard configuration may include:

* default widgets;
* widget order;
* refresh policy;
* default period;
* default scope.

Business-level configuration remains Backend-authoritative.

---

# 156. Report Configuration

Report configuration may define:

* available filters;
* supported periods;
* columns;
* export capability;
* comparison capability.

The Frontend consumes Backend-supported configuration rather than inventing unsupported report behavior.

---

# 157. System Invariants

The following invariants apply to Reports and Dashboard UI:

1. Backend is authoritative for report data.
2. Backend is authoritative for financial calculations.
3. Dashboard is separate from historical report versions.
4. Business scope is always explicit.
5. Branch scope is always explicit where applicable.
6. Unauthorized Branches are never intentionally displayed.
7. Unauthorized Businesses are never displayed.
8. URL parameters never provide authorization.
9. Product current price cannot rewrite historical reports.
10. Historical report versions are immutable.
11. Superseded reports remain distinguishable.
12. Empty report is not a technical error.
13. Loading state is distinct from empty state.
14. Error state is distinct from empty state.
15. Stale state is distinct from live state.
16. Cached report data is non-authoritative.
17. Cache is Business-isolated.
18. Branch-scoped cache is Branch-isolated.
19. Permission changes invalidate incompatible access.
20. Subscription read-only blocks restricted modifications.
21. Read-only users may view permitted reports.
22. Export requires authorization.
23. Export files may contain sensitive information.
24. Sensitive reports require appropriate permission.
25. Payroll reports are permission-controlled.
26. Audit reports are permission-controlled.
27. Financial values are Backend-provided.
28. Frontend does not independently recalculate authoritative financial totals.
29. Historical values are displayed from historical snapshots or report versions.
30. Report version identity is Backend-authoritative.
31. Report creation timestamp is Backend-authoritative.
32. Report creator is Backend-authoritative.
33. Report scope is Backend-authoritative.
34. Report status is Backend-authoritative.
35. Export status is Backend-authoritative.
36. Long-running report generation is asynchronous where required.
37. Long-running export generation is asynchronous where required.
38. Browser navigation must not corrupt report state.
39. Changing Branch invalidates incompatible report state.
40. Changing Business invalidates incompatible report state.
41. Dashboard refresh must not block POS operations.
42. Dashboard polling must be bounded.
43. Duplicate UI requests should be prevented where practical.
44. Backend idempotency remains authoritative.
45. Unknown operation results must be reconciled before retry.
46. Obsolete requests must not overwrite newer context.
47. Report filters must be deterministic.
48. Filter reset does not modify historical reports.
49. Report comparison basis must be explicit.
50. Trend comparisons must identify their comparison period.
51. Charts do not replace required exact values.
52. Important charts have accessible alternatives where required.
53. Color is not the sole state indicator.
54. Tables use semantic structure.
55. Large reports use pagination or equivalent bounded loading.
56. Unlimited dataset rendering is prohibited.
57. Large exports do not block the main UI.
58. Report generation does not require the browser page to remain open.
59. Export download revalidates authorization.
60. Sensitive report data is not unnecessarily logged.
61. Sensitive data is not placed unnecessarily in URLs.
62. Dashboard cache does not become financial authority.
63. Report cache does not become historical authority.
64. Current configuration does not reinterpret historical reports.
65. Report corrections create new versions where required.
66. Older report versions are not silently overwritten.
67. Newer report versions are clearly identifiable.
68. Offline cached reports are clearly marked.
69. Offline cached dashboard values are clearly marked when stale.
70. Offline mode does not fabricate unavailable reports.
71. Reconnection refreshes stale report/dashboard data.
72. Transaction synchronization has priority over report refresh.
73. Report UI respects Business timezone.
74. Report UI respects Branch timezone where applicable.
75. Currency formatting is centralized.
76. Decimal precision is not arbitrarily changed by UI.
77. Payroll data is masked or restricted when required.
78. Permission-aware UI is not a replacement for Backend authorization.
79. Feature flags cannot bypass authorization.
80. Feature flags cannot bypass subscription rules.
81. Business defaults and personal dashboard preferences are distinct.
82. Dashboard layout changes do not modify financial truth.
83. Widget failure does not make the entire dashboard unusable.
84. Widget loading is independent where practical.
85. Widget empty state is explicit.
86. Widget stale state is explicit where relevant.
87. Report filters remain understandable after navigation.
88. Report pages support safe deep linking.
89. Browser back/forward does not bypass authorization.
90. Deactivated employees cannot continue unauthorized report actions.
91. Deleted Businesses cannot be resurrected through cached report data.
92. Export operations are auditable where required.
93. Sensitive report access follows audit policy.
94. Report API contracts are explicit.
95. Frontend does not invent unsupported report states.
96. Backend status remains authoritative.
97. API errors are classified.
98. Retry is limited to safe/retryable operations.
99. Network failure does not create false success.
100. Report generation failure does not become an empty report.
101. Dashboard data freshness is communicated when required.
102. Eventual consistency is not presented as guaranteed real-time data.
103. Report versions remain reconstructable.
104. Historical report integrity has priority over UI convenience.
105. POS performance has priority over dashboard/report refresh.
106. Reports do not require high-end client hardware.
107. Chart rendering remains bounded.
108. Report state is separated from unrelated application state.
109. Shared components do not contain Business-specific report rules.
110. Dashboard widgets do not directly bypass API contracts.
111. Frontend report behavior remains aligned with Backend architecture.
112. Report UI changes must preserve authorization boundaries.
113. Report UI changes must preserve historical integrity.
114. Report UI changes must preserve Business/Branch isolation.
115. Report UI changes must preserve offline/synchronization rules.
116. Export UI changes must preserve file security.
117. Large report rendering must remain responsive.
118. Accessibility is required for core report workflows.
119. Performance regressions must be measurable.
120. Report/dashboard behavior must remain testable.
121. AI-agent changes must follow documentation-first workflow.
122. AI agents must not invent report business rules.
123. AI agents must not move financial authority into Frontend.
124. AI agents must not bypass Backend validation.
125. AI agents must preserve immutable history.
126. AI agents must preserve Business isolation.
127. AI agents must preserve Branch isolation.
128. AI agents must preserve permission boundaries.
129. AI agents must preserve subscription boundaries.
130. AI agents must update tests when report behavior changes.
131. AI agents must update documentation when architecture changes.
132. Report/dashboard UI must remain simple despite internal complexity.
133. Operationally critical information must remain easy to find.
134. Financial information must remain precise.
135. Historical information must remain trustworthy.
136. Report export must remain controlled.
137. Dashboard customization must not affect authoritative data.
138. Report comparison must remain explicit.
139. Stale data must never masquerade as current authoritative data.
140. Report and Dashboard Frontend must prioritize correctness, clarity and operational usability.

---

# 158. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/15_Attendance_and_Payroll_UI.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/29_Database_Security.md`

### System Analysis

* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`

---

# 159. Status

**Document Status:** Proposed

**Version:** 1.0

**Document:** `16_Reports_and_Dashboard_UI.md`

**Previous Document:** `15_Attendance_and_Payroll_UI.md`

**Next Document:** `17_Notifications_and_Alerts_UI.md`

