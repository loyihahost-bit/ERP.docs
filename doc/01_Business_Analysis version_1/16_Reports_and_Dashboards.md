# Reports and Dashboards

**Document ID:** FF-BA-016
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for dashboards, reports, report generation, report versions, Excel exports, report history, and report-related notifications.

The reporting system must provide business owners and authorized employees with reliable historical and operational information without changing the underlying transactional data.

Reports must remain consistent with:

* orders;
* payments;
* cash sessions;
* inventory;
* employees;
* payroll;
* branches;
* corrections;
* audit history.

---

## 2. Reporting Principles

The reporting system follows these principles:

1. Historical data must remain traceable.
2. Reports must respect business and branch permissions.
3. Reports must use the relevant historical transaction values.
4. Report versions must not silently overwrite previous versions.
5. Generated reports must remain available.
6. Report generation must not modify source transactions.
7. Reporting must remain practical and lightweight.
8. Exported reports must use Excel as the supported export format.

---

## 3. Dashboard Model

The dashboard provides a high-level operational view of the business.

The dashboard may provide information such as:

* sales;
* orders;
* branches;
* employees;
* menu activity;
* inventory conditions;
* expenses;
* payroll-related information;
* alerts;
* general business statistics.

Dashboard information must respect the user's permissions and branch scope.

---

## 4. Calendar-Based Dashboard Access

The dashboard may provide a calendar-based interface.

The user can select a date or relevant period and access the corresponding business information.

For example:

```text id="e4r1mk"
Dashboard
    ↓
Calendar
    ↓
Selected Date
    ↓
Detailed Business Information
```

The selected date must not cause the system to expose information outside the user's authorized scope.

---

## 5. Branch Dashboard

When a user has access to multiple branches, the dashboard must respect the selected branch context.

The user should be able to identify clearly which branch the displayed information belongs to.

Branch switching must not change the user's permissions.

It only changes the operational/reporting context to another branch the user is already authorized to access.

---

## 6. Business-Level Dashboard

Authorized users with business-wide access may view aggregated information across permitted branches.

Business-level information may include:

* total sales;
* branch comparison information;
* employee information;
* inventory indicators;
* general business statistics.

Aggregation must only include branches within the user's authorized scope.

---

## 7. Report Types

The system may provide reports covering:

* sales;
* orders;
* payments;
* cash sessions;
* cashiers;
* discrepancies;
* refunds;
* discounts;
* inventory;
* inventory variances;
* employees;
* attendance;
* payroll;
* expenses;
* branch performance;
* audit information;
* change history.

The exact report list may evolve as additional business requirements are defined.

---

## 8. Cash Session Reporting

Cash session reports must include relevant information such as:

* cash session;
* opening time;
* closing time;
* responsible cashier;
* orders;
* payment totals;
* expected cash;
* actual cash;
* difference;
* shortages;
* overages;
* handovers;
* corrections.

A cash session's reporting period is based on its actual opening and closing lifecycle.

It is not automatically restricted to a calendar day.

---

## 9. Monthly Report

The system must support an automatically generated monthly report.

The automatic monthly report is generated on the last calendar day of the month after the relevant cash sessions have been successfully closed.

At **23:59 on the last calendar day**, the system checks whether the relevant cash session is closed.

If it is closed, report generation begins.

If it is still open, report generation waits until the session is closed.

---

## 10. Monthly Report Generation Condition

The monthly report must use closed cash sessions.

If a cash session remains open at the end of the calendar month, that session must not be treated as completed until it is actually closed.

The report may therefore be generated later than the calendar month's final minute when a cash session remains open.

---

## 11. Report Generation Notification

The system may notify authorized users that the monthly report is expected to be generated after the relevant cash session is closed.

After successful report generation, the system must provide a report-ready notification to authorized users.

Notifications must respect business, branch, and permission scope.

---

## 12. Automatic Report Retry

If automatic report generation fails, the system must retry according to the system's retry mechanism.

If generation continues to fail after the available automatic retries, the system must:

* record the failure;
* preserve the error information;
* notify the Owner or authorized users;
* allow manual report generation/restart where permitted.

Report-generation errors must not silently disappear.

---

## 13. Manual Reports

Authorized users may manually generate reports.

Manual report generation is subject to permissions and branch scope.

The maximum period for a manually generated report is **one month**.

If a user requests a period longer than one month, the system must reject the request.

---

## 14. Report Date Validation

The system must validate report date ranges.

If:

```text
Start Date > End Date
```

the report request must be rejected.

The user must correct the date range before the report is generated.

---

## 15. Open Sessions in Manual Reports

If a requested report period includes an open cash session, the open session must be excluded from the report.

Only closed cash sessions are included in the applicable cash-session-based report.

