# Report and Report Version Data Model

**Document ID:** DB-21
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/01_Database_Overview.md`

## 1. Purpose

This document defines the database model for reports and immutable report versions.

The model must support:

* operational reports;
* financial and cash reports;
* inventory reports;
* employee and payroll reports;
* audit and history reports;
* branch and business performance reports;
* automatic and manually generated reports;
* immutable historical report versions;
* correction-driven report regeneration;
* authorized XLSX export;
* report generation without blocking POS operations.

A report is a derived representation of system data.

A report version is a historical snapshot of a report result at a specific point in time.

Report data must never become the authoritative source for operational state.

---

# 2. Core Principles

The database model follows these principles:

1. Operational tables remain the source of truth.
2. Reports are derived from operational data.
3. A report definition and a report result are separate concepts.
4. Report versions are immutable.
5. A new relevant data change creates a new report version when required.
6. Previous report versions are never silently overwritten.
7. Report generation must not block core POS operations.
8. Report access is controlled by Business, Branch, employee, permission, and subscription scope.
9. Report generation is idempotent.
10. Historical reports must remain reconstructable.
11. Corrections must preserve the relationship between the original report and the affected correction.
12. Exporting a report does not modify the report itself.

---

# 3. Report Ownership

Every report belongs to a Business.

Conceptually:

```text
Business
    |
    +-- Report
          |
          +-- Report Version
```

A report may have one of two scopes:

* Business-level;
* Branch-level.

A branch-level report must reference its Branch.

A Business-level report may aggregate multiple branches if the requesting employee has access to those branches.

A report must never expose data outside the authorized Business.

---

# 4. Report Identity

Each logical report has a permanent UUID.

Suggested field:

```text
report.id UUID
```

Properties:

* globally unique;
* immutable;
* never reused;
* independent from report version;
* safe for synchronization and idempotency.

The report UUID identifies the logical report.

The report version UUID identifies one historical generation of that report.

---

# 5. Report Types

The database should support a controlled report type registry.

Examples:

```text
SALES
ORDERS
PAYMENTS
CASH_SESSION
CASHIER
CASH_DISCREPANCY
REFUND
DISCOUNT
INVENTORY
INVENTORY_MOVEMENT
INVENTORY_VARIANCE
PURCHASE
EMPLOYEE
ATTENDANCE
PAYROLL
BRANCH_PERFORMANCE
EXPENSE
AUDIT
CHANGE_HISTORY
SUBSCRIPTION
```

The system may add new report types later without changing the fundamental report model.

Arbitrary SQL report definitions are out of scope.

---

# 6. Report Scope

A report must explicitly identify its scope.

Suggested values:

```text
BUSINESS
BRANCH
```

For branch-level reports:

```text
branch_id != NULL
```

For Business-level reports:

```text
branch_id = NULL
```

A report requesting multiple selected branches may use a separate report scope/filter representation rather than pretending that the report belongs to one Branch.

---

# 7. Report Definition

A logical report should store stable metadata.

Conceptual fields:

```text
Report
---------
id
business_id
branch_id
report_type
scope
status
name
created_by_employee_id
created_at
updated_at
```

The exact physical schema may differ.

The report definition identifies what report is being generated.

It does not contain mutable historical result data.

---

# 8. Report Lifecycle

A report may use the following conceptual lifecycle:

```text
REQUESTED
    ↓
GENERATING
    ↓
READY
```

Exceptional states:

```text
FAILED
CANCELLED
```

For version generation:

```text
REQUESTED
    ↓
GENERATING
    ↓
READY
```

A failed generation must not create a valid report version.

A retry may create a new generation attempt.

---

# 9. Report Version Identity

Every generated report result receives a permanent UUID.

Suggested:

```text
report_version.id UUID
```

The version belongs to exactly one logical report.

Conceptually:

```text
Report
  |
  +-- Version 1
  |
  +-- Version 2
  |
  +-- Version 3
