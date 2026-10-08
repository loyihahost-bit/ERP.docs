# Reporting Domain

**Document ID:** DA-13
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Reporting domain provides business and operational reports based on authoritative system data.

It is responsible for:

* report definitions;
* report scope;
* report generation;
* report snapshots;
* report versions;
* report history;
* report generation status;
* Excel export;
* report access control;
* report consistency;
* report regeneration after relevant corrections.

The Reporting domain does not own the underlying business data.

Orders, Payments, Inventory, Cash Sessions, Employees, Payroll, Expenses, and Audit remain authoritative in their respective domains.

---

# 2. Reporting Principle

Reports are derived views of authoritative business data.

The logical relationship is:

```text id="a7f2m9"
Authoritative Domain Data
        ↓
Consistent Snapshot
        ↓
Report Generation
        ↓
Immutable Report Version
        ↓
View / Excel Export
```

A report must not become an alternative source of truth for operational data.

---

# 3. Report Scope

Reports may be generated at:

* Business scope;
* Branch scope;
* authorized multi-Branch scope.

The requested scope must be validated against:

* Business;
* Branch;
* Employee permissions;
* subscription entitlement.

---

# 4. Business Scope

A Business-level report may aggregate authorized data across multiple Branches.

Only users with the required Business-level permission may access such reports.

Branch-level restrictions must not be bypassed through Business-level reporting.

---

# 5. Branch Scope

A Branch report contains only data belonging to the requested Branch and permitted related entities.

Branch isolation must be preserved across:

* report generation;
* report queries;
* report snapshots;
* report versions;
* Excel exports;
* report downloads.

---

# 6. Report Definition

A Report Definition identifies the logical type of report.

Examples include:

* Sales Report;
* Orders Report;
* Payment Report;
* Cash Session Report;
* Cashier Report;
* Inventory Report;
* Inventory Variance Report;
* Purchase Report;
* Employee Report;
* Attendance Report;
* Payroll Report;
* Expense Report;
* Branch Performance Report;
* Refund Report;
* Discount Report;
* Audit Report.

The exact list may evolve without changing the underlying reporting principles.

---

# 7. Report Identity

A logical report identity is based on:

```text id="c4n8p1"
Report Definition
+
Period
+
Scope
```

This identifies the report subject.

A report version represents a specific historical state of that report.

---

# 8. Report Version

A Report Version is an immutable representation of a generated report.

Each version preserves:

* report identity;
* version number;
* creation time;
* period;
* scope;
* creator/system source;
* creation reason;
* underlying data state or snapshot reference.

Once finalized, the version must not be modified.

---

# 9. Initial Version

The first successfully generated report becomes the initial version.

Conceptually:

```text id="k6m3q8"
Report
  ↓
Version 1
```

Subsequent relevant data changes may create Version 2, Version 3, and so on.

---

# 10. Version Creation

A new report version is created only when relevant underlying data changes the report result.

Examples:

* correction changes sales totals;
* payment correction changes payment totals;
* inventory correction changes inventory metrics;
* cash correction changes cash-session metrics.

A correction that does not affect the relevant report does not require a new version.

---

# 11. Version Immutability

Once a report version is finalized:

* its result cannot be silently edited;
* its historical values cannot be overwritten;
* its period cannot be changed;
* its scope cannot be changed;
* its source context cannot be changed.

Corrections produce a new version where required.

---

# 12. Report Snapshot

Report generation must use a consistent data snapshot.

The snapshot must represent a coherent state of the relevant source data.

A report must not combine incompatible states from different moments of a transaction.

---

# 13. Snapshot Consistency

For example, a Sales Report must not calculate:

```text id="m2q7v4"
Orders at State A
+
Payments at State B
+
Discounts at State C
```

when those states are inconsistent.

The report must use a consistent logical snapshot.

---

# 14. Report Period

Reports operate on an explicit period.

A period contains:

* start date/time;
* end date/time;
* applicable timezone/business calendar context.

The period must be preserved in the Report Version.

---

# 15. Manual Report Range

Manual reports are limited to a maximum period of one calendar month according to the established System Analysis rule.

An invalid range must be rejected.

Examples:

* start > end → reject;
* period longer than allowed → reject;
* unauthorized Branch → reject.

---

# 16. Empty Reports

A valid report period with no matching records still produces a valid report.

The result contains zero values or an appropriate empty-state representation.

The system must not treat an empty business period as a generation failure.

---

