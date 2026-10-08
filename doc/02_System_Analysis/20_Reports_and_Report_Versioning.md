# Reports and Report Versioning

**Document ID:** SA-20
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for reports, report generation, report snapshots, report versioning and Excel export.

The system must provide reliable historical reporting without allowing later corrections or configuration changes to silently rewrite previously generated report versions.

Reports must use a consistent transactional snapshot and must remain attributable to the Business, Branch, period and source data used to generate them.

---

## 2. Scope

This document covers:

* report identity;
* report types;
* Business and Branch scope;
* report periods;
* report generation;
* monthly reports;
* manual reports;
* report snapshots;
* report versions;
* report finalization;
* correction impact;
* report regeneration;
* empty reports;
* report failures;
* retry;
* duplicate generation prevention;
* Excel export;
* large exports;
* report access;
* report history;
* offline reports;
* subscription restrictions;
* audit;
* concurrency;
* performance;
* historical integrity.

---

## 3. Report Context

Reports are generated from Business operational data.

The general context is:

```text id="rpt472"
Business
   ↓
Report Definition
   ↓
Period + Scope
   ↓
Consistent Data Snapshot
   ↓
Report Version
   ↓
Excel Export
```

A report must always have a defined Business context.

Branch-scoped reports additionally identify the Branch.

---

## 4. Report Scope

A report may be:

* Business-scoped;
* Branch-scoped;
* otherwise explicitly scoped by an authorized report definition.

The system must not mix data from unrelated Business tenants.

A Branch report must not include another Branch's data unless the report definition explicitly requires Business-level aggregation.

---

## 5. Report Identity

A logical report is identified by:

```text id="rid583"
Report Definition
+
Period
+
Scope
```

This combination identifies the logical report.

A new version of the same logical report does not create a new logical report identity.

---

## 6. Report Version Identity

Every Report Version has its own stable UUID.

The Report Version UUID identifies one immutable generated state of the report.

A new version is created only when relevant underlying data changes the report result.

---

## 7. Report Definition

A Report Definition identifies what information the report calculates.

Examples include:

* Sales Report;
* Order Report;
* Payment Report;
* Cash Session Report;
* Cashier Report;
* Inventory Report;
* Inventory Variance Report;
* Refund Report;
* Discount Report;
* Employee Report;
* Attendance Report;
* Payroll Report;
* Expense Report;
* Branch Performance Report;
* Audit Report.

The system may support additional predefined report definitions later.

---

## 8. Report Period

Every report must define a period.

The period contains:

* start date/time;
* end date/time;
* applicable Business timezone;
* period interpretation.

The system must use consistent period boundaries.

---

## 9. Monthly Report

Monthly reports represent the applicable calendar month.

The monthly report is generated automatically on the last calendar day at the configured report-generation time.

The current defined generation time is:

**23:59 on the last calendar day of the month.**

---

## 10. Open Cash Session at Monthly Generation

If an applicable Cash Session remains open when monthly report generation begins:

* the monthly report waits;
* the report must not be finalized using an incomplete Cash Session;
* generation continues after the required session is closed.

The system must not silently exclude the open session.

---

## 11. Monthly Report Completion

Once all required source data is available, the system generates the report using a consistent snapshot.

The generated version records:

* period;
* scope;
* creation time;
* source;
* snapshot context;
* report definition.

---

## 12. Manual Reports

Authorized users may generate reports manually.

Manual reports must have:

* report definition;
* Business/Branch scope;
* start date;
* end date.

Manual report period is limited to a maximum of **one calendar month**.

---

## 13. Invalid Manual Period

The system rejects a manual report when:

* end date is before start date;
* required scope is invalid;
* requested period exceeds the allowed maximum;
* user lacks permission;
* subscription does not allow the requested operation.

The system must return a business-safe validation message.

---

## 14. Empty Reports

A valid report period with no relevant data must still produce a report.

For example:

```text id="emp921"
Orders: 0
Payments: 0
Refunds: 0
Inventory Movements: 0
```

The report must not be treated as a generation failure merely because its values are zero.

---

## 15. Consistent Snapshot

Report generation must use a consistent transactional snapshot.

The report must not combine incompatible states from different moments of the same data set.

For example, a report must not use:

* Orders from one state;
* Payments from a later state;
* Inventory from another inconsistent state.

The snapshot must represent one coherent reporting state.

---

## 16. Snapshot Source

A report version must be linked to the data state used for generation.

The system should retain enough metadata to identify:

* snapshot timestamp/context;
* source transaction boundary where applicable;
* report definition;
* period;
* scope;
* relevant configuration/version information.

---

## 17. Report Version Creation

A new Report Version is created when relevant underlying data changes the report result.

Examples:

