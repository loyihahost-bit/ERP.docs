# Reporting and Export Architecture

**Document ID:** BA-12
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the backend architecture for Reports and Export operations in FastFood ERP.

The architecture must provide:

* reliable operational reports;
* historical report integrity;
* Business and Branch scoped reporting;
* permission-aware report access;
* immutable report versions;
* monthly automatic reports;
* manual reports;
* XLSX export;
* asynchronous export processing;
* secure report file access;
* correction-aware report versioning;
* efficient report generation;
* auditability.

Reports are considered derived business information.

The authoritative source remains the underlying transactional data and immutable historical snapshots.

---

## 2. Scope

This document covers:

* report architecture;
* report definitions;
* report parameters;
* report query layer;
* operational reports;
* historical reports;
* report versions;
* report snapshots;
* monthly reports;
* manual reports;
* Branch and Business scope;
* authorization;
* XLSX export;
* export jobs;
* file storage;
* report generation;
* report recalculation;
* corrections;
* report idempotency;
* report concurrency;
* report performance;
* report caching;
* audit;
* subscription restrictions;
* offline limitations;
* error handling;
* recovery;
* testing;
* system invariants.

This document does not define individual business report formulas in detail.

Individual report definitions belong to the appropriate Business/System Analysis documents.

---

# 3. Reporting Principles

The reporting architecture follows these principles:

1. Transactional data is authoritative.
2. Historical reports must remain reproducible.
3. Report versions are immutable.
4. Current reports must not rewrite historical reports.
5. Business and Branch scope must always be enforced.
6. Report access requires authorization.
7. Report generation must not block POS operations.
8. XLSX generation must run asynchronously for expensive operations.
9. Export files must be protected by authorization.
10. Report caching must never become the source of truth.
11. Corrections must create new report state where required.
12. Empty reports are valid reports.
13. Report generation must be idempotent where retries are possible.
14. Report periods must be deterministic.
15. Timezone handling must be explicit.
16. Report generation must not modify transactional data.

---

# 4. Reporting Architecture

The reporting flow is:

```text
API
  ↓
Report Application Service
  ↓
Authorization + Scope Validation
  ↓
Report Definition
  ↓
Report Query Layer
  ↓
Transactional Data / Historical Snapshots
  ↓
Report Result
  ↓
Report Version
  ↓
Export Job
  ↓
XLSX Generator
  ↓
File Storage
  ↓
Authorized Download
```

The API layer must remain thin.

Report business behavior belongs to the Application/Reporting layer.

---

# 5. Reporting Layers

The reporting subsystem consists of:

```text
API
 ↓
Application Reporting Service
 ↓
Report Definition
 ↓
Report Query
 ↓
Report Builder
 ↓
Report Version
 ↓
Export Service
 ↓
File Storage
```

Each layer has a distinct responsibility.

---

# 6. Report API Layer

The API layer is responsible for:

* authentication;
* request parsing;
* parameter validation;
* request context creation;
* calling Application services;
* returning report results or job information.

The API layer must not:

* construct complex SQL;
* calculate business totals;
* determine Branch scope;
* bypass permissions;
* create report files directly;
* modify report versions directly.

---

# 7. Report Application Layer

The Application layer coordinates report operations.

Typical use cases include:

```text
GenerateReport
GetReport
CreateReportVersion
GenerateMonthlyReport
RequestReportExport
GetExportStatus
DownloadReportExport
```

The Application layer is responsible for:

* authorization;
* scope resolution;
* period validation;
* report definition selection;
* query execution;
* version handling;
* export job creation;
* audit;
* transaction boundaries where required.

---

# 8. Report Definition

A Report Definition describes how a report behaves.

A definition may contain:

* report type;
* report name;
* supported scope;
* supported period;
* required permissions;
* supported filters;
* data source;
* calculation rules;
* output columns;
* export format;
* versioning behavior.

Example:

```text
Cash Session Report

Scope:
Business / Branch

Period:
Calendar period

Filters:
Branch
Cashier
Cash Register
Cash Session

Output:
Opening Cash
Sales
Payments
Refunds
Discrepancies
Closing Cash
```

Report definitions should be represented explicitly rather than scattered across API handlers.

---

# 9. Report Types

Reports may be categorized as:

### 9.1. Operational Reports

Reports used for current operational work.

Examples:

* current cash session;
* today's orders;
* current inventory;
* active employees;
* current Branch performance.

Operational reports may use current transactional state.

### 9.2. Historical Reports

Reports representing a completed or historical period.

Examples:

* monthly Branch report;
* historical cash report;
* historical payroll report;
* historical inventory report.

Historical reports must use the appropriate historical transactional information.

### 9.3. Versioned Reports

Some reports require immutable stored versions.

Examples:

* monthly automatic report;
* manually generated financial report;
* corrected report;
* exported report associated with a specific report version.

---

# 10. Report Scope

Every report must define its supported scope.

Possible scopes:

```text
Business
Branch
Employee
Cashier
Cash Register
Cash Session
Product
Inventory
Payroll
Order
```

The report service must validate that the requested scope belongs to the authenticated Business.

---

# 11. Business Isolation

A report query must never return data belonging to another Business.

Business isolation must be enforced at the server side.

The client-provided:

```text
business_id
branch_id
```

must never be treated as sufficient authorization.

The effective Business and Branch scope must come from the authenticated request context and authorization layer.

---

# 12. Branch Scope

Branch-scoped reports must validate:

* employee Branch authority;
* requested Branch;
* employee status;
* permission;
* subscription entitlement.

An employee authorized for Branch A must not retrieve Branch B data.

All-Branch authority may permit Business-level reporting where explicitly allowed.

---

# 13. Permission Model

Report access follows the general authorization model:

```text
Authentication
    ↓
Employee Status
    ↓
Business Context
    ↓
Lifecycle
    ↓
Branch Scope
    ↓
Permission
    ↓
Subscription Entitlement
    ↓
Report Access
```

Example permissions may include:

```text
REPORT_VIEW
REPORT_EXPORT
REPORT_VIEW_FINANCIAL
REPORT_VIEW_INVENTORY
REPORT_VIEW_PAYROLL
REPORT_VIEW_AUDIT
REPORT_GENERATE_MANUAL
```

The exact permission names may be refined during implementation.

---

# 14. Subscription Entitlement

Report access is subject to subscription state.

When subscription expires:

* existing reports remain viewable;
* historical report versions remain available;
* permitted exports remain available;
* report modification operations are blocked where applicable;
* new modifying configuration is blocked.

Read-only subscription state must not prevent legitimate access to historical business data.

---

# 15. Report Parameters

Reports must use explicit parameters.

Typical parameters include:

```text
business_id
branch_id
period_start
period_end
employee_id
cashier_id
cash_session_id
product_id
category_id
```

Parameters must be:

* validated;
* normalized;
* authorization-checked;
* deterministic.

Invalid parameters must produce validation errors.

---

# 16. Reporting Periods

Each report must define its allowed period.

The current business requirement is:

* automatic monthly reports use a calendar month;
* manual reports may cover at most one month;
* smaller periods are allowed where the report supports them.

A manual report request covering more than one month must be rejected.

Example:

```text
01 March → 31 March
```

is valid.

```text
01 January → 31 March
```

is invalid for a manual report if the report has the one-month restriction.

---

# 17. Calendar Boundaries

Calendar calculations must use the Business/Branch timezone where applicable.

The backend must not interpret business reporting periods using the server's local timezone.

Example:

```text
Business timezone: Asia/Tashkent

March 1 00:00
        ↓
March 31 23:59:59
```

The exact implementation should use half-open intervals where possible:

```text
[start, end)
```

For example:

```text
2026-03-01 00:00:00
        →
2026-04-01 00:00:00
```

This avoids boundary ambiguity.

---

# 18. Report Query Layer

Report queries must be separated from ordinary transactional commands.

The reporting query layer is responsible for:

* selecting required data;
* joining relevant entities;
* aggregating data;
* applying report filters;
* applying Business/Branch scope;
* returning report-ready data.

Report queries must not mutate business state.

---

# 19. Reporting Read Model

Initially, reporting uses the primary PostgreSQL database.

A separate reporting database is not required for the initial architecture.

The architecture must nevertheless keep reporting queries isolated behind a reporting abstraction so that a read replica or dedicated reporting store can be introduced later.

---

# 20. Report Query Safety

Report queries must:

* always apply Business scope;
* apply Branch scope where required;
* use parameterized queries;
* avoid unbounded queries;
* use appropriate indexes;
* avoid unnecessary entity loading;
* avoid N+1 query patterns;
* use aggregation in the database where appropriate.

Large report queries must not load unnecessary transactional entities into application memory.

---

# 21. Report Builder

The Report Builder converts query results into a stable report representation.

Example:

```text
ReportResult
├── report_type
├── business_id
├── branch_scope
├── period
├── generated_at
├── rows
├── totals
└── metadata
```

The Report Builder must not modify source transactional records.

---

# 22. Report Result

A report result should contain enough metadata to identify:

* report type;
* Business;
* Branch;
* period;
* generation time;
* report version where applicable;
* source state;
* generated by;
* filters.

The report result must be deterministic for the same authoritative data state and parameters.

---

# 23. Empty Reports

A report with no matching records is a valid report.

For example:

```text
March 2026
Orders: 0
Sales: 0
Refunds: 0
```

The system must not treat this as an error.

An empty report may still be versioned and exported.

---

# 24. Report Version

A report version represents an immutable generated state of a report.

A version should contain:

```text
report_version_id
report_type
business_id
branch_id
period_start
period_end
created_at
created_by
generation_reason
source_state
version_number
status
```

The exact database structure is defined by the Database Report Data Model.

---

# 25. Report Version Immutability

Once a report version is committed:

* its data must not be modified;
* its period must not change;
* its source identity must not change;
* its creator must not change.

If the underlying business data changes in a way that affects the report, a new version must be created.

---

# 26. Report Versioning Rule

The system must not create a new version merely because a user opens or views a report.

A new version is created when:

* relevant source data changes;
* a correction changes report results;
* a new automatic period closes;
* an authorized manual generation creates a new report state;
* an explicit regeneration is required.

---

# 27. Report Generation Reason

Every stored report version must have a reason.

Examples:

```text
MONTHLY_AUTO_GENERATION
MANUAL_GENERATION
CORRECTION
REGENERATION
SYSTEM_RECOVERY
```

This reason must be auditable.

---

# 28. Historical Report Integrity

Historical reports must not be recalculated from current configuration when doing so would change historical meaning.

Examples:

* current Product price must not rewrite historical sales;
* current Recipe must not rewrite historical inventory deductions;
* current Branch price must not rewrite old Orders;
* current employee role must not rewrite historical payroll;
* current category must not rewrite historical transaction identity.

Reports must use historical transaction snapshots where required.

---

# 29. Report and Correction

When a correction affects a report:

```text
Original Report Version
        ↓
Correction
        ↓
New Report Version
```

The original version remains immutable.

The new version must identify the previous version where appropriate.

---

# 30. Monthly Automatic Reports

The system generates monthly reports automatically.

The automatic report period is the previous completed calendar month.

Example:

```text
March 2026
    ↓
April report generation
```

The automatic process must not generate an incomplete month.

---

# 31. Monthly Report Trigger

Monthly report generation may be initiated by a scheduled background job.

The scheduler must identify completed Business/Branch periods.

The generation operation must be idempotent.