# 17. Monthly Automatic Reports

The system automatically generates the monthly report on the last calendar day of the month.

The report generation is dependent on the required operational state.

If the relevant Cash Session remains open, the monthly report waits according to the established system rules.

---

# 18. Open Cash Session Dependency

A monthly report that depends on final Cash Session values must not finalize incomplete session data.

The system waits for the required session closure before generating the final report.

The waiting process must not block POS operations.

---

# 19. Report Creation Source

Every report version preserves its creation source.

Possible sources include:

* scheduled system generation;
* manual generation;
* correction-triggered regeneration;
* authorized administrative operation.

---

# 20. Creation Reason

A new report version may include a reason such as:

* initial generation;
* relevant correction;
* recalculation;
* authorized regeneration.

The reason supports historical interpretation.

---

# 21. Report Status

Report generation may conceptually use:

```text id="q5n8r3"
Requested
   ↓
Generating
   ↓
Completed
```

Failure may result in:

```text id="z4m7p2"
Failed
   ↓
Retrying
   ↓
Completed
```

The exact technical job lifecycle is defined by the Background Jobs domain/system rules.

---

# 22. Failed Generation

A failed report generation must not create a falsely finalized report version.

The failure should preserve:

* failure status;
* relevant error information;
* generation context;
* correlation information.

---

# 23. Retry

Report generation may be retried according to the global retry policy.

Retries must be idempotent.

A retry must not create duplicate finalized versions representing the same unchanged state.

---

# 24. Background Generation

Heavy reports may be generated asynchronously.

Examples include:

* large Branch reports;
* large Business reports;
* large Excel exports;
* long inventory histories;
* large audit exports.

Background generation must not block POS operations.

---

# 25. Small Reports

Small and lightweight reports may be generated synchronously where performance permits.

The implementation decision belongs to the Architecture phase.

The domain requirement is that reporting must not unnecessarily delay operational POS workflows.

---

# 26. Excel Export

The supported report export format is:

```text
.xlsx
```

PDF and CSV are outside the current Reporting domain scope.

---

# 27. Excel Snapshot Integrity

An Excel export represents a specific report version.

The exported file must correspond to the selected immutable version.

Exporting a report again must not silently recalculate it from newer source data when the user selected an older version.

---

# 28. Export Permissions

Export requires appropriate report access permission.

The same Business/Branch scope rules apply to exports as to report viewing.

A user who cannot view a report must not export it.

---

# 29. Export Audit

Report downloads and exports may be auditable where the operation is considered important or sensitive.

At minimum, sensitive or administrative report exports should remain traceable according to Audit domain rules.

---

# 30. Report History

Authorized users may view historical report versions.

History may include:

* version number;
* created time;
* period;
* scope;
* source;
* reason;
* relevant correction/change reference.

Historical versions remain immutable.

---

# 31. Correction Relationship

When a correction changes report results, the new report version should retain a relationship to the correction/change that caused the new version.

Conceptually:

```text id="v8p3k5"
Report Version 1
      ↓
Correction
      ↓
Report Version 2
```

This supports historical reconstruction.

---

# 32. No-Impact Correction

A correction may exist without affecting a specific report.

In this case:

* the correction remains part of its source domain history;
* the report does not receive an unnecessary new version.

This prevents meaningless report version growth.

---

# 33. Sales Reports

Sales reporting may consume:

* Orders;
* Order Items;
* discounts;
* relevant payment information;
* cancellations/refunds where applicable.

The Reporting domain does not modify those source records.

---

# 34. Payment Reports

Payment reports may consume:

* Payment records;
* payment method;
* payment portions;
* debt payments;
* refunds;
* overpayments;
* relevant Cash Session context.

Payment remains authoritative in the Payment domain.

---

# 35. Cash Reports

Cash reports may consume:

* Cash Sessions;
* opening cash;
* expected cash;
* actual cash;
* differences;
* corrections;
* cashier identity;
* payment totals.

The Cash domain remains authoritative for Cash Session data.

---

# 36. Inventory Reports

Inventory reports may consume:

* stock movements;
* purchases;
* inventory adjustments;
* variances;
* product quantities;
* recipe-related consumption.

Inventory remains authoritative for stock state.

---

# 37. Employee Reports

Employee reports may consume:

* employee state;
* Branch assignments;
* attendance;
* role context where authorized.

The Employee domain remains authoritative for employee data.

---

# 38. Payroll Reports

Payroll reports use finalized Payroll records.