* payment correction changes sales total;
* refund changes refund total;
* cash correction changes discrepancy;
* inventory correction changes inventory report;
* payroll correction changes payroll report.

---

## 18. No-Change Correction

A correction that does not change any metric included in a specific report does not require a new version of that report.

The report remains unchanged.

The correction may still be recorded in audit/history.

---

## 19. Report Version Immutability

Once a Report Version is created, it is immutable.

The system must not edit the existing version in place.

If the underlying report result changes, a new version is created.

---

## 20. Report Version Chain

Versions of the same logical report form a historical chain:

```text id="ver318"
Report
  ├── Version 1
  ├── Version 2
  ├── Version 3
  └── Version N
```

Every version remains independently identifiable.

---

## 21. Version Creation Reason

Each Report Version must record why it was generated.

Possible reasons include:

* Initial Generation;
* Data Correction;
* Payment Correction;
* Refund;
* Inventory Adjustment;
* Payroll Correction;
* Configuration-Related Regeneration;
* Manual Regeneration;
* System Retry.

The exact reason must remain identifiable.

---

## 22. Report Creator

The system must identify whether the report was created by:

* Employee;
* SYSTEM;
* background job.

The creation source is part of report metadata.

---

## 23. Report Version Metadata

A Report Version should contain:

* Report Version UUID;
* logical Report identity;
* Business UUID;
* Branch UUID where applicable;
* Report Definition;
* period;
* scope;
* creation timestamp;
* creator/source;
* creation reason;
* snapshot metadata;
* status.

---

## 24. Report Status

A report generation operation may use states such as:

```text id="rst741"
Pending
  ↓
Generating
  ↓
Generated
```

Failure may result in:

```text id="rst742"
Generating
  ↓
Failed
```

A generated immutable version remains available independently from later generation attempts.

---

## 25. Report Generation Failure

If report generation fails:

* the operation is marked Failed;
* the failure is logged;
* the failure is auditable;
* the system may retry according to retry policy;
* no incomplete report is treated as valid.

A failed report must not be presented as successfully generated.

---

## 26. Retry Policy

Automatic retry is permitted for retryable failures.

Retry behavior follows the system-wide background job policy:

* bounded retries;
* controlled backoff;
* idempotency;
* failure state after retry limit.

After the retry limit is reached:

* the operation remains Failed;
* the failure is logged;
* an appropriate notification may be generated.

---

## 27. Duplicate Report Generation

The system must prevent duplicate generation of the same logical report/version operation.

Generation requests must use deterministic report identity and idempotency protection.

Repeated requests should return the existing result or existing generation state where applicable.

---

## 28. Concurrent Report Generation

If two workers attempt to generate the same report simultaneously:

* only one authoritative generation operation is accepted;
* the other request must reuse or reference the existing operation;
* duplicate versions must not be created.

---

## 29. Report and Corrections

Corrections do not modify historical report versions.

Instead:

1. Original report version remains immutable.
2. Correction is recorded separately.
3. System determines whether the correction affects the report.
4. If affected, a new report version is generated.
5. New version references the relevant correction/change.

---

## 30. Report Version and Correction Link

When a new version is created because of a correction, the system should preserve:

* correction UUID;
* source entity;
* previous report version;
* new report version;
* creation reason.

This creates a traceable relationship between the business correction and report change.

---

## 31. Report Data Integrity

A report must use authoritative server/database state for finalized reporting.

Stale client-side state must not be treated as authoritative for final report generation.

---

## 32. Report and Historical Prices

Reports use historical transaction price snapshots.

Current Product prices must not be used to reinterpret historical Orders.

---

## 33. Report and Historical Recipes

Inventory-related reports use the historical Recipe Version associated with the relevant transaction.

Current Recipe configuration must not rewrite historical inventory results.

---

## 34. Report and Historical Payroll

Payroll reports use the applicable Payroll snapshot/version.

Current salary configuration must not recalculate finalized historical payroll.

---

## 35. Report and Cash Sessions

Cash reports use Cash Session state and transaction history.

A finalized Cash Session remains historically identifiable.

Corrections create separate correction records and, where relevant, new report versions.

---

## 36. Report and Payments

Payment reports use payment snapshots and financial correction history.

Payment corrections do not rewrite historical payment records.

If the correction changes a report metric, a new report version is generated.

---

## 37. Report and Refunds

Refund reports use the original refund operation and its correction history.

A refund does not rewrite the original payment.

Relevant changes may generate a new report version.

---

## 38. Report and Discounts

Discount reports use the discount snapshot recorded on the relevant Order.

Current Product price or current discount configuration must not rewrite historical discount results.

---

## 39. Report and Inventory

Inventory reports use authoritative Inventory Transactions.