```

Each version is immutable after successful creation.

---

# 10. Report Version Number

Each report version should have a monotonically increasing version number.

Example:

```text
1
2
3
4
```

The version number is unique within the logical report.

It is not globally unique.

Conceptual constraint:

```text
UNIQUE(report_id, version_number)
```

Version numbers must never be reused.

---

# 11. Report Period

Reports must explicitly identify their covered period.

Suggested fields:

```text
period_start
period_end
```

The period must use timezone-aware timestamps where time precision is required.

For calendar-day reports, the Business or Branch timezone must determine the calendar boundaries.

The system must not interpret report periods using the server's local timezone.

---

# 12. Report Creation Source

The report version must identify how it was generated.

Suggested values:

```text
AUTOMATIC
MANUAL
CORRECTION
RETRY
SYSTEM
```

Examples:

* monthly automatic report;
* Owner manually requests a report;
* correction causes a new version;
* failed generation is retried.

---

# 13. Report Creation Reason

The report version should optionally store a reason.

Examples:

```text
MONTH_END
MANUAL_REQUEST
DATA_CORRECTION
PAYMENT_CORRECTION
INVENTORY_CORRECTION
CASH_CORRECTION
PAYROLL_CORRECTION
SYSTEM_RETRY
```

For manual or correction-driven reports, a human-readable reason may also be stored.

---

# 14. Data Snapshot Context

A report version must identify the data state from which it was generated.

Conceptual fields:

```text
data_snapshot_at
generated_at
```

Depending on the implementation, the system may additionally store:

```text
source_data_watermark
source_sequence
```

The exact mechanism is an implementation decision.

The important requirement is that the system can determine which operational state produced the report.

---

# 15. Consistent Report Snapshot

A report covering multiple domains must be generated from a consistent logical data snapshot.

For example:

```text
Orders
Payments
Cash Sessions
Inventory
```

must not represent unrelated points in time.

The generation mechanism should use a consistent database snapshot or equivalent controlled reporting strategy.

Long-running report generation must not hold business transactions open unnecessarily.

---

# 16. Report Result Storage

The system should distinguish report metadata from report result data.

Conceptually:

```text
Report
    |
    +-- Report Version
            |
            +-- Result Metadata
            +-- Result Data
```

For initial implementation, report result data may be stored as structured JSON where appropriate.

However, frequently queried operational data must not be replaced by JSON report storage.

Report result storage is for historical report output, not operational state.

---

# 17. Report Version Payload

A report version may contain:

```text
summary
sections
columns
rows
totals
metadata
```

Conceptually:

```text
report_version.result_data
```

The exact structure should be defined by the reporting layer.

The database must preserve the generated result sufficiently to reproduce the historical report view.

---

# 18. Report Data Format

Report result data must use a versioned internal format.

Suggested:

```text
result_schema_version
```

Example:

```text
1
```

This allows the application to evolve report payload structures without interpreting historical versions incorrectly.

A report generated under an older schema must remain readable.

---

# 19. Report Calculation Metadata

A report version may store calculation metadata such as:

```text
total_orders
total_sales
total_payments
total_refunds
total_discount
total_expense
```

The exact fields depend on the report type.

Calculated values must be treated as snapshots.

They must not be used to update operational tables.

---

# 20. Report Version Immutability

Once a report version reaches:

```text
READY
```

its result must never be edited in place.

No normal application operation may modify:

* result data;
* period;
* creator;
* creation source;
* version number;
* snapshot context.

If the result must change, a new report version must be created.

---

# 21. Correction-Driven Versioning

Corrections may change a previously generated report.

Example:

```text
Report Version 4
      ↓
Cash correction
      ↓
Report Version 5
```

Version 4 remains unchanged.

Version 5 contains the updated result.

The system should preserve the relationship between the correction and Version 5.

---

# 22. Source Correction Reference

A report version may reference the correction that caused its creation.

Suggested:

```text
source_correction_id
```

This may reference a domain-specific correction record or a generalized correction identity.

The relationship must allow audit reconstruction.

---

# 23. Previous Version Reference

A report version may reference its predecessor.

Suggested:

```text
previous_version_id
```

This creates a historical chain:

```text
Version 1
   ↓