The Reporting domain must not independently recalculate salary.

Payroll remains authoritative for:

* salary calculation;
* payroll amount;
* payroll snapshot;
* payroll correction.

---

# 39. Expense Reports

Expense reports consume recorded Business/Branch expenses.

Expense records remain authoritative in their source domain.

---

# 40. Audit Reports

Audit reports consume immutable Audit records.

The Reporting domain may filter and present them but must not modify the underlying audit history.

---

# 41. Branch Performance

Branch performance reports may combine authorized metrics from several domains.

Examples:

* sales;
* orders;
* payments;
* cash;
* inventory;
* expenses;
* payroll;
* operational performance.

Cross-domain aggregation must use consistent source snapshots.

---

# 42. Report Access

Every report request must validate:

```text id="e7m4q9"
Authentication
+
Business Scope
+
Branch Scope
+
Permission
+
Subscription Entitlement
```

Subscription expiry may place the Business into read-only reporting access according to Subscription rules.

---

# 43. Read-Only Subscription State

When the Business is in read-only state:

* authorized report viewing remains available;
* report history remains available;
* allowed Excel exports remain available;
* modifying business operations remain blocked.

Reporting must not bypass subscription restrictions.

---

# 44. Report Data Security

Reports must not expose another Business's data.

Tenant isolation must be preserved through:

* report queries;
* generation jobs;
* snapshots;
* exports;
* background workers;
* downloaded files.

---

# 45. Offline Reporting

Offline devices may display supported locally available report information.

Offline reports are not a replacement for finalized server reports.

When synchronized, the server remains authoritative for finalized report versions.

---

# 46. Offline Report Identity

Offline-generated report requests must retain stable identities where queued for synchronization.

Duplicate synchronization must not create duplicate finalized report versions.

---

# 47. Report and Configuration

Reports must respect the configuration applicable to the relevant historical period.

For example, a later Menu price change must not rewrite historical Order price snapshots.

Reporting consumes historical transaction values rather than current configuration when the transaction already contains the applicable snapshot.

---

# 48. Report and Subscription History

Historical report versions must preserve the subscription/business context required to interpret their existence.

A later tariff change must not rewrite a previously generated report.

---

# 49. Report and Data Deletion

Reports follow Business data lifecycle rules.

During the allowed retention period:

* authorized reports remain accessible;
* historical versions remain available according to subscription/lifecycle state.

After permanent Business deletion, report data belonging to that Business is deleted according to Data Lifecycle rules.

---

# 50. Report Generation and POS

Report generation must not block:

* Order creation;
* Order acceptance;
* Payment;
* Cash operations;
* Inventory transactions;
* Kitchen operations.

Heavy reporting work must be isolated from critical POS paths.

---

# 51. Concurrency

Reporting must handle concurrent changes safely.

Examples:

* report generation while a payment is created;
* report generation while inventory changes;
* report generation while a Cash Session closes;
* report generation while a correction is created.

The report must use a consistent snapshot rather than an accidental mixture of states.

---

# 52. Duplicate Generation

The same report definition, period, scope, and unchanged source state must not create unnecessary duplicate finalized versions.

Idempotency keys or equivalent logical identity controls should prevent duplicate generation.

---

# 53. Version Ordering

Report versions must have deterministic ordering.

Version numbers must not be reused.

A later version must never replace the identity of an earlier version.

---

# 54. Report Corrections

A correction affecting report data must preserve:

```text id="b9q2n6"
Original Report Version
+
Correction Reference
+
New Report Version
```

This relationship must remain queryable for authorized users.

---

# 55. Report Reconstruction

An authorized user should be able to determine:

* what report was generated;
* for which period;
* for which scope;
* when it was generated;
* what source state it represented;
* whether a correction caused a later version.

---

# 56. Report Domain Services

Potential Reporting domain services include:

```text id="t6m8p3"
Report Definition Service
Report Scope Validation Service
Report Generation Service
Report Snapshot Service
Report Version Service
Report History Service
Excel Export Service
Report Access Service
```

These are logical domain services and do not necessarily represent separate applications.

---

# 57. Domain Events

Potential events include:

```text id="n4c7v2"
ReportGenerationRequested
ReportGenerationStarted
ReportGenerationCompleted
ReportGenerationFailed
ReportVersionCreated
ReportVersionSuperseded
ReportExportRequested
ReportExportCompleted
ReportExportFailed
```

A historical report version remains immutable even when a newer version is created.

---