Inventory corrections preserve original movements.

If a correction changes the report result, a new report version is created.

---

## 40. Report and Attendance

Attendance reports use historical attendance records and applicable corrections.

Current Employee status does not remove historical attendance.

---

## 41. Report and Notifications

Report generation may trigger notifications.

Notification failure must not roll back a successfully generated report.

---

## 42. Report Access

Report access requires validation of:

* Business scope;
* Branch scope;
* employee status;
* permission;
* subscription state.

The system must not expose a report from another Business.

---

## 43. Branch Report Access

A Branch-scoped report may be accessed only by employees with the required Branch authority.

Business-level authorized users may access multiple Branch reports according to their permissions.

---

## 44. Report History

Authorized users may view historical versions of a report.

Each version remains separately identifiable.

The system must not hide older versions merely because a newer version exists.

---

## 45. Report Version Download

Authorized users may download the selected Report Version.

The downloaded file must correspond to the exact selected snapshot/version.

Downloading a report does not create a new report version.

---

## 46. Excel Export

Report export is supported in:

**`.xlsx` format.**

The export must represent the selected Report Version exactly.

The system does not require PDF or CSV export in the current scope.

---

## 47. Excel Export Integrity

An Excel export must not recalculate the report from current live data.

It must use the selected immutable Report Version.

This ensures that downloading an older version produces the same historical report state.

---

## 48. Large Excel Export

Large Excel exports may run as background jobs.

The export job must:

* have a stable job UUID;
* reference the Report Version;
* use idempotency;
* support retry;
* preserve failure state;
* not block POS operations.

---

## 49. Export Audit

Report downloads/exports are auditable where required by the audit policy.

The system may record:

* Employee;
* Business;
* Branch;
* Report Version;
* export format;
* timestamp;
* source/device;
* result.

---

## 50. Offline Reports

Authorized offline devices may access locally available report data according to their offline authorization.

Offline reports are not considered final authoritative report generation unless explicitly synchronized and validated by the server.

The server remains authoritative for finalized report versions.

---

## 51. Offline Report Data

Offline report data must:

* respect Branch scope;
* respect employee permissions;
* respect subscription bounds;
* identify its data state;
* avoid presenting stale data as newly finalized server data.

Where necessary, the UI must indicate that the report is based on local/offline state.

---

## 52. Subscription Expiry

When the Business enters read-only state:

* existing reports remain accessible according to permissions;
* report history remains available;
* allowed Excel exports remain available;
* new modifying operations are blocked.

Offline devices cannot bypass the read-only state.

---

## 53. Report Generation During Expiry

If subscription expiry occurs while a report generation operation is active:

* server entitlement rules determine whether the operation may complete;
* no report is treated as valid if the required operation is unauthorized;
* historical reports remain available.

The system must use server time and authoritative entitlement state.

---

## 54. Report Permissions

The permission model may distinguish:

* view reports;
* view Branch reports;
* generate reports;
* view report history;
* export reports;
* access sensitive reports;
* access audit reports.

Permissions are evaluated together with Business and Branch scope.

---

## 55. Sensitive Reports

Some reports may contain sensitive information such as:

* payroll;
* employee information;
* audit history;
* financial discrepancies.

Access must be explicitly permission-controlled.

---

## 56. Report Performance

Report generation must not block POS operations.

The system uses:

* synchronous processing for small/fast reports;
* background processing for heavy reports;
* isolated workers where required.

The POS must remain operational while heavy reports are generated.

---

## 57. Report Job Isolation

Heavy report generation, Excel export and historical recalculation should execute outside the main POS request path.

Worker failure must not affect committed POS transactions.

---

## 58. Report Concurrency and Source Data

Reports use consistent snapshots even when operational transactions continue.

A report generation operation must not partially include a transaction that was not fully committed.

Only committed authoritative data may enter the report snapshot.

---

## 59. Report and Transaction Boundaries

A committed core transaction may later affect a report.

Report generation is a secondary operation.

Therefore:

* POS transaction success does not depend on immediate report generation;
* report failure does not roll back the committed POS transaction;
* the report system records pending/retry state where required.

---

## 60. Report Regeneration

A report may be regenerated when:

* relevant source data changes;
* a previous generation failed;
* authorized manual regeneration is requested.

Regeneration must preserve the previous immutable versions.

---

## 61. Manual Regeneration

Manual regeneration requires appropriate permission.

The system must determine whether a new version is actually required.

If no relevant data changed, the system should not create an unnecessary new version merely because regeneration was requested.

---

## 62. Report Version Retention

Report versions must remain available according to the Business data lifecycle and configured retention rules.

A newer version does not automatically delete an older version.

---

## 63. Report and Data Deletion