Repeated scheduler execution must not create duplicate authoritative report versions for the same generation event.

---

# 32. Manual Reports

Authorized employees may request manual reports.

Manual reports:

* validate period;
* validate scope;
* validate permissions;
* use current authoritative data;
* may create a new report version where versioning is required.

The maximum manual report period is one calendar month.

---

# 33. Report Regeneration

Report regeneration must not delete the old report version.

Instead:

```text
Version 1
   ↓
Regeneration
   ↓
Version 2
```

Version 1 remains accessible according to retention and lifecycle rules.

---

# 34. Report Snapshot

A report version must identify the source state from which it was generated.

The snapshot may include:

* source timestamp;
* transaction state;
* relevant configuration version;
* report query version;
* report definition version.

This allows the system to explain why a historical report contains specific values.

---

# 35. Report Definition Version

If report calculation logic changes significantly, the report definition itself should be versioned.

Example:

```text
Report Definition v1
       ↓
Calculation change
       ↓
Report Definition v2
```

Existing report versions remain associated with the definition version under which they were generated.

---

# 36. Report Calculation Version

The backend should record the calculation/report-definition version used to generate important historical reports.

This prevents a future code change from making an old report appear to have been generated using new calculation rules.

---

# 37. Export Architecture

XLSX export is asynchronous for reports that may require non-trivial processing.

The flow is:

```text
User
 ↓
Request Export
 ↓
Authorization
 ↓
Create Export Job
 ↓
Commit
 ↓
Background Worker
 ↓
Generate Report Data
 ↓
Generate XLSX
 ↓
Store File
 ↓
Update Export Status
 ↓
User Downloads File
```

---

# 38. Export Job

An Export Job should contain:

```text
export_job_id
report_type
report_version_id
business_id
branch_id
requested_by
format
status
created_at
started_at
completed_at
file_id
error_code
operation_id
```

Possible statuses:

```text
PENDING
PROCESSING
COMPLETED
RETRYING
FAILED
CANCELLED
```

---

# 39. Export Idempotency

Export requests must support idempotency.

A retry with the same operation UUID must not create multiple logically identical export jobs.

The system may return the existing job/result when an identical idempotent request is received.

---

# 40. Export Job Transaction

Creating an export job is a short database transaction.

The transaction should:

1. validate authorization;
2. validate report/version;
3. create export job;
4. create required outbox event;
5. commit.

XLSX generation must occur after the transaction commits.

---

# 41. XLSX Generation

The XLSX generator is responsible for:

* formatting columns;
* creating worksheets;
* writing report data;
* writing totals;
* applying safe formatting;
* generating the final file.

The generator must not modify business data.

---

# 42. XLSX File Structure

A report export may contain:

```text
Sheet 1:
Summary

Sheet 2:
Details

Sheet 3:
Totals / Statistics
```

The exact worksheet structure belongs to the individual report definition.

---

# 43. File Storage

Generated files must be stored through a storage abstraction.

The reporting system must not depend directly on a particular storage provider.

Possible storage implementations include:

```text
Local Storage
Object Storage
S3-Compatible Storage
```

The storage implementation is an infrastructure concern.

---

# 44. File Metadata

Each exported file should have metadata:

```text
file_id
business_id
report_version_id
export_job_id
filename
content_type
size
storage_key
created_at
expires_at
created_by
checksum
```

The exact retention policy is defined by lifecycle requirements.

---

# 45. File Access Security

A user must never be able to download an export merely by knowing its file ID.

Download authorization must validate:

* employee identity;
* Business scope;
* Branch scope;
* report permission;
* file ownership/scope;
* file state.

Storage keys must not be treated as authorization credentials.

---

# 46. Export Filename

Export filenames should be deterministic and human-readable.

Example:

```text
cash-report-branch-a-2026-03.xlsx
```

The filename must not contain sensitive credentials, tokens, or internal security data.

---

# 47. Export Download

The download flow is:

```text
Authenticate
   ↓
Authorize
   ↓
Validate Export Job
   ↓
Validate File
   ↓
Retrieve File
```

Large files should preferably be streamed or delivered through a controlled storage mechanism.

---

# 48. Export Expiration

Export files may have an expiration time.

After expiration:

* the file may be deleted;
* the report version remains available;
* the user may request a new export if permitted.

Deleting an export file must not delete the report version.

---

# 49. Export Audit

Important export operations must be audited.

Audit context should include:

```text
Event UUID
Business UUID
Branch UUID
Employee UUID
Device UUID
Report Version UUID
Export Job UUID
File UUID
Timestamp
Result
```

The audit record must not store sensitive file contents.

---

# 50. Background Processing

Report generation and export jobs use the background job architecture.

The worker must:

* claim pending jobs safely;
* process one job;
* update status;
* retry transient failures;
* record permanent failures;
* avoid duplicate processing.

Workers must not hold database transactions while generating large XLSX files.

---

# 51. Worker Transaction Boundaries

The worker should use short transactions for:

```text
claim job
update processing state
save result
save failure
```

The actual XLSX generation runs outside the database transaction.

This prevents long-running file generation from holding database locks.

---

# 52. Retry Policy

Temporary failures may be retried.

Examples:

* temporary storage failure;
* temporary database connection failure;
* worker interruption.

Permanent failures must not be retried indefinitely.

Examples:

* invalid report definition;
* missing required source data;
* corrupted configuration;
* unsupported export format.

Retries must be bounded.

---

# 53. Export Concurrency

Multiple users may request exports simultaneously.

The system must prevent:

* duplicate processing of the same idempotent job;
* two workers processing the same job;
* conflicting updates to export status.

Job claiming must use safe concurrency control.

---

# 54. Report Concurrency

Reports may be generated while transactions are occurring.

The reporting system must use a consistent database state appropriate for the report.