# 58. Aggregate Boundaries

The Reporting domain may conceptually contain:

* Report Definition;
* Report Identity;
* Report Version;
* Report Snapshot Reference;
* Report Generation;
* Report Export.

It does not own:

* Order;
* Payment;
* Inventory;
* Cash Session;
* Employee;
* Payroll;
* Menu;
* Subscription;
* Audit source records.

---

# 59. Invariants

### Identity and Scope

1. Every report version has a stable identity.
2. Report identity includes report definition, period, and scope.
3. Business scope is mandatory.
4. Branch scope is explicit where applicable.
5. Cross-Business report access is prohibited.
6. Unauthorized Branch data is excluded.
7. Report access requires appropriate permission.
8. Subscription restrictions are enforced.

### Versions

9. Every finalized report version is immutable.
10. Version numbers are never reused.
11. Earlier versions remain accessible according to lifecycle rules.
12. A new version is created only when relevant data changes.
13. A no-impact correction does not create an unnecessary new version.
14. A new version preserves its creation reason.
15. A relevant correction may create a new version.
16. Previous versions are never silently overwritten.

### Consistency

17. Reports use a consistent logical snapshot.
18. Reports do not mix incompatible source states.
19. Cross-domain reports use consistent source data.
20. Historical transaction snapshots take precedence over current configuration where applicable.
21. Report generation does not modify authoritative business data.

### Periods

22. Every report has an explicit period.
23. Manual report ranges respect the configured maximum.
24. Invalid ranges are rejected.
25. Empty valid periods produce valid reports.
26. Monthly reports use the correct calendar period.
27. Monthly reports do not finalize incomplete required Cash Session data.

### Generation

28. Report generation has a defined lifecycle.
29. Failed generation does not produce a falsely finalized version.
30. Generation failures are observable.
31. Retry is bounded.
32. Retry is idempotent.
33. Duplicate generation is prevented.
34. Heavy reports may execute asynchronously.
35. Report generation does not block POS operations.

### Export

36. Supported export format is `.xlsx`.
37. Exported data corresponds to the selected report version.
38. Export requires report access permission.
39. Export respects Business and Branch scope.
40. Sensitive exports may be audited.
41. Export failure does not modify the report version.

### Corrections

42. Relevant corrections preserve a relationship to the affected report version.
43. A correction does not modify an existing report version.
44. New report versions preserve historical continuity.
45. Report history can identify the correction that caused a new version.

### Subscription

46. Read-only subscription state may allow authorized report viewing.
47. Allowed Excel export remains subject to permission.
48. Report generation cannot bypass subscription restrictions.
49. Historical reports do not change because of tariff changes.

### Offline

50. Offline report requests use stable identity.
51. Duplicate offline synchronization does not create duplicate report versions.
52. Server remains authoritative for finalized reports.
53. Offline reporting cannot bypass Branch scope.
54. Offline reporting cannot bypass permission.
55. Offline reporting cannot bypass subscription restrictions.

### Security

56. Report queries enforce tenant isolation.
57. Background report workers preserve tenant isolation.
58. Export workers preserve tenant isolation.
59. Report snapshots preserve tenant context.
60. Downloaded reports correspond to authorized scope.

### Historical Integrity

61. Report creation time is preserved.
62. Report source is preserved.
63. Report reason is preserved.
64. Report period is preserved.
65. Report scope is preserved.
66. Report version history remains reconstructable.

### Integration

67. Payroll reports consume Payroll results.
68. Cash reports consume Cash Session results.
69. Inventory reports consume Inventory results.
70. Payment reports consume Payment results.
71. Audit reports consume Audit records.
72. Reporting does not independently redefine domain rules.

---

# 60. Completion Criteria

The Reporting domain is complete when:

* report identity is defined;
* Business and Branch scope is defined;
* report definitions are separated from source domains;
* report snapshots are defined;
* immutable report versions are defined;
* correction-driven versioning is defined;
* no-impact corrections are defined;
* monthly automatic reporting is defined;
* manual report limits are defined;
* empty reports are defined;
* Excel export is defined;
* report access control is defined;
* subscription read-only behavior is defined;
* offline reporting boundaries are defined;
* concurrency and idempotency are defined;
* report history is reconstructable;
* data deletion boundaries are defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous Domain Documents

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/11_Kitchen_Domain.md`
* `docs/03_Domain_Analysis/12_Employee_and_Payroll_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/12_Employee_and_Payroll_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