Version 2
   ↓
Version 3
```

The chain must not be mutable.

---

# 24. No-Change Correction

Not every correction requires a new report version.

If a correction does not affect the report's covered data or calculation result, a new report version is not required.

The system must distinguish:

```text
Correction occurred
```

from:

```text
Report result changed
```

---

# 25. Report Generation Request

A report generation request should have a separate identity.

Suggested:

```text
report_generation_request.id UUID
```

This supports:

* idempotency;
* retries;
* background processing;
* failure recovery;
* duplicate prevention.

A generation request must reference the logical Report.

---

# 26. Generation Request Idempotency

A generation request must have an idempotency key.

Conceptually:

```text
idempotency_key
```

Repeated requests with the same logical identity must not create duplicate report versions unintentionally.

The uniqueness scope should include Business context.

---

# 27. Automatic Monthly Reports

The system generates the required monthly report at the end of the calendar month.

The report generation process must use the Business or Branch timezone.

If a required Cash Session is still open, the system must wait according to the defined report-generation rule.

The system must not generate a misleading final report from an incomplete cash state.

---

# 28. Manual Report Limits

Manual report requests are permission-controlled.

The current business rule allows a manual report period of at most one month.

Validation:

```text
period_start <= period_end
```

and:

```text
period_length <= configured maximum
```

The application must reject invalid periods before expensive generation begins.

---

# 29. Empty Reports

A valid report may contain zero operational records.

For example:

```text
No sales during the selected period.
```

The system should still create a valid report version.

An empty result is not a generation failure.

---

# 30. Report Permissions

Report access must be evaluated through:

```text
Employee
+
Effective Permissions
+
Branch Scope
+
Subscription Entitlement
```

The frontend must never be the authority for report authorization.

The server must validate access for:

* generation;
* viewing;
* version history;
* downloading;
* exporting.

---

# 31. Report Branch Isolation

A Branch-scoped employee must not access reports for unauthorized branches.

A Business-level report containing multiple branches must include only branches the requesting employee is authorized to see.

A report generated by one employee must not become a mechanism for bypassing branch permissions.

---

# 32. Report Subscription Rules

Subscription status affects report operations.

When a Business is active:

* authorized reports may be generated;
* report history may be viewed.

After subscription expiry:

* report generation requiring modification is blocked according to entitlement rules;
* existing reports remain viewable where permitted;
* allowed XLSX exports remain available.

After Business deletion:

* operational and report data are deleted according to the data lifecycle policy.

---

# 33. Report Export

The current export format is:

```text
.xlsx
```

PDF and CSV export are outside the current scope.

Exporting a report must not alter the report version.

The exported file is a representation of the immutable report version.

---

# 34. Export Audit

Report downloads and exports should be auditable where required.

Conceptual audit context:

```text
employee_id
business_id
branch_id
report_id
report_version_id
export_format
created_at
```

The export itself does not create a new report version.

---

# 35. Report Version Download

A user with permission may download a historical report version.

The system must always return the selected version.

It must not silently substitute the latest version.

Example:

```text
Requested Version 3
        ↓
Download Version 3
```

not:

```text
Requested Version 3
        ↓
Download Version 5
```

---

# 36. Report History

Users with sufficient permission may view:

* report identity;
* report type;
* period;
* version number;
* generation source;
* creation time;
* creator;
* version status;
* correction relationship.

Historical versions must remain distinguishable.

---

# 37. Report Status vs Version Status

Logical report state and report version state should not be confused.

For example:

```text
Report
  status = ACTIVE

Report Version
  status = READY