For reports requiring historical consistency, immutable transaction snapshots and report versions must be preferred over attempting to freeze the entire Business.

The system must not lock an entire Branch merely to generate a report.

---

# 55. Report Generation and POS

Report generation must not block normal POS operation.

The system must avoid:

* long write transactions;
* broad table locks;
* unnecessary row locks;
* synchronous XLSX generation inside API requests.

POS transactions remain the priority for operational performance.

---

# 56. Reporting Performance

Reporting queries must use appropriate indexes.

Potential indexed fields include:

```text
business_id
branch_id
created_at
order_date
payment_date
cash_session_id
employee_id
product_id
status
```

Exact indexes are defined in:

`26_Database_Indexes_and_Query_Strategy.md`

---

# 57. Large Reports

Large reports should be processed asynchronously.

The system must avoid loading the entire dataset into memory when unnecessary.

Streaming or chunked processing may be used for large exports.

Export limits must be explicit rather than relying on accidental infrastructure limits.

---

# 58. Report Cache

Caching may be used for frequently requested reports.

However:

**Cache is not authoritative.**

A cached report must always be associated with:

* Business;
* Branch;
* report parameters;
* report definition version;
* relevant data/version state.

Invalid or stale cache entries must be safely discarded.

---

# 59. Cache Invalidation

When relevant source data changes:

* affected cached report data may be invalidated;
* immutable report versions remain unchanged;
* new report generation may produce a new version.

Cache invalidation failure must not corrupt authoritative report data.

---

# 60. Read Replica

A PostgreSQL read replica may be introduced in the future for heavy reporting workloads.

The architecture should allow:

```text
Primary DB
   ↓
Transactional Operations

Read Replica
   ↓
Heavy Reporting Queries
```

However, a read replica must not be used for operations requiring immediate authoritative consistency unless replication guarantees are sufficient.

---

# 61. Reporting and Offline Mode

Offline devices may continue creating operational transactions.

They do not generate authoritative historical Business reports independently.

Offline devices may display locally available operational information where explicitly supported.

Authoritative report generation occurs after server synchronization.

---

# 62. Offline Transactions and Reports

Example:

```text
Offline Order
    ↓
Local transaction
    ↓
Synchronization
    ↓
Server validation
    ↓
Authoritative transaction
    ↓
Report becomes eligible for server reporting
```

A local device must not claim that an unsynchronized transaction is already part of an authoritative server report.

---

# 63. Report and Synchronization

Synchronization must preserve transaction snapshots.

If an offline Order contains:

```text
Price Version A
```

and the server currently uses:

```text
Price Version B
```

the historical Order remains associated with Version A.

Reports must use the authoritative synchronized transaction snapshot.

---

# 64. Report and Subscription Expiry

When a Business becomes read-only:

* existing reports remain accessible;
* existing report versions remain immutable;
* allowed exports remain available;
* new modifying operations are blocked;
* report generation must respect lifecycle restrictions.

If report generation is still allowed during read-only state, it must not modify transactional Business data.

---

# 65. Report and Business Deletion

When a Business enters deletion lifecycle:

```text
ACTIVE
 ↓
READ_ONLY
 ↓
DELETION_ELIGIBLE
 ↓
DELETING
 ↓
DELETED
```

New report generation must be restricted according to lifecycle policy.

During deletion:

* report files are deleted according to lifecycle rules;
* report versions are deleted according to retention policy;
* audit/history follows the defined deletion policy;
* backups may retain data according to backup retention rules.

---

# 66. Report Security

Reports may contain sensitive business information.

Therefore:

* authorization is mandatory;
* Business isolation is mandatory;
* Branch scope is mandatory where applicable;
* export access is audited;
* storage access is controlled;
* file URLs/tokens must be short-lived where used;
* sensitive information must not appear in logs.

---

# 67. Report Logging

Application logs may include:

```text
request_id
operation_id
report_type
business_id
branch_id
report_version_id
export_job_id
duration
status
```

Logs must not contain:

* passwords;
* tokens;
* storage credentials;
* private file contents;
* unnecessary sensitive financial details.

---

# 68. Report Metrics

The system should measure:

```text
report_generation_duration
report_generation_count
report_generation_failure_count
export_job_duration
export_job_failure_count
export_retry_count
report_query_duration
report_cache_hit
report_cache_miss
```

Metrics must support identifying slow report definitions.

---

# 69. Report Failure Isolation

A failed report must not roll back an unrelated committed transaction.

For example:

```text
Order accepted
    ↓
Transaction committed
    ↓
Report generation fails
```

The Order remains committed.

The report job may be retried independently.

---

# 70. Report Recovery

If report generation fails:

1. mark job as failed/retryable;
2. record failure reason;
3. retry when safe;
4. create a new report version only after successful generation;
5. preserve existing report versions.

A failed generation must not create a partially valid authoritative report version.

---

# 71. Partial Export Failure

If XLSX generation fails after report generation succeeds:

* report version remains valid;
* export job becomes retryable or failed;
* file generation is retried;
* report data is not regenerated unnecessarily when the stored report version is still valid.

---

# 72. Report Version and Export Relationship

The export should reference a specific report version whenever the report is versioned.

Example:

```text
Report Version 7
      ↓
Export Job
      ↓
report-v7.xlsx
```

If Version 8 is later created, an old export remains an export of Version 7.

---

# 73. Historical Export Integrity

An old XLSX export must not silently change because a newer report version exists.

If the underlying file remains available, it represents the report version from which it was generated.

If the file expires, a new export should be generated from the requested report version where still available.

---

# 74. Report API Response

Synchronous report requests may return:

```text
report_type
period
scope
generated_at
report_version
data
```

Asynchronous exports should return:

```text
export_job_id
status
report_version_id
```

