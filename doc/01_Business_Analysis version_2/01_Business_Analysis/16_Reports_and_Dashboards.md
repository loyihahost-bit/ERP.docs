# Reports and Dashboards

**Document ID:** FF-BA-016
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for:

* dashboards;
* operational reports;
* historical reports;
* report generation;
* report versioning;
* report corrections;
* Excel exports;
* report history;
* report-related notifications;
* business and branch reporting scope.

The reporting system must provide reliable operational and historical information without modifying the underlying transactional records.

Reports must remain consistent with:

* orders;
* payments;
* cash sessions;
* inventory;
* employees;
* attendance;
* payroll;
* expenses;
* branches;
* corrections;
* audit history.

---

## 2. Reporting Principles

The reporting system follows these principles:

1. Historical transaction data must remain traceable.
2. Reports must respect Business and Branch scope.
3. Reports must respect employee permissions.
4. Historical reports must use historical transaction values.
5. Report versions must be immutable.
6. A changed report must receive a new version rather than silently changing an old version.
7. Report generation must not modify source transactions.
8. Exported reports must respect the same access controls as on-screen reports.
9. Reporting must not unnecessarily affect POS performance.
10. Excel is the supported report export format.

---

## 3. Dashboard Model

The dashboard provides a high-level operational view of the Business.

Depending on the user's permissions and scope, the dashboard may display:

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

Dashboard information must be calculated only from data the user is authorized to access.

---

## 4. Dashboard Scope

Dashboard information may be displayed at:

* Branch level;
* Business level.

A Branch-level dashboard contains information belonging to the selected authorized Branch.

A Business-level dashboard may aggregate information across multiple authorized Branches.

The dashboard must not use a user's ability to switch Branches as a way to bypass Branch permissions.

---

## 5. Calendar-Based Dashboard

The dashboard may provide a calendar-based interface.

A user may select a date or applicable period and view information associated with that period.

Example:

```text
Dashboard
    ↓
Calendar
    ↓
Selected Date / Period
    ↓
Authorized Business Information
```

The selected date must not expose information outside the user's authorized Business or Branch scope.

---

## 6. Branch Dashboard

When a user has access to multiple Branches, the dashboard must clearly identify the selected Branch context.

Changing Branch context:

* changes the reporting/operational context;
* does not change permissions;
* does not grant access to another Branch;
* must preserve the user's existing authorization scope.

---

## 7. Business-Level Dashboard

Authorized users with Business-wide access may view aggregated information across permitted Branches.

Business-level information may include:

* total sales;
* total orders;
* Branch performance;
* employee information;
* inventory indicators;
* expenses;
* payroll indicators;
* general statistics.

Aggregated results must contain only authorized Branch data.

---

# Report Types

## 8. Report Categories

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
* inventory movements;
* inventory variances;
* purchases;
* employees;
* attendance;
* payroll;
* expenses;
* Branch performance;
* audit information;
* change history.

Additional report types may be introduced through later business requirements.

---

## 9. Cash Session Reports

Cash session reports may include:

* cash session;
* opening time;
* closing time;
* responsible cashier;
* orders;
* payment totals;
* cash received;
* card received;
* expected cash;
* actual cash;
* shortage;
* overage;
* handovers;
* corrections.

A cash session report follows the actual lifecycle of the cash session.

It is not automatically limited to a calendar day.

A session opened on one calendar day and closed on another remains one historical cash session.

---

## 10. Cash Session Reporting State

Open cash sessions must not be treated as finalized cash-session results.

For finalized cash-session reporting:

* closed sessions are included;
* open sessions are excluded where the report requires finalized cash information.

This prevents incomplete cash data from being presented as final.

---

# Automatic Reports

## 11. Monthly Report

The system supports an automatically generated monthly report.

Automatic monthly report generation begins on the last calendar day of the month at **23:59**.

The system checks whether the relevant cash sessions required for the report have been closed.

If the required sessions are closed, report generation may begin.

If a required session remains open, report generation waits until the session is closed.

---

## 12. Open Session at Month End

An open cash session must not be treated as completed merely because the calendar month has ended.

For example:

```text
Month End
   ↓
Cash Session Still Open
   ↓
Monthly Final Report Waits
   ↓
Cash Session Closes
   ↓
Report Generation
```

The resulting report may therefore be generated after the calendar month has technically ended.

---

## 13. Automatic Report Generation Failure

If automatic report generation fails, the system must retry according to the configured retry mechanism.

If generation continues to fail after the available automatic retries, the system must:

* record the failure;
* preserve relevant error information;
* notify the Owner or authorized users;
* allow manual generation or restart where permitted.

A report-generation failure must not silently disappear.

---

## 14. Report Generation Source

Reports may be generated:

* automatically by the system;
* manually by an authorized user.

The creation source must be preserved as report metadata.

The source does not change the report's historical integrity requirements.

---

# Manual Reports

## 15. Manual Report Generation

Authorized users may manually generate reports.

Manual generation is subject to:

* report permissions;
* Business scope;
* Branch scope;
* subscription entitlement;
* report date validation.

---

## 16. Manual Report Period

The maximum period for one manually generated report is **one month**.

A request exceeding one month must be rejected.

Longer historical analysis may require multiple report periods.

The system must not silently reduce or truncate a user's requested period.

---

## 17. Report Date Validation

The system must validate report dates.

If:

```text
Start Date > End Date
```

the request must be rejected.

The user must provide a valid date range.

---

## 18. Open Sessions in Manual Reports

When a manual report depends on finalized cash-session information, open cash sessions are excluded.

The system must not represent an open session as a finalized cash result.

Other report categories may use their own data-state rules where cash-session closure is not applicable.

---

## 19. Empty Reports

A valid report request must still produce a report when no relevant activity exists.

Where a numeric value has no activity, the report must show:

```text
0
```

The report should not unnecessarily display:

```text
0 so'm
```

when the value is simply zero.

The report structure must remain consistent even when there is no data.

---

# Report Versioning

## 20. Report Version Model

Each generated report is treated as a versioned historical representation.

A report version represents:

* report identity;
* reporting period;
* relevant data state;
* creation time;
* creation source;
* version number.

Previous versions must remain immutable.

---

## 21. Version Creation Rule

A new report version is required when relevant underlying business data changes in a way that affects the report.

If the same report period is requested again and no relevant underlying data has changed, the system does not need to create an unnecessary duplicate version.

The system must distinguish between:

* report requested again;
* report data actually changed.

---

## 22. Selective Re-Versioning

A business-data change must only create new versions for reports affected by that change.

The system must not regenerate every report merely because one record changed.

For example:

```text
Cash Session Correction
        ↓
Affected Cash Report → New Version
        ↓
Other Unaffected Report → No New Version
```

The exact set of affected reports is determined by their underlying data dependencies.

---

## 23. Report Version Metadata

Each report version must preserve, where applicable:

* report identity;
* reporting period;
* version number;
* creation time;
* creator or system source;
* creation reason;
* status;
* relevant correction/data-change reference.

The metadata must make the historical report state identifiable.

---

## 24. Immutable Report Versions

Once created, a report version must not be silently modified.

If the underlying business data changes:

```text
Report v1
   ↓
Relevant business correction
   ↓
Report v2
```

Version 1 remains available as the historical state that existed when it was generated.

---

## 25. Report Corrections

When a business correction affects an already generated report, the system must preserve:

* previous report version;
* new report version;
* underlying correction;
* correction reason;
* responsible employee;
* correction timestamp.

The original report version remains immutable.

---

## 26. No-Change Corrections

A correction operation that produces no actual report-affecting business-data change must not create a report-change notification or unnecessary new report version.

The system must distinguish between:

* correction action performed;
* actual data change;
* actual report impact.

This avoids unnecessary report history and notifications.

---

# Report Change Notifications

## 27. Report Change Notification

When an existing report changes because of an underlying business correction, authorized users may receive a notification.

The notification may contain:

* report type;
* report period;
* previous version;
* new version;
* affected cash/session context where applicable;
* correction reason;
* responsible employee;
* timestamp;
* relevant previous value;
* relevant new value;
* change amount.

The notification should focus on meaningful report-affecting changes.

---

## 28. Notification Scope

Report notifications must respect:

* Business scope;
* Branch scope;
* notification permissions.

A user must not receive report-change information from an unauthorized Branch.

Detailed notification rules are defined in:

`17_Notifications_and_Alerts.md`

---

# Report History

## 29. Report List

The reporting interface should provide a list of generated reports.

The list may display:

* report name;
* reporting period;
* version;
* status;
* creation time;
* last relevant update;
* available actions.

Available actions may include:

* view;
* download.

The actions displayed must depend on the user's permissions.

---

## 30. Report History

Authorized users must be able to access previous report versions.

Historical versions should be:

* viewable;
* downloadable where export permission exists;
* clearly distinguishable from the current primary version.

Historical report versions must not be deleted through normal user operations.

---

## 31. Primary Report Version

For each report identity and period, the latest applicable version is treated as the current primary version.