This prevents incomplete cash-session information from being treated as final.

---

## 16. Empty Reports

A report must still be generated when there is no relevant business activity.

For values where no data exists, the report must show:

```text
0
```

It should not display:

```text
0 so'm
```

when the value is simply zero.

The report structure must remain consistent even when there is no data.

---

## 17. Report Creation Source

Reports may be generated automatically or manually.

The user-facing report does not need to expose whether a report was generated automatically or manually.

The system may retain the creation source as internal metadata for auditability and administration.

---

## 18. Report Versioning

Each generated report is treated as a report version.

A report version represents the report state for a defined period at a particular point in time.

The system must preserve previous report versions.

Previous versions must be immutable.

The latest applicable version is treated as the primary current version.

---

## 19. Report Version Creation

A new report version is created when the underlying report data has changed in a way that affects the report.

If the same report period is requested again and no relevant data has changed, the system does not need to create another version.

This prevents unnecessary duplicate report versions.

---

## 20. Report Version Information

Each report version should preserve:

* report identity;
* reporting period;
* version number;
* creation time;
* creator or system source;
* creation cause;
* status;
* relevant change information.

The version must remain linked to the underlying business data.

---

## 21. Immutable Previous Versions

Once a report version is created, it must not be silently modified.

If new information changes the report, a new version must be generated.

For example:

```text id="6u1q0h"
Report v1
   ↓
Business data changes
   ↓
Report v2
```

Version 1 remains available as the historical report state.

---

## 22. Selective Report Re-Versioning

A change should only create a new version for the report that is actually affected.

The system should not regenerate every report simply because one business record changed.

For example, a cash-session correction may affect a cash report and related reports, but unrelated reports should not automatically receive a new version unless their underlying information changed.

---

## 23. Report Updates After Corrections

When a closed cash session is corrected, the relevant report may need a new version.

The system must preserve:

* previous report version;
* new report version;
* underlying correction;
* reason for the change;
* responsible employee;
* timestamp.

The original report version remains available.

---

## 24. Report Change Notification

When a report changes because of an underlying business correction, authorized users may receive a notification.

The notification should identify relevant information such as:

* what changed;
* cash status;
* report period;
* report type;
* previous version;
* new version;
* reason;
* cash session;
* previous value;
* new value;
* change amount;
* responsible employee;
* timestamp.

If multiple metrics changed, the notification should focus on the important changes rather than presenting unnecessary detail.

---

## 25. No-Change Correction Notification

A correction that produces no actual business-data change should not create a report-change notification.

The system must distinguish between:

* correction action performed;
* actual report-affecting data change.

This prevents unnecessary notifications.

---

## 26. Report List

The reporting interface should provide a list of generated reports.

The report list should show information such as:

* report name;
* reporting period;
* version;
* status;
* creation time;
* last updated time;
* available actions.

Available actions may include:

* view;
* download.

---

## 27. Report History

Previous report versions must remain accessible to authorized users.

Historical versions should be viewable and downloadable.

Users must be able to distinguish the current primary version from previous versions.

Historical report versions must not be deleted through normal user operations.

---

## 28. Excel Export

Excel is the supported report export format.

The system does not currently require:

* PDF export;
* CSV export.

Reports should be generated as `.xlsx` files.

---

## 29. Excel Report Structure

A generated Excel report may contain separate sheets for relevant categories.

The report structure may include:

* Summary;
* Cash Sessions;
* Cashiers;
* Orders;
* Payments;
* Discrepancies;
* Corrections;
* Correction Requests;
* Audit Log;
* Change History.

The exact sheet list may vary depending on the report type.

---

## 30. Report Export

A user may download a report only if they have the required report/export permission.

The exported report must respect the user's authorized business and branch scope.

A user must not be able to export data that they are not authorized to view.

---

## 31. Exported Report Storage

Generated exported reports are retained by the system.

Exported reports must not be deleted through normal user operations.

The system must preserve generated report files or their equivalent historical report representation according to the data lifecycle rules.

---

## 32. Report Filename

The system should automatically generate report filenames.

A typical filename format is:

```text
Hisobot_2026-09-01_2026-09-15.xlsx
```

The filename should identify the report period clearly.

---

## 33. Report Search and Filtering

The current report interface requires period/date-range based search and filtering.

The primary reporting filter is:

* date range.

Additional filtering may be introduced later if business requirements justify it.

---

## 34. Report Permissions

Report access is permission-controlled.

Permissions may independently determine whether an employee can:

* view reports;
* download Excel reports;
* generate reports manually.

The same employee may have different report access across different branches.

---

## 35. Owner and Manager Reporting Access

The Owner may configure report permissions for employees.

A Manager may access reports only when the required permission has been granted.

The Manager's access remains limited by:

* business scope;
* branch scope;
* assigned permissions;
* subscription entitlement.

---

## 36. Inventory Reports

Inventory-related reports may include:

* current inventory;
* inventory movements;
* purchases;
* stock counts;
* inventory variance;
* low-stock conditions;
* out-of-stock conditions;
* inventory history.

Inventory reports must preserve branch isolation.

---

## 37. Sales and Order Reports

Sales and order reports may include:

* order count;
* completed orders;
* order values;
* order types;
* discounts;
* refunds;
* final amounts;
* product sales.

Historical order prices must be used rather than current product prices.

---

## 38. Payment Reports

Payment reports may distinguish:

* cash;
* card;
* discounts;
* refunds;
* relevant totals.

Card amounts must not be treated as physical cash.

Cash reports must remain consistent with cash session calculations.

---

## 39. Employee and Payroll Reports

Authorized users may access reports related to:

* employees;
* attendance;
* salary;
* payroll;
* bonuses.

Payroll information must remain permission-controlled.

Historical payroll values must use the applicable historical salary configuration.

---

## 40. Branch Reports

Authorized users may view branch-specific reports.

Branch reports may include:

* sales;
* orders;
* payments;
* inventory;
* employees;
* payroll;
* expenses;
* cash sessions.

The system must not expose one branch's report data to another branch without explicit authorization.

---

## 41. Business-Level Reports

Users with business-wide reporting permission may access aggregated information across permitted branches.

Aggregated reports must be calculated only from authorized branch data.

The system must preserve the ability to trace aggregated results back to the relevant branch-level information where appropriate.

---

## 42. Report and Subscription Lifecycle

Report access follows the subscription lifecycle.

When a subscription is active, authorized users may perform permitted report operations.

After subscription expiry:

* modifying functions are restricted;
* historical information remains viewable according to the read-only rules;
* relevant lists and sections may be exported to Excel;
* report access remains subject to user permissions.

Trusted devices do not bypass subscription restrictions.

---

## 43. Report and Offline Operation

Offline devices may access only the report information available within their valid offline authorization and locally available data.

The server remains authoritative for finalized reports.

Offline-generated or locally viewed information must not bypass report permissions.

After synchronization, the central system becomes the authoritative reporting source.

---

## 44. Report Auditability

Important report actions must be traceable.

The system should preserve:

* who generated a report;
* when it was generated;
* reporting period;
* report version;
* creation source;
* reason for new version where applicable;
* relevant correction or data change.

Historical report versions must remain immutable.

---

## 45. Report Performance

Reports must not significantly affect normal POS operations.

Large report generation tasks should be handled separately from critical transaction processing where appropriate.

Report generation should not block:

* order entry;
* payment processing;
* inventory operations;
* cash-session operations.

The system should remain suitable for the project's lightweight hardware requirements.

---

## 46. Business Rules Summary

| Area                           | Rule                                                             |
| ------------------------------ | ---------------------------------------------------------------- |
| Dashboard                      | Provides operational/business overview                           |
| Calendar                       | Can be used to access date-based information                     |
| Branch context                 | Must be clearly visible                                          |
| Monthly report                 | Automatically generated after applicable sessions close          |
| Last calendar day              | Automatic generation starts at 23:59 if conditions are satisfied |
| Open session                   | Wait until session closes                                        |
| Failed generation              | Retry, then notify and allow manual restart                      |
| Manual report                  | Authorized users only                                            |
| Manual period                  | Maximum one month                                                |
| Invalid dates                  | Start date greater than end date is rejected                     |
| Open sessions in manual report | Excluded                                                         |
| Empty report                   | Generated with zero values                                       |
| Creation source                | Internal metadata                                                |
| Versioning                     | New version when relevant data changes                           |
| No data change                 | No unnecessary new version                                       |
| Previous versions              | Immutable                                                        |
| Report deletion                | Not allowed through normal user operations                       |
| Export format                  | Excel                                                            |
| PDF/CSV                        | Not currently required                                           |
| Report filtering               | Date/period based                                                |
| Permissions                    | View, export, and generation can be separately controlled        |
| Historical prices              | Preserve transaction-time values                                 |
| Branch isolation               | Required                                                         |
| Subscription                   | Separate from employee permissions                               |
| Performance                    | Must not block POS                                               |

---

## 47. Business Boundaries

The current Reports and Dashboards scope does **not** define:

* PDF reports;
* CSV exports;
* real-time BI platforms;
* external analytics platforms;
* customer analytics;
* advanced predictive analytics;
* AI-generated management recommendations;
* automatic accounting filing;
* government reporting integrations;
* customizable report-builder engines;
* arbitrary SQL/report queries for end users.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 48. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `19_Data_Lifecycle_and_Deletion.md`
* `20_Business_Rules.md`