```

A report may remain active while multiple historical versions exist.

---

# 38. Report Failure

If generation fails:

```text
Report Version
```

must not be created as a valid READY version.

The generation request records the failure.

Suggested metadata:

```text
failure_code
failure_reason
failed_at
retry_count
```

Sensitive internal exception details should not be exposed directly to ordinary users.

---

# 39. Retry

Report generation must support controlled retry.

A retry must:

* preserve the original failed request;
* create a new attempt;
* remain idempotent;
* not corrupt existing versions;
* not overwrite successful versions.

---

# 40. Concurrent Generation

The system must prevent unintended duplicate generation.

Example:

```text
Manual request
+
Automatic request
```

for the same logical report period must be handled according to a deterministic idempotency rule.

The database should enforce uniqueness where appropriate.

---

# 41. Report Generation and POS

Report generation must not block:

* order acceptance;
* payment;
* cash session operations;
* inventory operations;
* shift handover.

Heavy report generation belongs to background processing.

Core POS transactions remain independent from report generation.

---

# 42. Reporting Read Strategy

Reports should primarily read from:

* operational tables;
* immutable historical tables;
* approved report snapshots.

The reporting layer must not modify operational data.

For heavy reports, the worker may generate a historical result asynchronously.

---

# 43. Report Data Consistency

Reports involving financial data must use authoritative sources.

For example:

```text
Sales Report
    → Accepted Orders
    → Completed Payments where applicable
    → Refunds
    → Discounts
```

The report must not infer financial truth from UI state.

---

# 44. Cash Reports

Cash reports may include:

* opening cash;
* cash sales;
* cash debt repayments;
* cash refunds;
* cash in/out;
* expected cash;
* actual cash;
* difference;
* correction transactions.

Closed Cash Sessions are historical financial records.

---

# 45. Inventory Reports

Inventory reports may include:

* opening quantity;
* purchases;
* sales consumption;
* production consumption;
* production output;
* returns;
* losses;
* shrinkage;
* adjustments;
* closing quantity.

The report must be based on Inventory Transactions and authoritative balances.

---

# 46. Payroll Reports

Payroll reports must reference finalized payroll calculations.

A report must not independently recalculate finalized payroll using current salary configuration.

Historical payroll configuration and calculation snapshots remain authoritative for that payroll period.

---

# 47. Audit Reports

Audit reports must read from immutable audit events.

They must preserve:

* actor;
* Business;
* Branch;
* device;
* cash session;
* transaction;
* event type;
* result;
* reason;
* timestamp.

Audit reports must not modify audit records.

---

# 48. Report Snapshot vs Operational Snapshot

The following concepts are different:

```text
Operational state
Report generation snapshot
Report version
```

Operational data may continue changing after a report is generated.

The report version remains unchanged.

---

# 49. Historical Reconstruction

The system should be able to answer:

```text
What did the report show at the time it was generated?
```

The answer must come from the stored report version.

It must not require rerunning the report against current data.

---

# 50. Report Version Comparison

The application may provide comparison between versions.

Example:

```text
Version 4
vs
Version 5
```

The database must preserve enough metadata to identify why the versions differ.

Detailed visual diffing is an application concern.

---

# 51. Report Metadata Snapshot

Where report interpretation depends on configuration, the version should preserve relevant metadata.

Examples:

* currency;
* timezone;
* report type;
* period;
* branch;
* calculation schema version;
* selected filters;
* relevant configuration version.

This prevents historical reports from being interpreted using unrelated current configuration.

---

# 52. Report Filters

A report version may store the filters used to generate it.

Examples:

```text
branch_ids
employee_ids
product_ids
payment_methods
order_types
```

Filters must be validated against the requesting employee's permissions.

Stored filters are historical metadata.

They do not grant future access.

---

# 53. Report Filter Security

A historical report containing unauthorized data must never become accessible merely because the current employee can guess its UUID.

Every read must revalidate:

```text
Business
+
Branch Scope
+
Permission
+
Subscription State
```

---

# 54. Report Ownership and Actor History

The report should preserve:

```text
created_by_employee_id
```

when a human initiated the generation.

System-generated reports may use:

```text
SYSTEM
```

as the generation actor.

If the employee later becomes inactive, the report remains valid.

---

# 55. Employee Snapshot

For historical readability, a report version may store relevant creator metadata such as:

```text
creator_name_snapshot
```

The authoritative employee record remains separate.

The snapshot exists to preserve historical context.

---

# 56. Report Version Timestamps

Use timezone-aware timestamps.

Important timestamps include:

```text
requested_at
started_at
generated_at
failed_at
```

The system should distinguish client time from server time where offline or distributed execution is involved.

Server time is authoritative for report lifecycle decisions.

---

# 57. Report Generation Source Data Watermark

For large systems, a report generation process may use a source watermark.

Conceptually:

```text
source_watermark
```

The watermark can identify the highest authoritative event or data sequence included in the report.

This supports:

* reproducibility;
* debugging;
* incremental processing;
* consistency validation.

The exact implementation is architecture-dependent.

---

# 58. Report Result Integrity

Stored result data must be protected from accidental modification.

Recommended mechanisms include:

* database permissions;
* application-level immutability;
* restricted update paths;
* audit logging;
* optional result checksum.

A checksum may be stored as:

```text
result_checksum
```

if useful for integrity verification.

---

# 59. Report Result Compression

Large historical report payloads may be compressed.

Compression is an implementation optimization.

It must not change the logical report version.

The system must still be able to retrieve and render the original result.

---

# 60. Large Report Handling

Very large reports must not be loaded entirely into memory by the API.

The system should support:

* background generation;
* streaming or controlled download;
* bounded worker memory;
* paginated report views where applicable.

The database model must not force an unnecessarily large single transaction.

---

# 61. Report Version Storage Strategy

The implementation may use:

```text
report_versions.result_data JSONB
```

for structured report results.

For very large outputs, the architecture may use a separate report artifact storage mechanism while keeping metadata in PostgreSQL.

The database must remain authoritative for report identity and version metadata.

---

# 62. Report Artifact Reference

If external or object storage is later introduced, the version may contain:

```text
artifact_storage_type
artifact_reference
artifact_checksum
```

The artifact must remain associated with exactly one report version.

Deleting or replacing an artifact must not change the report version identity.

---

# 63. Report Generation Job

Background processing should use a separate job identity.

Conceptually:

```text
Report Generation Request
        |
        v