Previous versions remain historical references.

The existence of a newer version must not modify the content of older versions.

---

# Excel Export

## 32. Supported Export Format

Excel is the supported report export format.

Reports are exported as:

```text
.xlsx
```

The current scope does not require PDF or CSV export.

---

## 33. Excel Report Structure

A generated Excel report may contain separate sheets for relevant categories.

Depending on the report type, sheets may include:

* Summary;
* Cash Sessions;
* Cashiers;
* Orders;
* Payments;
* Discounts;
* Refunds;
* Discrepancies;
* Corrections;
* Correction Requests;
* Inventory;
* Employees;
* Payroll;
* Audit Log;
* Change History.

The exact sheet structure depends on the report type.

---

## 34. Export Authorization

A user may download/export a report only when the required permission exists.

Export access must respect:

* Business scope;
* Branch scope;
* employee permissions;
* subscription entitlement.

Exporting a report must never provide more information than the user is authorized to view.

---

## 35. Exported Report History

Generated report exports or their equivalent historical representation must be retained according to the system's data-lifecycle rules.

Normal users must not be able to delete historical report versions through ordinary report operations.

The retained report representation must remain consistent with its version metadata.

---

## 36. Report Filename

The system should generate report filenames automatically.

Example:

```text
Hisobot_2026-09-01_2026-09-15.xlsx
```

The filename should clearly identify the report period.

The exact naming convention may later be standardized during system analysis.

---

# Filtering and Access

## 37. Report Filtering

The primary report filter is date/period based.

The current reporting scope supports:

* date range;
* Branch context where authorized;
* report type.

Additional filters may be introduced later when justified by business requirements.

---

## 38. Report Permissions

Report permissions may independently control whether an employee can:

* view reports;
* generate reports;
* download/export reports;
* access Branch-level reports;
* access Business-level reports;
* access sensitive payroll information.

An employee may have different reporting permissions in different Branches.

---

## 39. Owner Reporting Access

The Owner may access reports according to Business-level permissions.

The Owner may configure reporting permissions for employees.

Owner access remains subject to the overall subscription entitlement.

---

## 40. Manager Reporting Access

A Manager may access reports only when the required permission has been granted.

Manager access remains limited by:

* Business scope;
* Branch scope;
* assigned permissions;
* subscription entitlement.

A Manager must not gain Business-wide reporting authority merely by being assigned to one Branch.

---

# Domain Reports

## 41. Sales and Order Reports

Sales and order reports may include:

* order count;
* order type;
* product sales;
* item quantities;
* transaction values;
* discounts;
* refunds;
* final amounts.

Historical order prices must be taken from the recorded transaction snapshot.

Current menu prices must not be used to recalculate historical sales.

---

## 42. Payment Reports

Payment reports may distinguish:

* cash;
* card;
* debt;
* mixed payments;
* discounts;
* refunds;
* applicable net amounts.

Cash and card must remain distinguishable.

Only physical cash-related transactions contribute to physical cash reconciliation.

Detailed payment rules are defined in:

`14_Payments_Discounts_and_Refunds.md`

---

## 43. Cash Session Reports

Cash reports may include:

* opening cash;
* cash received;
* cash refunds;
* expected cash;
* actual cash;
* shortage;
* overage;
* card totals;
* relevant adjustments;
* handovers;
* corrections.

Historical cash-session reports must use the applicable cash-session transaction history.

---

## 44. Inventory Reports

Inventory reports may include:

* current stock;
* stock movements;
* purchases;
* stock adjustments;
* inventory counts;
* inventory variances;
* low-stock conditions;
* out-of-stock conditions;
* inventory history.

Inventory reports must preserve Branch isolation.

Historical inventory corrections must remain traceable.

---

## 45. Employee and Payroll Reports

Authorized users may access reports covering:

* employees;
* attendance;
* salary;
* payroll;
* bonuses.

Payroll information is permission-controlled.

Historical payroll reports must use the salary configuration and calculation snapshot applicable to the payroll period.

---

## 46. Expense Reports

Expense reports may include:

* expenses by Branch;
* expense amount;
* expense category;
* date;
* responsible user;
* comments where applicable.

Expense records must respect the established Business and Branch permissions.

---

## 47. Branch Performance Reports

Authorized users may view Branch-level performance information such as:

* sales;
* orders;
* payments;
* inventory indicators;
* employees;
* payroll;
* expenses;
* cash sessions.

A Branch performance report must not expose unauthorized Branch information.

---

## 48. Business-Level Aggregation

Authorized users may view aggregated Business-level information across permitted Branches.