The API must not keep an HTTP request open while generating a large XLSX file.

---

# 75. Report Status

A report generation job may use:

```text
PENDING
GENERATING
COMPLETED
FAILED
```

An export job may use:

```text
PENDING
PROCESSING
COMPLETED
RETRYING
FAILED
CANCELLED
```

The exact implementation may combine states where appropriate.

---

# 76. Report Idempotency

Idempotency is required for operations such as:

* automatic monthly generation;
* manual report generation where repeated requests must not duplicate a version;
* export job creation;
* retrying export processing.

The idempotency key must be scoped sufficiently to prevent collisions between Businesses.

---

# 77. Automatic Monthly Idempotency

The system must prevent duplicate monthly reports for the same:

```text
Business
Branch
Report Type
Period
Generation Definition Version
```

unless an explicit regeneration is requested.

---

# 78. Report Authorization at Generation Time

Authorization must be checked when the report is requested.

The system must not rely solely on authorization performed when a report was previously generated.

A user who later loses permission must not automatically gain access merely because they know a historical report version ID.

---

# 79. Report Authorization at Download Time

Export downloads must perform authorization again.

This is required because:

* employee permissions may change;
* employee may become inactive;
* Branch scope may change;
* Business subscription may expire;
* Business lifecycle may change.

Previously generated files must not bypass current access controls.

---

# 80. Report Ownership

Every report version must belong to exactly one Business.

Branch-specific reports must also identify their Branch.

Cross-Business report ownership is prohibited.

---

# 81. Report Data Ownership

Report results are derived from Business-owned transactional data.

A report must never combine data from different Businesses.

If a Business-level report combines multiple Branches, all Branches must belong to the same Business.

---

# 82. Report Calculation Rules

Financial report calculations must use authoritative monetary values.

The reporting layer must not recalculate historical financial values from:

* current Product price;
* current discount configuration;
* current Recipe;
* current Branch price;
* current Set configuration.

Historical transaction snapshots are authoritative for historical financial reporting.

---

# 83. Report Totals

Totals should be calculated consistently.

Examples:

```text
Gross Sales
- Discounts
+/- Adjustments
- Refunds
= Net Sales
```

Exact formulas are defined by the relevant business/report specification.

The same report definition must use the same calculation rules across UI and export.

---

# 84. UI and XLSX Consistency

When a report is shown in the UI and exported to XLSX, both should originate from the same report result/version where possible.

The XLSX exporter must not implement a separate independent financial calculation.

This prevents discrepancies between:

```text
UI Report
vs
Excel Report
```

---

# 85. Report Generation Workflow

Standard workflow:

```text
1. Authenticate
2. Validate Employee
3. Validate Business
4. Validate Lifecycle
5. Resolve Branch Scope
6. Validate Permission
7. Validate Subscription
8. Validate Report Parameters
9. Resolve Report Definition
10. Execute Report Query
11. Build Report Result
12. Create Report Version if required
13. Return Result
```

For export:

```text
14. Create Export Job
15. Commit
16. Worker processes export
17. Generate XLSX
18. Store file
19. Mark Export Completed
20. Audit
```

---

# 86. Report Transaction Boundary

Report reading should normally use a read-only transaction or consistent database session.

Report version creation, where required, should use an appropriate short transaction.

XLSX generation must not occur inside the transaction that creates the report version.

---

# 87. Report Consistency

The system must avoid generating a report from an internally inconsistent mixture of transactional states.

For historical/versioned reports, the report query must use a consistent source state.

Where required, report generation may use:

* database transaction snapshot;
* committed historical transaction data;
* immutable report source versions.

The system should avoid long-lived database snapshots for expensive exports.

---

# 88. Report Query Timeout

Report queries must have bounded execution time.

A report exceeding the configured threshold should:

* fail safely;
* record diagnostic information;
* not block the database indefinitely.

Long-running reports should be optimized or moved to an appropriate asynchronous/read-replica architecture.

---

# 89. Report Pagination

Large UI reports should support pagination where appropriate.

Pagination must not change financial totals.

Example:

```text
Page 1 → Orders 1–50
Page 2 → Orders 51–100

Total → calculated independently and consistently
```

The total must not depend on only the current page.

---

# 90. Export Row Limits

Export limits must be explicitly defined.

If a report exceeds a safe export size:

* the system may reject the export;
* recommend a smaller period;
* or process the export asynchronously with appropriate chunking.

The system must not crash because an unexpectedly large export was requested.

---

# 91. Report Sorting

Report sorting must be deterministic.

If two records have equal values for the primary sort field, a stable secondary key should be used.

This prevents inconsistent pagination and export ordering.

---

# 92. Report Filtering

Filters must be validated against the user's scope.

Example:

An employee authorized only for Branch A must not request:

```text
branch_id = Branch B
```

and receive Branch B data.

Filters are not authorization.

Authorization must occur independently.

---

# 93. Report Search

Search parameters may be supported for report data where useful.

Search must:

* be parameterized;
* be bounded;
* respect scope;
* not bypass filters;
* use indexes where appropriate.

---

# 94. Report and Audit

Audit reports are special because they may contain security-sensitive historical information.

Access to audit reports requires explicit permission.

Audit records themselves remain immutable.

Generating an audit report must not modify the audit history being reported.

---

# 95. Report and Payroll

Payroll reports must respect:

* Business scope;
* Branch scope;
* employee privacy;
* payroll permissions;
* historical payroll snapshots.

Current salary configuration must not rewrite historical payroll results.

---

# 96. Report and Inventory

Inventory reports must use:

* inventory transaction history;
* stock movements;
* relevant warehouse/Branch;
* recipe version where required;
* adjustment history.

Current Recipe configuration must not reinterpret historical inventory transactions.

---

# 97. Report and Cash

Cash reports must use:

* Cash Register;
* Cash Session;
* opening cash;
* payments;
* refunds;
* corrections;
* handovers;
* closing cash;
* discrepancies.

Closed Cash Sessions remain historical records.

---

# 98. Report and Orders

Order reports must use historical Order and Order Item snapshots.

Current Product configuration must not rewrite historical Order totals.

Cancelled, refunded, corrected and paid states must be interpreted according to their authoritative transaction history.

---

# 99. Report and Payments

Payment reports must use authoritative payment records.

Payment corrections and revisions must preserve the original transaction history.

A report must not simply replace the original payment with the corrected value without preserving the correction chain.

---

# 100. Report and Refunds

Refund reports must use historical refund records and their associated Order/payment context.

Current Product price must never be used to calculate an old refund.

---

# 101. Report and Discounts

Discount reports must distinguish:

```text
Base Product Price
Discount
Final Order Amount
```

A discount must not be interpreted as a permanent Product price change.

---

# 102. Report and Markup

Reports involving custom markup must preserve the transaction-level markup information.

Current Last Purchase Cost must not be used to recalculate an historical markup.

---

# 103. Report and Sets

Set reports must use the Set configuration/version applicable to the transaction.

Current Set composition must not rewrite historical Set sales.

---

# 104. Report and Configuration

Reports that need configuration context must reference the relevant configuration version.

Examples:

```text
Price Version
Recipe Version
Set Version
Menu Configuration Version
Report Definition Version
```

---

# 105. Report and Notifications

Report generation may produce notifications such as:

```text
REPORT_READY
REPORT_FAILED
EXPORT_READY
EXPORT_FAILED
```

Notifications are secondary operations.

Notification failure must not invalidate a successful report generation.

---

# 106. Report and Outbox

Required asynchronous report/export events should use the Outbox pattern.

Example:

```text
Create Export Job
       +
Create Outbox Event
       ↓
Single Transaction
       ↓
Commit
       ↓
Worker
```

This prevents committed export jobs from becoming invisible to background workers.

---

# 107. Report Event Idempotency

Background report events must be idempotent.

If the same event is delivered more than once:

* the report/export must not be duplicated;
* processing must detect the existing operation;
* the worker may safely acknowledge the duplicate.

---

# 108. Report Error Classification

Report errors should be classified as:

```text
Validation Error
Authorization Error
Business Rule Violation
Conflict
Not Found
Temporary Infrastructure Error
Permanent Processing Error
```

Examples:

```text
Period > 1 month
→ Validation Error

No REPORT_EXPORT permission
→ Authorization Error

Stale report definition
→ Conflict where applicable

Storage temporarily unavailable
→ Temporary Infrastructure Error
```

---

# 109. API Error Behavior

The API must return stable error responses.

Typical mapping:

```text
400 → Validation Error
401 → Authentication Error
403 → Authorization Error
404 → Resource Not Found
409 → Conflict
422 → Business Rule Violation where used
500/503 → Infrastructure Failure
```

Exact API error format is defined by the global error architecture.

---

# 110. Report Recovery After Worker Crash

If a worker crashes while processing an export:

```text
PROCESSING
   ↓
Worker failure
   ↓
Recovery / timeout detection
   ↓
RETRYING
   ↓
New worker
```

The same Export Job must be recoverable.

A new duplicate job should not be created merely because the worker crashed.

---

# 111. Report Job Lease

For long-running jobs, the system may use a lease/heartbeat mechanism.

If a worker stops reporting progress beyond the configured timeout, another worker may safely reclaim the job.

The reclaim operation must be concurrency-safe.

---

# 112. Report Storage Failure

If report generation succeeds but file storage fails:

* report version remains valid;
* export job is retryable;
* no transactional business data is rolled back.

The system must preserve separation between report state and file delivery state.

---

# 113. Report Cleanup

Background cleanup may remove:

* expired export files;
* obsolete temporary files;
* failed temporary artifacts.

Cleanup must not delete active report versions unless lifecycle/retention policy explicitly permits it.

---

# 114. Report Lifecycle

A report version may follow:

```text
GENERATING
    ↓
READY
    ↓
SUPERSEDED
    ↓
RETAINED / DELETED
```

The exact state model may be simplified.

Immutable historical versions remain identifiable even when superseded.

---

# 115. Report Definition Changes

When a report definition changes:

* the new definition receives a new version;
* future reports use the new definition;
* existing report versions remain associated with the old definition;
* historical reports are not silently rewritten.

---

# 116. Report API Versioning

If report API response structure changes incompatibly, API versioning must be used.

A report calculation version and API version are separate concepts.

Changing the HTTP representation does not necessarily mean changing historical report calculation logic.

---

# 117. Report Export Format

The current supported export format is:

```text
.xlsx
```

The architecture should allow future formats through an exporter interface.

Example:

```text
ReportExporter
├── XlsxExporter
├── CsvExporter (future)
└── PdfExporter (future)
```

No future format should require rewriting the report calculation layer.

---

# 118. Report Export Abstraction

The export pipeline should be:

```text
Report Result
      ↓
Exporter Interface
      ↓
XLSX Exporter
      ↓
File Storage
```

The exporter receives report data.

It must not independently query transactional data unless explicitly designed as a specialized streaming export.

---

# 119. Security of Generated Files

Generated files must not expose:

* access tokens;
* passwords;
* internal secrets;
* database credentials;
* security signatures;
* unnecessary internal identifiers.

Internal UUIDs may be included only when useful for traceability and permitted by report design.

---

# 120. Report Traceability

Important reports should be traceable through:

```text
Request
 ↓
Operation UUID
 ↓
Report Version
 ↓
Export Job
 ↓
File
 ↓
Audit Event
```

This enables support and debugging without changing historical data.

---

# 121. Report Supportability