Background Job
        |
        v
Report Version
```

The job must be retryable and observable.

---

# 64. Job and Report Idempotency

A worker retry must not create duplicate READY versions for the same generation request.

The system should use:

* generation request UUID;
* idempotency key;
* database uniqueness;
* transaction-safe version creation.

---

# 65. Report Version Creation Transaction

Creating a successful report version should be atomic.

Conceptually:

```text
BEGIN
    validate generation request
    determine next version number
    store report version
    mark generation request successful
COMMIT
```

If the transaction fails, no partially valid report version may remain.

---

# 66. Version Number Concurrency

Two workers must not create the same report version number.

The database must protect:

```text
(report_id, version_number)
```

using a unique constraint and appropriate transaction handling.

---

# 67. Report Period Uniqueness

Automatic reports may require a logical uniqueness rule such as:

```text
Business
+
Report Type
+
Period
+
Generation Policy
```

The exact uniqueness key depends on the report type.

Manual reports may intentionally generate multiple versions for the same period.

Therefore, uniqueness must not blindly prevent legitimate manual regeneration.

---

# 68. Report Configuration Version

If a report depends on configurable calculation rules, store the relevant configuration version.

Example:

```text
report_configuration_version
```

This supports historical interpretation when calculation logic changes.

---

# 69. Report Schema Version vs Business Configuration Version

These are different:

```text
result_schema_version
```

defines the structure of the stored result.

```text
configuration_version
```

defines the business configuration used for calculation.

They must not be confused.

---

# 70. Report and Audit Relationship

Important report operations should generate audit events.

Examples:

* report generation;
* report download;
* report export;
* report version creation;
* report generation failure;
* authorized report access;
* report correction-driven regeneration.

Audit data remains separate from report data.

---

# 71. Report and Notification Relationship

Report failures may create notifications for authorized users.

Examples:

```text
Monthly report generation failed.
```

Notification failure must not roll back report data.

Report generation failure and notification failure are separate failure domains.

---

# 72. Report and Subscription Relationship

Report operations must use current entitlement.

Historical report versions remain historical data.

Subscription expiry must not rewrite or delete report versions immediately.

Deletion occurs only according to the Business data lifecycle.

---

# 73. Report and Data Deletion

When a Business enters permanent deletion:

* report metadata is deleted according to lifecycle policy;
* report versions are deleted;
* report artifacts are deleted;
* report generation jobs are cancelled or invalidated;
* pending report requests cannot recreate the deleted Business.

Stale background jobs must not resurrect report data.

---

# 74. Report and Synchronization

Offline devices may locally display authorized reports.

However:

* finalized server reports are authoritative;
* offline-created operational data must synchronize before becoming part of server reports;
* stale local report data must not overwrite server versions.

Report synchronization is secondary to operational transaction synchronization.

---

# 75. Offline Report Generation

Offline report generation may be allowed for limited authorized views.

Offline reports must be explicitly marked as local/non-final where required.

They must not be presented as authoritative finalized server reports.

---

# 76. Report Access After Subscription Expiry

After subscription expiry:

```text
Modify
    → blocked