The aggregation must use only data within the user's authorized scope.

Where appropriate, aggregated values should remain traceable to the underlying Branch-level data.

---

# Subscription and Offline Reporting

## 49. Report and Subscription Lifecycle

Report functionality is subject to subscription entitlement.

While the subscription is active, authorized users may perform permitted report operations.

After subscription expiry:

* modifying functions are restricted according to subscription rules;
* historical information remains viewable according to read-only rules;
* relevant information may be exported to Excel;
* report access remains subject to employee permissions.

Subscription expiry must not silently delete historical reports.

---

## 50. Report and Offline Operation

Offline devices may access only reporting information that is:

* available locally;
* covered by valid offline authorization;
* within the employee's Branch and permission scope.

The central server remains authoritative for finalized reports.

Offline operation must not bypass:

* subscription restrictions;
* report permissions;
* Branch scope;
* historical report integrity.

After synchronization, the central system is the authoritative reporting source.

---

# Audit and Integrity

## 51. Report Auditability

Important report actions must be traceable.

The system should preserve:

* actor;
* report identity;
* reporting period;
* report version;
* creation time;
* creation source;
* generation reason where applicable;
* relevant correction/data-change reference.

---

## 52. Report and Source Data Separation

Generating a report must never modify the source business transaction.

Reports are derived representations of business data.

For example:

```text
Orders / Payments / Inventory / Payroll
                ↓
             Report
```

Not:

```text
Report
  ↓
Modify Source Transaction
```

Any correction must occur through the relevant business domain operation, after which the affected report may receive a new version.

---

## 53. Historical Integrity

Historical reports must remain internally consistent with the transaction state represented by that report version.

Current changes to:

* product prices;
* recipes;
* discounts;
* employee salaries;
* permissions;
* Branch configuration;

must not silently rewrite historical report versions.

If relevant source data changes through an authorized correction, a new affected report version is created.

---

# Performance

## 54. POS Performance

Reporting must not significantly affect critical POS operations.

Report generation must not unnecessarily block:

* order creation;
* order acceptance;
* payment processing;
* inventory operations;
* cash-session operations;
* cashier handover.

Large report generation should be handled separately from critical transaction processing where appropriate.

---

## 55. Report Generation Performance

The reporting system should support efficient generation for:

* daily reports;
* monthly reports;
* Branch reports;
* Business-level reports;
* historical report versions.

The system must remain suitable for the project's lightweight hardware requirements.

---

# 56. Business Rules Summary

| Area                    | Rule                                                    |
| ----------------------- | ------------------------------------------------------- |
| Dashboard               | Provides operational/business overview                  |
| Dashboard scope         | Branch or authorized Business scope                     |
| Calendar                | Supports date/period-based access                       |
| Branch context          | Must be clearly identified                              |
| Monthly report          | Automatically generated after required sessions close   |
| Automatic generation    | Starts at 23:59 on the last calendar day                |
| Open session            | Prevents final cash-session completion                  |
| Failed generation       | Retry, record failure, notify, allow authorized restart |
| Manual reports          | Authorized users only                                   |
| Manual period           | Maximum one month                                       |
| Invalid date range      | Rejected                                                |
| Open cash session       | Excluded from finalized cash-session reporting          |
| Empty report            | Generated with zero values                              |
| Creation source         | Preserved as metadata                                   |
| Report versioning       | New version when relevant data changes                  |
| No relevant change      | No unnecessary new version                              |
| Previous versions       | Immutable                                               |
| Selective re-versioning | Only affected reports receive new versions              |
| Report history          | Preserved                                               |
| Report deletion         | Not available through normal user operations            |
| Export format           | `.xlsx`                                                 |
| PDF/CSV                 | Not currently required                                  |
| Export permission       | Separate permission may be applied                      |
| Payroll reports         | Permission-controlled                                   |
| Branch isolation        | Required                                                |
| Business aggregation    | Only authorized Branches included                       |
| Subscription            | Independent from employee permissions                   |
| Offline reporting       | Limited to valid local authorization/data               |
| Audit                   | Report generation and version changes traceable         |
| Performance             | Must not block critical POS operations                  |

---

# 57. Business Boundaries

The current Reports and Dashboards scope does **not** define:

* PDF reports;
* CSV exports;
* external BI platforms;
* external analytics platforms;
* customer analytics;
* advanced predictive analytics;
* AI-generated management recommendations;
* automatic accounting filing;
* government reporting integrations;
* customizable end-user report-builder engines;
* arbitrary SQL/report queries for end users;
* automated tax reporting.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 58. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
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