Support/debugging should allow authorized administrators to answer:

* who generated the report;
* when it was generated;
* for which Business;
* for which Branch;
* for which period;
* which definition version was used;
* which report version was generated;
* whether it was exported;
* whether export succeeded;
* which file was produced.

---

# 122. Report Performance Strategy

Initial architecture:

```text
PostgreSQL Primary
        ↓
Reporting Query Layer
        ↓
Background Export Worker
```

Future scaling options:

```text
PostgreSQL Read Replica
        ↓
Heavy Reports
```

and, if required later:

```text
Dedicated Reporting Store
        ↓
Analytics
```

The initial system must not introduce unnecessary infrastructure.

---

# 123. Report Database Strategy

The reporting subsystem uses the existing PostgreSQL database initially.

It does not create:

* a separate database per Branch;
* a separate database per Business;
* a separate report database solely for architectural separation.

Business isolation remains logical and server-enforced.

---

# 124. Report Query Optimization

Optimization should follow this order:

1. Correct query;
2. Correct scope;
3. Correct indexes;
4. Efficient joins;
5. Aggregation in database;
6. Pagination;
7. Query caching where safe;
8. Background processing;
9. Read replica if necessary;
10. Dedicated reporting architecture only when justified.

Premature reporting infrastructure is prohibited.

---

# 125. Report Testing Strategy

Reporting requires multiple test layers.

### Unit Tests

Test:

* parameter validation;
* report calculations;
* totals;
* filters;
* date boundaries;
* empty reports.

### Integration Tests

Test:

* PostgreSQL queries;
* Business isolation;
* Branch scope;
* report version creation;
* transaction consistency.

### Export Tests

Test:

* XLSX generation;
* worksheet structure;
* totals;
* empty exports;
* large exports;
* file metadata.

### Security Tests

Test:

* cross-Business access;
* cross-Branch access;
* inactive employee;
* revoked permission;
* expired subscription;
* deleted Business.

### Concurrency Tests

Test:

* duplicate generation;
* duplicate export;
* two workers claiming one job;
* simultaneous corrections and report generation.

---

# 126. Report Invariants

The following invariants apply to Reporting and Export:

1. Every report belongs to exactly one Business.
2. Branch-scoped reports belong to a Branch of the same Business.
3. Cross-Business report access is prohibited.
4. Branch scope is always server validated.
5. Report permission is required.
6. Inactive employees cannot access reports through active authorization.
7. Subscription restrictions are enforced.
8. Report parameters are validated.
9. Manual report period cannot exceed one month.
10. Automatic monthly reports cover completed calendar periods.
11. Empty reports are valid.
12. Report queries do not modify transactional data.
13. Report versions are immutable.
14. Historical report versions cannot be silently overwritten.
15. New relevant source state creates a new version where versioning is required.
16. Current Product price cannot rewrite historical sales reports.
17. Current Recipe cannot rewrite historical inventory reports.
18. Current Set configuration cannot rewrite historical Set reports.
19. Current payroll configuration cannot rewrite historical payroll reports.
20. Current employee permissions cannot rewrite historical report authorship.
21. Report calculation definition version is identifiable for important historical reports.
22. Report generation is independent from XLSX generation.
23. XLSX generation does not modify transactional data.
24. Export jobs are idempotent where retries are possible.
25. Duplicate idempotent requests do not create duplicate logical exports.
26. Only one worker may actively process a job at a time.
27. Worker crashes must not permanently lose export jobs.
28. Temporary export failures may be retried.
29. Permanent failures must not retry indefinitely.
30. Failed exports do not invalidate valid report versions.
31. Export files are not authorization credentials.
32. File downloads require current authorization.
33. Expired files do not delete report versions.
34. Report versions do not depend on the continued existence of an export file.
35. Report generation must not block normal POS transactions unnecessarily.
36. Long-running XLSX generation occurs outside core database transactions.
37. Report queries use Business scope.
38. Report queries use Branch scope where required.
39. Cache is not the authoritative source for reports.
40. Cache failure cannot corrupt report history.
41. Read replicas cannot silently become authoritative transactional sources.
42. Offline devices cannot create authoritative server report versions independently.
43. Unsynchronized offline transactions are not treated as server-authoritative report data.
44. Report generation is auditable where required.
45. Export operations are auditable where required.
46. Report failures do not roll back unrelated committed transactions.
47. Report storage failure does not roll back committed report state.
48. Historical export files represent the report version from which they were generated.
49. Report definition changes do not rewrite old report versions.
50. API representation changes do not automatically change historical calculation versions.
51. Report sorting is deterministic.
52. Pagination does not change report totals.
53. Filters cannot bypass authorization.
54. Report files must not contain secrets.
55. Report logs must not contain sensitive credentials.
56. Report cleanup must respect retention and lifecycle policy.
57. Business deletion must respect data lifecycle policy.
58. Report generation must not resurrect deleted or read-only Business data.
59. Report operations preserve traceability from request to report version.
60. UI and XLSX representations of the same report version must use consistent calculations.
61. Financial report calculations use authoritative historical transaction values.
62. Payment corrections preserve historical correction chains.
63. Refund calculations use historical financial snapshots.
64. Discount reporting separates base price and discount.
65. Markup reporting preserves transaction-level markup information.
66. Cash reports use authoritative Cash Session history.
67. Inventory reports use authoritative Inventory Transaction history.
68. Payroll reports use authoritative historical payroll data.
69. Audit reports cannot modify audit history.
70. Background report processing is isolated from core transaction processing.
71. Report generation must use deterministic period boundaries.
72. Business timezone is used for business calendar calculations.
73. Server local timezone must not silently define Business report periods.
74. Report version creation is atomic where required.
75. Secondary notifications cannot invalidate successful report generation.
76. Report export must be replaceable through an exporter abstraction.
77. Report calculation and export formatting remain separate concerns.
78. Report architecture must remain compatible with future read replicas.
79. Reporting infrastructure must not be introduced without measurable need.
80. Historical integrity has priority over UI convenience.