View historical reports
    → allowed where policy permits

Export XLSX
    → allowed where policy permits
```

The exact entitlement remains server-authoritative.

---

# 77. Report Access After Employee Deactivation

An inactive employee cannot normally generate new reports.

Historical reports created by that employee remain valid.

Access to existing reports is determined by the employee's current permissions and scope.

---

# 78. Report Access After Branch Deactivation

Deactivating a Branch must not delete its historical reports.

Historical branch reports remain available to authorized users.

New operational reports for an inactive Branch are blocked unless explicitly allowed by system policy.

---

# 79. Report Indexing

Recommended indexes include:

```text
reports(business_id, report_type)
reports(business_id, branch_id, report_type)
report_versions(report_id, version_number)
report_versions(report_id, generated_at)
report_versions(business_id, period_start, period_end)
report_generation_requests(business_id, status)
report_generation_requests(idempotency_key)
```

Exact indexes should be validated against production query patterns.

---

# 80. Tenant Isolation Constraints

Every report-related table must preserve Business ownership.

Conceptually:

```text
report.business_id
report_version.business_id
generation_request.business_id
```

must agree.

Where Branch is present:

```text
branch.business_id = report.business_id
```

must be enforced.

Cross-Business references are prohibited.

---

# 81. Foreign Key Strategy

Recommended relationships:

```text
Report.business_id
    → Business.id

Report.branch_id
    → Branch.id

Report.created_by_employee_id
    → Employee.id

ReportVersion.report_id
    → Report.id

ReportVersion.previous_version_id
    → ReportVersion.id

GenerationRequest.report_id
    → Report.id