When Business data enters permanent deletion:

* associated report data follows the Business deletion lifecycle;
* deletion is performed through the controlled data lifecycle process;
* deletion must not be reported as successful unless the operation actually completes.

Platform-level deletion audit remains separate where required.

---

## 64. Audit

Important report operations are audited, including:

* report generation;
* report regeneration;
* report failure;
* report retry;
* report version creation;
* report export;
* sensitive report access where configured;
* report correction linkage.

Audit events remain immutable.

---

## 65. Error Handling

Report errors are classified as:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

Technical details are kept in logs.

Users receive business-safe error messages.

---

## 66. Recovery

Report recovery relies on:

* idempotency;
* retry;
* background jobs;
* immutable versions;
* consistent snapshots;
* correction linkage;
* audit.

A failed report generation must not corrupt an existing valid Report Version.

---

## 67. System Invariants

The following invariants apply to Reports and Report Versioning:

1. Every report belongs to a Business context.
2. Branch-scoped reports identify their Branch.
3. Cross-Business report access is prohibited.
4. Logical report identity is based on Report Definition + Period + Scope.
5. Every Report Version has a stable UUID.
6. Report Versions are immutable.
7. A new version is created when relevant underlying data changes the report result.
8. A correction that does not affect report metrics does not require a new version.
9. Historical report versions remain accessible to authorized users.
10. Report generation uses a consistent transactional snapshot.
11. Only committed authoritative data enters finalized report snapshots.
12. Current client state is not authoritative for finalized reports.
13. Monthly reports use calendar-month boundaries.
14. Monthly report generation occurs on the last calendar day at the configured generation time.
15. Open applicable Cash Sessions prevent premature monthly report finalization.
16. Manual report periods cannot exceed one calendar month.
17. Invalid date ranges are rejected.
18. Valid empty periods still produce reports.
19. Report generation failures do not create valid completed reports.
20. Retryable report failures may be retried.
21. Retry count is bounded.
22. Failed report generation remains identifiable.
23. Duplicate generation of the same logical report operation is prevented.
24. Concurrent generation cannot create duplicate authoritative versions.
25. Report versions record creation reason.
26. Report versions identify their creator/source.
27. Corrections do not modify existing report versions.
28. Correction-driven report changes create new versions when relevant.
29. New versions retain links to relevant corrections.
30. Historical Product prices are used for historical reporting.
31. Historical Recipe Versions are used for historical inventory reporting.
32. Historical Payroll snapshots are used for historical payroll reporting.
33. Historical payment snapshots are used for payment reporting.
34. Historical refund data is preserved for refund reporting.
35. Historical discount snapshots are preserved for discount reporting.
36. Historical Cash Session state is preserved for cash reporting.
37. Historical attendance remains available for attendance reporting.
38. Report access requires Business scope validation.
39. Branch report access requires Branch authorization.
40. Sensitive reports require appropriate permission.
41. Excel export uses `.xlsx`.
42. Excel export represents the selected immutable Report Version.
43. Export does not recalculate historical data from current state.
44. Large exports may run as background jobs.
45. Export jobs are idempotent.
46. Export failures are recoverable.
47. Report downloads/exports may be audited according to policy.
48. Offline report access respects authorization.
49. Offline report data cannot bypass subscription restrictions.
50. Server remains authoritative for finalized reports.
51. Subscription expiry does not delete historical reports immediately.
52. Read-only access may continue according to subscription lifecycle rules.
53. Heavy report generation must not block POS operations.
54. Background report workers are isolated from core POS transactions.
55. Report failure does not roll back a committed core business transaction.
56. Report generation may continue independently from later operational transactions.
57. Manual regeneration does not automatically create a new version if no relevant data changed.
58. Report versions follow Business data lifecycle rules.
59. Deletion must not be reported as successful before actual completion.
60. Important report operations are audited.
61. Audit records are immutable.
62. Report generation is attributable to Employee or SYSTEM.
63. Report period boundaries are deterministic.
64. Report scope is preserved in every version.
65. Report snapshot context is preserved.
66. Historical report data cannot be silently overwritten.
67. Report corrections are traceable to their source changes.
68. Current configuration cannot reinterpret historical report versions.
69. Report generation must remain idempotent under request retry.
70. Report integrity has priority over generation convenience.
71. Report processing must not reduce normal POS availability.
72. Failed background workers can be safely retried.
73. A valid existing Report Version remains intact when a newer generation fails.
74. Report versions remain historically distinguishable even when their displayed values are identical.
75. The system must preserve enough historical information to reconstruct the report state represented by each version.

---

## 68. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 69. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `20_Reports_and_Report_Versioning.md`

**Next Document:** `21_Notifications_and_Alerts.md`