---

# 127. Recommended Backend Structure

The reporting subsystem should follow the existing backend structure:

```text
app/
├── application/
│   └── reports/
│       ├── commands/
│       ├── queries/
│       ├── services/
│       └── validators/
│
├── reporting/
│   ├── definitions/
│   ├── queries/
│   ├── builders/
│   ├── generators/
│   ├── exporters/
│   └── versions/
│
├── background/
│   ├── jobs/
│   ├── workers/
│   └── handlers/
│
└── infrastructure/
    ├── database/
    ├── storage/
    └── messaging/
```

The exact module boundaries may evolve during implementation.

---

# 128. Dependency Rules

Reporting must follow the existing dependency rules:

```text
API
 ↓
Application
 ↓
Reporting / Domain
 ↓
Repository Abstraction
 ↓
Infrastructure
```

Reporting code must not:

* directly depend on HTTP;
* directly expose SQLAlchemy models to API consumers;
* bypass authorization;
* modify transactional state through query code.

---

# 129. Repository Boundary

Report repositories or query services may expose optimized read operations.

They must not silently commit transactions.

Example:

```text
ReportQueryRepository
    ↓
SQL Query
    ↓
Report DTO
```

This is separate from transactional repositories used for business commands.

---

# 130. Report DTOs

Reports should use dedicated DTO/read models.

The API should not expose database ORM entities directly.

Example:

```text
CashReportRow
OrderReportRow
InventoryReportRow
PayrollReportRow
```

This allows report presentation to evolve independently from database models.

---

# 131. Report Service Separation

The architecture should separate:

```text
Report Calculation
        ↓
Report Versioning
        ↓
Export Formatting
        ↓
File Storage
```

Changing XLSX formatting must not require changing financial calculations.

Changing storage provider must not require changing report calculations.

---

# 132. Background Job Separation

The background subsystem should distinguish:

```text
Report Generation Job
Export Generation Job
File Cleanup Job
Monthly Report Scheduler
```

This prevents one category of failure from blocking unrelated jobs.

---

# 133. Report Queue Isolation

If the job infrastructure supports multiple queues, report/export work should use a dedicated queue or bounded worker pool.

Heavy report generation must not starve:

* synchronization;
* notifications;
* critical business background jobs.

---

# 134. Report Scheduling

Scheduled monthly reports must use a centralized scheduler.

The scheduler should:

* detect completed periods;
* create idempotent jobs;
* avoid duplicate scheduling;
* record execution state;
* recover after restart.

Scheduler failure must not permanently prevent monthly reports from being generated.

---

# 135. Report and Time

All persisted timestamps should use UTC.

Business/Branch timezone is used for:

* calendar periods;
* monthly boundaries;
* daily reports;
* date-based filters.

The report should preserve enough metadata to identify the timezone used for its calendar interpretation.

---

# 136. Report and Clock

The backend should use the existing clock abstraction rather than calling system time directly throughout reporting code.

This improves:

* deterministic tests;
* scheduled jobs;
* period calculations;
* recovery;
* historical debugging.

---

# 137. Report Version Creation Example

Example:

```text
March Monthly Report

Business: B1
Branch: A
Period:
2026-03-01 00:00
→
2026-04-01 00:00

Definition Version: 3

Generation:
MONTHLY_AUTO_GENERATION

Result:
Report Version 5
```

Later a correction changes March sales:

```text
Report Version 5
      ↓
Correction
      ↓
Report Version 6
```

Version 5 remains immutable.

---

# 138. Export Example

```text
User requests March Sales XLSX
        ↓
Authorization
        ↓
Report Version 6 selected
        ↓
Export Job created
        ↓
Outbox event committed
        ↓
Worker receives job
        ↓
XLSX generated
        ↓
File stored
        ↓
Export Job = COMPLETED
        ↓
User downloads file
```

---

# 139. Report Security Guardrails

The implementation must reject:

* cross-Business report IDs;
* cross-Branch access;
* unauthorized payroll reports;
* unauthorized financial reports;
* expired/invalid export access;
* deleted Business report generation;
* forged report version identifiers;
* unauthorized report regeneration.

---

# 140. Report Architecture Guardrails

The following implementation patterns are prohibited:

* report logic directly inside API routes;
* financial calculations duplicated in XLSX exporter;
* report generation inside long-running request transactions;
* direct file storage access from business logic;
* cache as report authority;
* current configuration used to rewrite historical data;
* cross-Business report queries;
* silent permission bypass;
* silent last-write-wins for report versions;
* unbounded export generation;
* unbounded retry loops.

---

# 141. Future Scaling

The architecture may later support:

```text
Primary PostgreSQL
        ↓
Read Replica
        ↓
Reporting Query Layer
```

and eventually:

```text
Operational PostgreSQL
        ↓
ETL / CDC
        ↓
Dedicated Reporting Store
        ↓
Analytics
```

These changes must preserve the same external report contracts and historical integrity principles.

---

# 142. Related Documents

### Business Analysis

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
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend

* `docs/06_Backend/01_Backend_Architecture.md`
* `docs/06_Backend/02_Backend_Project_Structure.md`
* `docs/06_Backend/06_Authentication_and_Authorization.md`
* `docs/06_Backend/07_Transaction_Management.md`
* `docs/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/06_Backend/11_Configuration_and_Environment_Management.md`

---

# 143. Status

**Backend Architecture Document:** Completed.

**Document Status:** Accepted.

**Current Document:** `12_Reporting_and_Export_Architecture.md`

**Next Document:** `13_Backend_Health_Observability_and_Monitoring.md`