```

Historical references must not be broken by ordinary employee deactivation.

Where permanent deletion is required by Business lifecycle, deletion must follow the controlled dependency graph.

---

# 82. Database Constraints

Important constraints include:

```text
report.id UNIQUE
report_version.id UNIQUE
(report_id, version_number) UNIQUE
```

Additional checks:

```text
period_start <= period_end
```

Branch scope:

```text
scope = BRANCH → branch_id IS NOT NULL
scope = BUSINESS → branch_id IS NULL
```

A report version must belong to the same Business as its Report.

---

# 83. Monetary and Numeric Values

Report financial values should use exact decimal types.

Do not use floating-point types for authoritative monetary values.

Quantities should use the same exact decimal conventions as Inventory.

Report values are derived from authoritative monetary and quantity fields.

---

# 84. Currency

Business currency must be captured in the report context where financial interpretation requires it.

A historical report must not silently switch to a future Business currency configuration.

---

# 85. Timezone

Report calendar periods must use the relevant Business or Branch timezone.

For example:

```text
23:59 Branch local time
```

must not be interpreted using UTC or server local time without explicit conversion.

---

# 86. Pagination

Report history queries must use deterministic pagination.

Recommended ordering:

```text
generated_at DESC
version_number DESC
id DESC
```

A stable unique tie-breaker should be included.

Large report result sets should use bounded pagination.

---

# 87. Report Query Performance

Report queries must avoid unnecessary joins and repeated recalculation.

Heavy calculations should run in background workers.

The POS request path must not execute expensive historical report generation.

---

# 88. Caching

Report results may be cached for read performance.

Cache entries must never become the source of truth.

Cache keys must include Business and report version identity.

Example:

```text
report:{business_id}:{report_version_id}
```

Cached data must be invalidated or naturally expire when appropriate.

---

# 89. Report Version Retention

Report versions follow Business data lifecycle rules.

They should not be deleted merely because a newer version exists.

Historical versions are retained until the Business reaches permanent deletion or an explicitly approved retention policy applies.

---

# 90. Report Archival

For very large systems, old report versions may be moved to archival storage.

Archival must preserve:

* report UUID;
* version UUID;
* version number;
* period;
* result integrity;
* creation metadata;
* correction relationship.

Archival must not change historical meaning.

---

# 91. Report Restoration

If archived report data is restored, its original:

* Report UUID;
* Report Version UUID;
* version number;
* period;
* timestamps

must remain unchanged.

Restoration must be idempotent.

---

# 92. Report Security

Report data may contain sensitive business information.

Access must be restricted by:

* Business;
* Branch;
* Employee;
* Permission;
* Subscription;
* report type.

Report result payloads must not contain unnecessary credentials, secrets, authentication tokens, or unrelated personal data.

---

# 93. Report Generation Authorization

The server must validate authorization immediately before generation.

A previously valid UI request must not remain authorized indefinitely.

For background generation, the job must retain sufficient authorization context to verify that the requested report remains permitted.

---

# 94. Report Generation and Employee Changes

If an employee loses permission while a report job is pending, the system must apply the defined authorization policy.

For security-sensitive reports, the worker should revalidate authorization before producing the final report.

---

# 95. Report Generation and Subscription Changes

If a subscription expires while a report job is pending, the worker must evaluate current entitlement.

The system must not allow background processing to bypass subscription restrictions.

Already-created historical report versions remain governed by historical integrity and lifecycle rules.

---

# 96. Suggested Logical Tables

The database model should conceptually support:

```text
reports
report_versions
report_generation_requests
```

Optional later structures:

```text
report_artifacts
report_export_records
```

The exact physical schema may evolve during implementation.

---

# 97. Suggested `reports` Fields

Conceptual fields:

```text
id
business_id
branch_id
report_type
scope
name
status
created_by_employee_id
created_at
updated_at
```

Optional:

```text
description
```

---

# 98. Suggested `report_versions` Fields

Conceptual fields:

```text
id
report_id
business_id
branch_id
version_number
status
period_start
period_end
creation_source
creation_reason
created_by_employee_id
creator_name_snapshot
generated_at
data_snapshot_at
result_schema_version
configuration_version
result_data
result_checksum
previous_version_id
source_correction_id
created_at
```

The exact field set depends on implementation.

---

# 99. Suggested `report_generation_requests` Fields

Conceptual fields:

```text
id
business_id
report_id
requested_by_employee_id
request_source
idempotency_key
status
period_start
period_end
requested_at
started_at
completed_at
failed_at
retry_count
failure_code
failure_reason
created_at
updated_at
```

---

# 100. Database Invariants

The following invariants are mandatory:

1. Every Report belongs to exactly one Business.
2. Every Report Version belongs to exactly one Report.
3. Every Report Version has a permanent UUID.
4. Report UUIDs are never reused.
5. Report Version UUIDs are never reused.
6. Version numbers are unique within a Report.
7. Version numbers are never reused.
8. READY Report Versions are immutable.
9. A failed generation cannot produce a READY version.
10. A Report Version cannot reference a different Business.
11. A Branch-scoped Report must reference a Branch.
12. A Business-scoped Report must not require a Branch.
13. A Branch must belong to the same Business as its Report.
14. Report periods cannot have `period_start > period_end`.
15. Report access is permission-controlled.
16. Report access is Business-scoped.
17. Report access is Branch-scoped where applicable.
18. Subscription entitlement is checked by the server.
19. Frontend state cannot authorize report access.
20. Historical reports cannot bypass current access controls.
21. Historical versions remain distinguishable.
22. Previous versions are not overwritten.
23. A correction affecting a report may create a new version.
24. A correction not affecting a report does not require a new version.
25. Correction-driven versions retain correction context.
26. Version chains cannot contain circular references.
27. Report generation requests have stable identity.
28. Generation requests support idempotency.
29. Worker retries cannot create unintended duplicate versions.
30. Automatic report generation is deterministic for its logical period.
31. Manual reports may generate multiple versions when explicitly requested.
32. Empty reports are valid reports.
33. Empty reports are not treated as failures.
34. Report exports do not modify report versions.
35. Downloading an older version returns that exact version.
36. Report generation must not block POS transactions.
37. Heavy report generation is background work.
38. Report results are derived data.
39. Operational tables remain authoritative.
40. Report results cannot update operational state.
41. Financial reports use authoritative financial data.
42. Inventory reports use authoritative inventory data.
43. Payroll reports use finalized payroll snapshots.
44. Audit reports use immutable audit events.
45. Report period timezone is explicit.
46. Business or Branch timezone determines calendar boundaries.
47. Server time is authoritative for report lifecycle.
48. Historical report timestamps remain unchanged.
49. Report metadata remains historically reconstructable.
50. Report schema versions identify result structure.
51. Business configuration versions identify calculation context where required.
52. Report result integrity can be validated.
53. Sensitive credentials must never be stored in report payloads.
54. Report payloads must minimize unnecessary personal data.
55. Cache is never the authoritative report source.
56. Cache keys include Business scope.
57. Cache keys identify Report Version.
58. Cross-Business report references are forbidden.
59. Cross-Branch unauthorized access is forbidden.
60. Inactive employees cannot automatically gain report access.
61. Deactivated employees remain valid historical creators.
62. Deactivated branches retain historical reports.
63. Subscription expiry does not immediately delete historical reports.
64. Subscription expiry cannot be bypassed by background jobs.
65. Business deletion eventually removes report data.
66. Stale report jobs cannot recreate deleted Business data.
67. Report artifacts belong to a specific Report Version.
68. Artifact restoration preserves original identity.
69. Report history is ordered deterministically.
70. Report history pagination is bounded.
71. Version creation is transactionally consistent.
72. Version number allocation is concurrency-safe.
73. Duplicate generation is prevented where logically required.
74. Report failure state is observable.
75. Retry state is observable.
76. Failed generations preserve failure metadata.
77. Successful versions are not overwritten by retries.
78. Report generation authorization is validated.
79. Report generation entitlement is validated.
80. Report downloads may be audited.
81. Report exports may be audited.
82. Report generation may produce notifications without making notifications transactional with the report.
83. Notification failure cannot invalidate a successful report.
84. Report generation failure cannot corrupt operational data.
85. Report data must remain historically stable.
86. Report version comparison must use immutable versions.
87. Report filters are historical metadata.
88. Stored filters never grant authorization.
89. Offline report data cannot overwrite authoritative server reports.
90. Server-finalized reports are authoritative.
91. Operational synchronization precedes authoritative reporting where required.
92. Report generation must respect Business lifecycle.
93. Report generation must respect Branch lifecycle.
94. Report generation must respect Employee lifecycle.
95. Report generation must respect Subscription lifecycle.
96. Report result numeric values use exact types.
97. Financial report values preserve currency context.
98. Report schema evolution must preserve historical readability.
99. Report lifecycle operations must be auditable where required.
100. Report data must remain consistent with the system's historical integrity model.

---

# Related Documents

* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`

