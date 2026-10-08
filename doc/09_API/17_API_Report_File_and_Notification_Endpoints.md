# API Report, File and Notification Endpoints

**Document ID:** API-17
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the public API contract for Reports, Report Versions, File Exports, File Access and Notifications in FastFood ERP.

The API must support:

* operational reports;
* Business and Branch reports;
* daily reports;
* monthly reports;
* report generation;
* report versions;
* immutable historical report snapshots;
* XLSX export;
* asynchronous export jobs;
* file metadata;
* authorized file download;
* notification retrieval;
* notification state;
* alert categories;
* read/unread state;
* notification delivery metadata;
* report and notification permissions;
* Business and Branch isolation;
* subscription read-only behavior;
* auditability;
* historical integrity;
* asynchronous processing;
* performance and SLOs.

The API must distinguish between:

1. authoritative Report Versions;
2. temporary/generated report results;
3. exported files;
4. user-facing Notifications;
5. alert generation and delivery.

These are related but separate resources.

---

# 2. Scope

This document covers:

* Report resources;
* Report definitions;
* Report generation;
* Daily reports;
* Monthly reports;
* Branch reports;
* Cash reports;
* Order reports;
* Payment reports;
* Inventory reports;
* Employee reports;
* Payroll reports;
* discrepancy reports;
* correction reports;
* audit-related reports;
* Report Versions;
* report source state;
* report period;
* report regeneration;
* XLSX export;
* export jobs;
* file metadata;
* file authorization;
* file download;
* file expiration;
* file lifecycle;
* Notifications;
* notification categories;
* notification recipients;
* notification read state;
* bulk notification state changes;
* alert creation;
* alert severity;
* asynchronous notification delivery;
* Business and Branch scope;
* subscription restrictions;
* offline notification behavior;
* idempotency;
* concurrency;
* audit;
* observability;
* performance.

---

# 3. Architectural Position

The API follows the standard architecture:

```text
Client
   ↓
API
   ↓
Authentication
   ↓
Authorization
   ↓
Business / Branch Scope
   ↓
Request Validation
   ↓
Application Use Case
   ↓
Domain / Reporting Services
   ↓
Repository / Reporting Infrastructure
   ↓
PostgreSQL
   ↓
Background Workers where required
   ↓
File Storage / Notification Infrastructure
```

Large report generation and file export must not unnecessarily block normal POS operations.

---

# 4. Resource Model

The main resources are:

```text
Business
   ├── Report
   │    └── Report Version
   │
   ├── Export Job
   │    └── File
   │
   └── Notification
        └── Delivery / Read State
```

A Report describes a reporting resource.

A Report Version represents an immutable historical report result.

An Export Job represents asynchronous file generation.

A File represents stored exported content.

A Notification represents a user-facing event or alert.

---

# 5. Report Resource

A Report represents a logical report definition and its generated versions.

Example:

```json
{
  "id": "018f...",
  "type": "DAILY_SALES",
  "business_id": "018f...",
  "branch_id": "018f...",
  "period": {
    "from": "2026-10-01",
    "to": "2026-10-01"
  },
  "status": "AVAILABLE"
}
```

The Report identity must not be confused with a Report Version.

---

# 6. Report Types

Initial report types may include:

```text
DAILY_SALES
MONTHLY_SALES
BRANCH_PERFORMANCE
CASH_SESSION
CASHIER
ORDERS
PAYMENTS
REFUNDS
DISCREPANCIES
CORRECTIONS
INVENTORY
EMPLOYEE
PAYROLL
AUDIT
CHANGE_HISTORY
```

The exact report registry is controlled by the reporting architecture.

Unsupported report types must be rejected.

---

# 7. Report Creation

Endpoint:

```http
POST /api/v1/reports
```

Example:

```json
{
  "type": "DAILY_SALES",
  "branch_id": "018f...",
  "period": {
    "from": "2026-10-07",
    "to": "2026-10-07"
  }
}
```

The server validates:

* report type;
* Business scope;
* Branch scope;
* period;
* permissions;
* subscription state;
* report limits.

The client does not determine authoritative Business ownership.

---

# 8. Report Read

Endpoint:

```http
GET /api/v1/reports/{report_id}
```

The response may contain:

* Report identity;
* type;
* Business;
* Branch;
* period;
* current status;
* latest Version;
* creation information;
* available exports.

Only authorized report information may be returned.

---

# 9. Report List

Endpoint:

```http
GET /api/v1/reports
```

Supported filters may include:

```text
type
branch_id
status
from
to
created_by
```

Results must use bounded pagination.

---

# 10. Report Status

Possible Report states:

```text
REQUESTED
GENERATING
AVAILABLE
FAILED
ARCHIVED
```

The state represents report availability.

It must not be confused with the immutable state of a Report Version.

---

# 11. Synchronous Reports

Small and predictable reports may be generated synchronously.

Example:

```text
GET /reports/{id}/summary
```

The API should return directly when the expected processing time remains within the defined API latency budget.

---

# 12. Asynchronous Reports

Large reports must use asynchronous processing.

Example:

```http
POST /api/v1/reports
```

Response:

```http
202 Accepted
```

Example:

```json
{
  "report_id": "018f...",
  "job_id": "018f...",
  "status": "PROCESSING"
}
```

The client can then query the status.

---

# 13. Report Job Status

Endpoint:

```http
GET /api/v1/reports/{report_id}/status
```

Possible states:

```text
PENDING
PROCESSING
COMPLETED
FAILED
CANCELLED
```

The server remains authoritative for job state.

---

# 14. Report Period

Every period-based report must have an explicit period.

Example:

```json
{
  "from": "2026-10-01",
  "to": "2026-10-31"
}
```

Date-only reporting concepts must not be interpreted as arbitrary timestamps.

Business timezone rules must be applied consistently.

---

# 15. Daily Report

Endpoint:

```http
GET /api/v1/reports/daily
```

Possible parameters:

```text
date
branch_id
```

The report may contain:

* Orders;
* sales;
* payments;
* refunds;
* cash sessions;
* inventory effects;
* discrepancies;
* relevant operational metrics.

The exact report definition belongs to the reporting architecture.

---

# 16. Monthly Report

Endpoint:

```http
GET /api/v1/reports/monthly
```

Parameters:

```text
year
month
branch_id
```

The system supports:

* automatic monthly report generation;
* manual report generation.

Manual report period must remain within the configured maximum range.

The current Business rule allows a manual report period of up to one month.

---

# 17. Automatic Monthly Report

The system may automatically generate the monthly report on the last calendar day after the required operational closing conditions are satisfied.

Automatic generation occurs through background processing.

The API exposes the resulting Report and Report Version.

---

# 18. Empty Reports

A valid report may contain no business activity.

For example:

```text
Orders = 0
Payments = 0
Refunds = 0
```

The API must still be able to produce a valid report.

An empty result is not automatically a failure.

---

# 19. Branch Reports

Branch-scoped reports require Branch authorization.

Example:

```http
GET /api/v1/reports/daily?branch_id=018f...
```

The server must verify:

* Business membership;
* Branch scope;
* report permission.

A user cannot access another Branch by changing the Branch UUID.

---

# 20. Business-Level Reports

Business-level reports may aggregate multiple Branches where the actor has sufficient authority.

Example:

```http
GET /api/v1/reports/branch-performance
```

The API must only aggregate Branches within the authorized Business scope.

---

# 21. Report Data Authority

Reports must use authoritative transactional data.

Examples:

```text
Orders
Payments
Refunds
Cash Sessions
Inventory Transactions
Attendance
Payroll
Audit Events
```

Cached values must not silently replace authoritative historical sources when producing authoritative Report Versions.

---

# 22. Report Version

A Report Version is an immutable historical representation of a report result.

Example:

```json
{
  "id": "018f...",
  "report_id": "018f...",
  "version": 3,
  "status": "FINAL",
  "period": {
    "from": "2026-10-01",
    "to": "2026-10-31"
  }
}
```

Once committed, a Report Version must not be modified.

---

# 23. Report Version Endpoint

Endpoint:

```http
GET /api/v1/reports/{report_id}/versions
```

Specific version:

```http
GET /api/v1/reports/{report_id}/versions/{version_id}
```

The API may expose:

* Version number;
* creation timestamp;
* period;
* creator/system source;
* creation reason;
* source state;
* status;
* available exports.

---

# 24. Report Version Creation

A new Report Version is created when the reporting rules require a new authoritative result.

Examples:

* relevant transaction correction;
* report source data changes;
* report definition change;
* explicit regeneration;
* scheduled report generation.

The previous Version remains immutable.

---

# 25. Report Version Source State

A Report Version must identify the relevant source state.

Possible information includes:

```text
Report Definition Version
Data Snapshot / Source State
Creation Timestamp
Period
Business
Branch
Generation Reason
```

This allows historical results to remain explainable.

---

# 26. Report Version Immutability

The API must not provide a generic endpoint for modifying an existing Report Version.

There is no normal:

```http
PATCH /report-versions/{id}
```

Historical corrections require a new Version.

---

# 27. Report Regeneration

Endpoint:

```http
POST /api/v1/reports/{report_id}/regenerate
```

Regeneration must create a new Version where the reporting architecture determines that the result should change.

The previous Version remains available.

---

# 28. Report Version Reason

A new Version should record the reason:

```text
INITIAL_GENERATION
DATA_CORRECTION
REPORT_DEFINITION_CHANGE
MANUAL_REGENERATION
SCHEDULED_REGENERATION
SYSTEM_RECONCILIATION
```

The reason is historical metadata.

---

# 29. Report Definition Version

If report calculation logic changes, the Report Version should identify the Report Definition Version used.

Example:

```json
{
  "report_definition_version": 2,
  "report_version": 5
}
```

A new definition must not reinterpret old Report Versions.

---

# 30. Report Corrections

If a transaction correction changes a previously generated report:

```text
Original Report Version
        ↓
Relevant correction
        ↓
New Report Version
```

The previous Version remains immutable.

The API must not silently rewrite the original result.

---

# 31. Report Historical Integrity

Current transaction data must not be used to silently rewrite historical Report Versions.

Historical reporting must preserve the state required to reproduce or explain the original Version.

---

# 32. Report Access

Report access requires:

* authenticated actor;
* Business scope;
* Branch scope where applicable;
* report permission;
* subscription state;
* resource-level authorization.

---

# 33. Report Permissions

Typical permissions may include:

```text
report.view
report.view_branch
report.view_business
report.generate
report.regenerate
report.export
report.view_sensitive
```

The exact permission registry remains centralized.

---

# 34. Sensitive Reports

Reports containing sensitive information may require additional permission.

Examples:

* payroll;
* salary;
* audit;
* detailed cost;
* financial corrections.

The API must not expose sensitive report fields merely because the actor can view ordinary sales reports.

---

# 35. Report Export

Endpoint:

```http
POST /api/v1/reports/{report_id}/exports
```

Example:

```json
{
  "format": "XLSX",
  "version_id": "018f..."
}
```

The server validates:

* Report access;
* Report Version;
* export format;
* Business scope;
* Branch scope.

---

# 36. Export Formats

Initial supported format:

```text
XLSX
```

Future formats may be introduced without changing the Report Version model.

Unsupported formats must return a stable error code.

---

# 37. XLSX Export

Large XLSX generation must run asynchronously.

Example response:

```http
202 Accepted
```

```json
{
  "export_id": "018f...",
  "job_id": "018f...",
  "status": "PENDING"
}
```

The API must not hold a normal HTTP request open unnecessarily while generating large files.

---

# 38. Export Job

An Export Job represents the process of generating a file.

Possible states:

```text
PENDING
PROCESSING
COMPLETED
FAILED
EXPIRED
CANCELLED
```

The job state is server-authoritative.

---

# 39. Export Job Status

Endpoint:

```http
GET /api/v1/exports/{export_id}
```

Response may include:

```json
{
  "id": "018f...",
  "status": "COMPLETED",
  "file_id": "018f..."
}
```

A failed export should expose a safe machine-readable error state.

---

# 40. Export Idempotency

Export requests may use idempotency where duplicate generation would be expensive.

Example:

```http
Idempotency-Key: 018f...
```

Repeated requests with the same valid operation identity must not unexpectedly create uncontrolled duplicate export jobs.

---

# 41. Export and Report Version

An Export must reference the exact Report Version being exported.

Example:

```text
Report
  ↓
Report Version 5
  ↓
XLSX Export
```

Current report data must not change the contents of an already-created export.

---

# 42. File Resource

A File represents stored generated content.

Example:

```json
{
  "id": "018f...",
  "name": "daily-sales-2026-10-07.xlsx",
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "size": 24576
}
```

Raw filesystem paths must never be exposed.

---

# 43. File Metadata

File metadata may include:

```text
File ID
Original Name
MIME Type
Size
Storage Reference
Owner Resource
Created At
Expiration
Checksum
Status
```

The storage reference remains an internal implementation detail.

---

# 44. File Upload and Generated Files

This API section primarily covers generated files.

User-uploaded documents and general file-storage behavior follow:

`15_Backend_File_Storage_and_Document_Management.md`

The API must preserve a clear distinction between:

* generated report files;
* user-uploaded files;
* temporary processing files.

---

# 45. File Access

Endpoint:

```http
GET /api/v1/files/{file_id}
```

The server validates authorization before returning metadata.

---

# 46. File Download

Endpoint:

```http
GET /api/v1/files/{file_id}/download
```

The API must verify:

* file existence;
* Business ownership;
* resource ownership;
* Employee permission;
* file status;
* expiration.

A File UUID alone does not grant access.

---

# 47. Download Authorization

A user who can access a Report Version may access its authorized export.

However, this does not imply access to every File belonging to the Business.

File authorization must remain resource-specific.

---

# 48. File Expiration

Temporary export files may have an expiration time.

After expiration:

```text
File
 ↓
EXPIRED
```

The API should return a stable error such as:

```text
FILE_EXPIRED
```

Expiration of an exported file must not delete the authoritative Report Version.

---

# 49. File Deletion

Temporary generated files may be deleted after their retention period.

Deleting an export file must not delete:

* Report;
* Report Version;
* source transactions;
* audit records.

---

# 50. File Integrity

Generated files should have an integrity identifier such as a checksum where appropriate.

The checksum allows the system to verify that the stored file corresponds to the generated content.

---

# 51. File Security

The API must not expose:

* filesystem paths;
* storage credentials;
* bucket credentials;
* internal storage topology.

Temporary download URLs, if used, must be authorization-controlled and time-bounded.

---

# 52. Notification Resource

A Notification represents a user-facing message generated by a Business event, system event or operational alert.

Example:

```json
{
  "id": "018f...",
  "type": "LOW_STOCK",
  "severity": "WARNING",
  "title": "Low stock",
  "read": false
}
```

---

# 53. Notification Categories

Initial categories include:

```text
LOW_STOCK
OUT_OF_STOCK
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_READ_ONLY
SALARY_DUE
LARGE_REFUND
INVENTORY_VARIANCE
BRANCH_LOSS
CASH_DISCREPANCY
CORRECTION_REQUEST
SYNC_CONFLICT
SECURITY_ALERT
SYSTEM_ALERT
```

The registry may expand without changing the notification architecture.

---

# 54. Notification Severity

Initial severity values:

```text
INFO
SUCCESS
WARNING
CRITICAL
```

Severity influences presentation and operational priority.

It does not independently grant permissions.

---

# 55. Notification Creation

Notifications are normally created by Application/Domain/background workflows rather than directly by ordinary clients.

The API should not allow a user to impersonate the system and create arbitrary security or financial notifications.

---

# 56. Notification Read

Endpoint:

```http
GET /api/v1/notifications
```

The result is limited to notifications belonging to the authenticated recipient or authorized Business context.

---

# 57. Notification Details

Endpoint:

```http
GET /api/v1/notifications/{notification_id}
```

The server verifies recipient ownership and scope.

A user cannot access another Employee's private notification by changing the UUID.

---

# 58. Mark Notification as Read

Endpoint:

```http
POST /api/v1/notifications/{notification_id}/read
```

The operation should be idempotent.

Repeated requests do not create duplicate business effects.

---

# 59. Mark All Notifications as Read

Endpoint:

```http
POST /api/v1/notifications/read-all
```

The operation applies only to notifications accessible to the authenticated user.

It must not mark notifications belonging to another Employee as read.

---

# 60. Unread Count

Endpoint:

```http
GET /api/v1/notifications/unread-count
```

Example:

```json
{
  "count": 7
}
```

The count is user-scoped.

It must not expose another Employee's notification state.

---

# 61. Notification Filtering

The list endpoint may support:

```text
type
severity
read
from
to
branch_id
```

All filters remain authorization-aware.

---

# 62. Notification Pagination

Notification lists use bounded pagination.

Example:

```http
GET /api/v1/notifications?limit=50&cursor=...
```

Ordering should be deterministic, normally using:

```text
created_at DESC
id DESC
```

---

# 63. Notification Delivery

Notifications may be delivered through:

```text
In-App
Background Delivery
Future External Channel
```

The current primary channel is in-app notification.

External delivery is asynchronous.

---

# 64. Notification Transaction Boundary

Core business transactions must not depend on successful notification delivery.

Example:

```text
Cash Session Close
      ↓
Database Commit
      ↓
Notification Event
      ↓
Notification Worker
```

Notification failure must not rollback the committed Cash Session.

---

# 65. Notification Outbox

Important notifications should use the Outbox architecture.

Example:

```text
Business Transaction
      +
Notification Outbox Event
      ↓
Atomic Commit
      ↓
Notification Worker
      ↓
Notification Record
```

This prevents important notification events from being lost between transaction commit and background processing.

---

# 66. Notification Idempotency

Notification generation must be protected against duplicate processing.

For important events, the system should identify:

```text
Event UUID
Business
Recipient
Notification Type
Source Entity
```

Repeated worker execution must not create uncontrolled duplicate notifications.

---

# 67. Notification Deduplication

Some alert types may require deduplication.

Example:

```text
LOW_STOCK
Product A
Branch B
```

Repeated detection of the same condition should not necessarily create a new notification every time the background job runs.

Deduplication rules must be explicit per notification type.

---

# 68. Notification Aggregation

High-frequency operational events may be aggregated.

Example:

```text
10 low-stock Products
      ↓
One summary notification
```

Aggregation must not hide critical alerts where individual visibility is required.

---

# 69. Notification Lifecycle

Possible states:

```text
CREATED
DELIVERED
READ
ARCHIVED
EXPIRED
```

The exact state model may be simplified.

Read state and delivery state should remain conceptually separate.

---

# 70. Notification Retention

Notifications are operational records, not the primary historical source for Business transactions.

Retention may be limited according to the notification lifecycle policy.

Deleting an old Notification must not delete:

* Order;
* Payment;
* Inventory Transaction;
* Audit;
* Report Version.

---

# 71. Notification and Audit

Important notifications may reference their source event.

Example:

```json
{
  "source_type": "CASH_SESSION",
  "source_id": "018f..."
}
```

The source event remains authoritative.

Notification text is not the authoritative financial or operational record.

---

# 72. Notification Source Integrity

For example:

```text
CASH_DISCREPANCY notification
        ≠
Cash Session authoritative state
```

The notification informs the user.

The Cash Session remains authoritative.

---

# 73. Subscription Notifications

The system may notify users when subscription approaches expiry.

Example:

```text
SUBSCRIPTION_EXPIRING
```

After expiry:

```text
SUBSCRIPTION_READ_ONLY
```

Notifications must not override subscription enforcement.

The subscription state remains server-authoritative.

---

# 74. Low Stock Notifications

Low-stock notifications are generated from authoritative inventory conditions.

The notification must not itself change:

* stock;
* Product state;
* menu availability.

---

# 75. Large Refund Notifications

A large refund notification may reference:

```text
Order
Refund
Branch
Employee
```

The refund remains authoritative in the financial domain.

Notification creation is secondary processing.

---

# 76. Inventory Variance Notifications

A large inventory variance may generate a notification.

The notification should reference the relevant:

* Product;
* Warehouse;
* Inventory Count;
* Adjustment.

The notification does not perform the adjustment itself.

---

# 77. Branch Loss Notifications

Branch performance or loss alerts may reference a relevant report or calculation.

The API must not allow users to manipulate an alert to change the underlying financial data.

---

# 78. Security Notifications

Security alerts may include:

```text
UNTRUSTED_DEVICE
DEVICE_REVOKED
SUSPICIOUS_AUTHENTICATION
OFFLINE_AUTHORIZATION_FAILURE
```

Security notifications must not expose sensitive security material.

---

# 79. Notification Authorization

Notifications must be visible only to their intended recipients or explicitly authorized Business/Branch users.

Owner-level alerts may be visible to:

* Owner;
* explicitly authorized Manager;
* authorized administrative users.

Cashier-specific alerts may remain limited to the relevant employee where appropriate.

---

# 80. Branch Notification Scope

Branch-scoped notifications must identify the Branch.

A Branch user must not receive another Branch's private operational notification unless explicitly authorized.

---

# 81. Business Notification Scope

Business-level notifications may be visible across multiple Branches according to permission.

The API must still validate Business membership.

---

# 82. Offline Notifications

Offline clients may display locally synchronized notifications.

The local copy is not authoritative.

After synchronization:

```text
Server Notification State
      ↓
Device Synchronization
      ↓
Local Notification State
```

A client must not manufacture authoritative notifications while offline.

---

# 83. Notification Synchronization

Notification synchronization should preserve:

* Notification UUID;
* recipient;
* source event;
* creation timestamp;
* read state;
* server state.

Conflicting notification state should be resolved according to the synchronization architecture.

---

# 84. Report and Notification Relationship

A Report may generate a notification.

Example:

```text
Inventory Report
      ↓
Large Variance
      ↓
Notification
```

The Report remains the analytical source.

The Notification is the user-facing alert.

---

# 85. Report and File Relationship

A File may be generated from a specific Report Version.

Relationship:

```text
Report
 ↓
Report Version
 ↓
Export Job
 ↓
File
```

Deleting an exported File must not delete the Report Version.

---

# 86. Report and Subscription

When Business subscription enters `READ_ONLY`:

Allowed:

* viewing permitted historical reports;
* viewing Report Versions;
* generating permitted read-only reports;
* exporting permitted reports to XLSX.

Blocked:

* report operations classified as modifying Business state;
* operations prohibited by subscription policy.

The exact entitlement remains server-controlled.

---

# 87. File and Subscription

Previously generated authorized files may remain accessible according to their retention and authorization rules.

New exports after subscription expiry are allowed only where the subscription policy explicitly permits them.

The API must not use file existence as proof of authorization.

---

# 88. Notification and Subscription

Subscription expiry notifications may remain available after expiry where policy permits.

A notification cannot reactivate a subscription.

---

# 89. Report Security

Reports must respect:

* Business scope;
* Branch scope;
* employee permissions;
* payroll confidentiality;
* inventory cost confidentiality;
* audit restrictions.

A report endpoint must not expose a broader dataset than the actor could access through the underlying authorization model.

---

# 90. Export Security

An export must inherit the authorization boundary of its source Report Version.

If access to the source Report Version is revoked, the API must reevaluate access to the export according to file policy.

Possessing a previous File URL must not automatically bypass current authorization.

---

# 91. Export Expiration and Regeneration

If an export expires:

```text
Expired File
      ↓
Generate New Export
      ↓
Same Report Version
```

The Report Version itself does not need to change merely because a File expired.

---

# 92. Report Cache

Read-heavy reports may use cache where safe.

However:

```text
Cached Report
      ≠
Immutable Report Version
```

A cached report result must not replace the historical Report Version.

---

# 93. Report Cache Source State

A cached report should identify sufficient source information such as:

```text
Business
Branch
Period
Report Definition Version
Relevant Source State
```

This prevents stale results from being treated as authoritative historical versions.

---

# 94. File Cache

File metadata may be cached.

File authorization must still be evaluated according to the current security policy.

Caching a File metadata record must not grant access to the underlying content.

---

# 95. Notification Cache

Unread counts may be cached for performance.

The cache must be:

* user-scoped;
* bounded;
* invalidated when notification state changes.

Cached unread counts must not expose another user's notification state.

---

# 96. Audit

Important report and file operations should be auditable:

* report generation;
* sensitive report access where required;
* report regeneration;
* export creation;
* sensitive file download;
* file deletion where relevant;
* notification administrative operations.

Routine notification reads do not necessarily require business audit records.

---

# 97. Error Codes

Relevant error codes include:

```text
REPORT_NOT_FOUND
REPORT_TYPE_NOT_SUPPORTED
REPORT_PERIOD_INVALID
REPORT_SCOPE_DENIED
REPORT_GENERATION_FAILED
REPORT_GENERATION_IN_PROGRESS
REPORT_VERSION_NOT_FOUND
REPORT_VERSION_NOT_AVAILABLE
REPORT_VERSION_CONFLICT
EXPORT_NOT_FOUND
EXPORT_FORMAT_NOT_SUPPORTED
EXPORT_FAILED
EXPORT_EXPIRED
FILE_NOT_FOUND
FILE_EXPIRED
FILE_ACCESS_DENIED
FILE_NOT_READY
FILE_INTEGRITY_ERROR
NOTIFICATION_NOT_FOUND
NOTIFICATION_ACCESS_DENIED
NOTIFICATION_ALREADY_READ
INVALID_NOTIFICATION_STATE
SUBSCRIPTION_READ_ONLY
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
ACCESS_DENIED
DUPLICATE_OPERATION
RATE_LIMITED
SERVICE_UNAVAILABLE
```

Canonical error behavior is defined in:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 98. Idempotency

Idempotency should be used for retryable state-changing operations such as:

```text
Report generation
Report regeneration
Export creation
Notification administrative mutations
```

Marking a notification as read should also be safe to repeat.

Duplicate operations must not create uncontrolled duplicate:

* Report Versions;
* Export Jobs;
* Notifications.

---

# 99. Concurrency

Report generation and regeneration must use appropriate concurrency control.

For example, two simultaneous regeneration requests should not create uncontrolled duplicate authoritative Report Versions when the same operation is intended to be idempotent.

Export Jobs may run concurrently when they reference different Report Versions.

Notification read state must remain concurrency-safe.

---

# 100. Async Job Recovery

If a worker fails during report generation:

```text
Report Job
   ↓
FAILED / RETRYABLE
   ↓
Retry
```

A retry must not corrupt an existing completed Report Version.

If a Report Version was already committed, retry logic must recognize the authoritative result.

---

# 101. Export Worker Recovery

If an XLSX worker fails:

```text
Export Job
   ↓
FAILED
   ↓
Retry
```

A completed File must not be duplicated indefinitely because of worker retry.

Operation identity must remain stable.

---

# 102. Notification Worker Recovery

If notification delivery fails:

```text
Notification Event
   ↓
Retry
```

The retry must not create duplicate user notifications when the original Notification already exists.

---

# 103. File Storage Failure

If file storage fails after Report Version creation:

```text
Report Version
   ↓
Committed
   ↓
File Export Failed
```

The Report Version remains authoritative.

The export may be retried independently.

---

# 104. Report Generation Performance

Initial targets:

| Operation                     |   Target |
| ----------------------------- | -------: |
| Report metadata read p95      | ≤ 200 ms |
| Small report read p95         | ≤ 500 ms |
| Report list p95               | ≤ 300 ms |
| Report Version list p95       | ≤ 300 ms |
| Report status read p95        | ≤ 200 ms |
| Report generation request p95 | ≤ 300 ms |
| XLSX export request p95       | ≤ 300 ms |
| Export status read p95        | ≤ 200 ms |
| File metadata read p95        | ≤ 200 ms |
| Notification list p95         | ≤ 250 ms |
| Notification read p95         | ≤ 200 ms |
| Notification mark-read p95    | ≤ 200 ms |
| Unread count p95              | ≤ 150 ms |

Large report generation and XLSX creation are asynchronous and are not measured by normal synchronous API latency.

---

# 105. Background Processing SLO

Initial background targets:

* normal report generation jobs should begin processing within **30 seconds** of acceptance;
* normal XLSX export jobs should begin processing within **30 seconds**;
* critical notifications should enter notification processing within **10 seconds** after transaction commit;
* normal operational notifications should enter processing within **60 seconds**.

These are initial targets and may be refined using production measurements.

---

# 106. Availability Target

Report, File and Notification APIs follow the platform target:

**≥ 99.9% monthly availability**

The system must protect core POS and transactional workloads from heavy report/export workloads.

---

# 107. Background Resource Isolation

Large reports and XLSX exports must not monopolize resources required by:

* POS;
* payment;
* inventory;
* synchronization;
* authentication.

Worker concurrency must remain bounded.

---

# 108. Rate Limiting

Rate limiting may apply to:

* report generation;
* report regeneration;
* XLSX exports;
* large file operations;
* notification bulk operations.

Normal report reads and notification reads should not be unnecessarily restricted.

---

# 109. Export Limits

The system may enforce:

* maximum report period;
* maximum concurrent exports;
* maximum file size;
* maximum export frequency;
* maximum background job duration.

Limits must be explicit and return stable errors.

---

# 110. Large Report Strategy

Large reports should use:

* asynchronous jobs;
* database aggregation;
* bounded memory;
* streaming where supported;
* temporary file storage;
* controlled worker concurrency.

The entire report should not necessarily be loaded into application memory.

---

# 111. XLSX Memory Strategy

XLSX generation should avoid unbounded in-memory datasets.

The implementation should use:

* streaming generation where supported;
* bounded batches;
* temporary storage;
* controlled worker memory.

---

# 112. Notification Performance

Notification creation should be asynchronous when generated as a secondary effect.

Reading notifications must remain fast enough for dashboard and operational UI usage.

Unread count should use an optimized query or bounded cache.

---

# 113. Observability

Metrics should include:

```text
report_generation_count
report_generation_latency
report_generation_failure_count
report_version_creation_count
export_job_count
export_job_latency
export_failure_count
file_download_count
file_access_denied_count
notification_creation_count
notification_delivery_failure_count
notification_read_count
notification_unread_count
```

Metrics must avoid uncontrolled identifiers such as raw Business UUIDs or Notification UUIDs as metric labels.

---

# 114. Report Monitoring

Alerts should be considered for:

* report generation backlog;
* report generation failure spikes;
* unusually long report jobs;
* XLSX export backlog;
* file storage failures;
* notification delivery backlog.

---

# 115. Notification Monitoring

The system should monitor:

* notification queue depth;
* notification processing latency;
* delivery failure rate;
* duplicate detection;
* unread count processing;
* worker failures.

Critical security or operational alerts require higher monitoring priority.

---

# 116. Testing Requirements

The API must test:

### Reports

* daily report;
* monthly report;
* Branch report;
* Business report;
* empty report;
* report generation;
* regeneration;
* Report Version creation;
* Report Version immutability;
* correction-triggered new Version.

### Exports

* XLSX generation;
* asynchronous processing;
* export status;
* file creation;
* file authorization;
* file expiration;
* retry;
* duplicate export prevention.

### Notifications

* creation;
* recipient isolation;
* Branch scope;
* Business scope;
* mark-read;
* unread count;
* deduplication;
* aggregation;
* retry;
* offline synchronization.

---

# 117. Security Testing

Security tests must verify:

* Business report isolation;
* Branch report isolation;
* payroll report confidentiality;
* inventory cost report confidentiality;
* file access authorization;
* expired file rejection;
* Notification recipient isolation;
* unauthorized notification access;
* export authorization;
* sensitive report access;
* subscription restrictions.

---

# 118. Historical Integrity Testing

Tests must verify:

```text
Report Version 1
      ≠
Report Version 2
```

when relevant source changes require a new version.

Also:

```text
Report Version
      ≠
Current cached report
```

and:

```text
File deletion
      ≠
Report Version deletion
```

---

# 119. Failure Recovery Testing

The system must test:

* report worker crash;
* XLSX worker crash;
* file storage outage;
* Redis/cache outage;
* notification worker crash;
* duplicate worker execution;
* transaction commit followed by notification failure;
* Report Version commit followed by export failure;
* export retry after completed file creation.

---

# 120. Endpoint Summary

### Reports

```text
GET    /reports
POST   /reports
GET    /reports/{id}
GET    /reports/{id}/status
POST   /reports/{id}/regenerate
GET    /reports/{id}/versions
GET    /reports/{id}/versions/{version_id}

GET    /reports/daily
GET    /reports/monthly
GET    /reports/branch-performance
```

### Exports

```text
POST   /reports/{report_id}/exports
GET    /exports/{export_id}
POST   /exports/{export_id}/cancel
```

### Files

```text
GET    /files/{file_id}
GET    /files/{file_id}/download
```

### Notifications

```text
GET    /notifications
GET    /notifications/{notification_id}
GET    /notifications/unread-count
POST   /notifications/{notification_id}/read
POST   /notifications/read-all
```

---

# 121. API Invariants

The following invariants apply to Report, File and Notification APIs:

1. Reports are Business-scoped.
2. Branch reports are Branch-scoped.
3. Report access is authorization-controlled.
4. Client-provided Business UUID is never authoritative.
5. Client-provided Branch UUID is never authoritative.
6. Report types are controlled by the server.
7. Unsupported report types are rejected.
8. Report periods are explicitly defined.
9. Date-only report periods use Business timezone rules.
10. Report list endpoints are bounded.
11. Report generation respects subscription entitlement.
12. Report Versions are immutable.
13. Historical Report Versions cannot be silently overwritten.
14. Current transactions cannot silently rewrite historical Report Versions.
15. A relevant correction may require a new Report Version.
16. Report Version creation records its source state.
17. Report Version creation identifies the report definition version where required.
18. Report regeneration does not delete previous versions.
19. Empty reports are valid report results.
20. Business-level reports aggregate only authorized Branches.
21. Branch-level reports cannot cross Branch scope.
22. Sensitive reports require appropriate permission.
23. Payroll reports require salary-sensitive authorization.
24. Inventory cost reports require cost visibility authorization.
25. Report cache is not authoritative historical state.
26. Cached report results cannot replace immutable Report Versions.
27. Large report generation is asynchronous.
28. XLSX generation is asynchronous for large exports.
29. Export Jobs have bounded lifecycle states.
30. Export Jobs use stable operation identity where idempotency is required.
31. Duplicate export requests must not create uncontrolled duplicate jobs.
32. An Export references a specific Report Version.
33. An exported File cannot reinterpret a Report Version.
34. File UUID alone does not grant access.
35. File download requires authorization.
36. File storage paths are never exposed as authoritative identifiers.
37. File credentials are never exposed through the API.
38. Temporary files may expire.
39. File expiration does not delete the Report Version.
40. File deletion does not delete source reports.
41. File integrity should be verifiable where required.
42. Report and File access remain Business-isolated.
43. Notification recipient ownership is server-authoritative.
44. Notification UUID alone does not grant access.
45. Notification lists are recipient-scoped.
46. Notification unread counts are recipient-scoped.
47. Notification read operations are idempotent.
48. Marking one notification read cannot modify another user's state.
49. Mark-all-read applies only to the authorized notification scope.
50. Notifications do not become authoritative transaction records.
51. Notification source references do not replace source records.
52. Important notifications are generated through controlled application/background workflows.
53. Clients cannot impersonate system-generated security notifications.
54. Notification creation is protected against duplicate worker execution.
55. Notification deduplication rules are explicit.
56. Notification aggregation cannot hide required critical alerts.
57. Notification delivery does not rollback committed business transactions.
58. Notification worker retries cannot create uncontrolled duplicates.
59. Security notifications do not expose sensitive credentials or security material.
60. Branch notifications remain Branch-scoped.
61. Business notifications remain Business-scoped.
62. Subscription notifications do not override subscription enforcement.
63. Low-stock notifications do not modify inventory.
64. Refund notifications do not modify refund state.
65. Inventory variance notifications do not modify inventory.
66. Report-triggered notifications do not modify the Report.
67. Offline notification copies are not authoritative.
68. Offline clients cannot manufacture authoritative notification events.
69. Notification synchronization preserves server identity.
70. Report export authorization remains resource-specific.
71. Possession of an old File URL does not automatically bypass authorization.
72. Sensitive file downloads are auditable where required.
73. Important report operations are auditable.
74. Report Version history remains reconstructable.
75. File lifecycle cannot destroy authoritative reporting history.
76. Notification retention cannot destroy source business history.
77. READ_ONLY subscription blocks prohibited report/export mutations.
78. READ_ONLY subscription does not delete historical reports.
79. Deleted Businesses cannot accept normal report mutations.
80. Deleted Business report access follows data lifecycle policy.
81. Report generation cannot monopolize POS resources.
82. XLSX generation cannot monopolize POS resources.
83. Background worker concurrency is bounded.
84. Report jobs have bounded resource consumption.
85. Export jobs have bounded resource consumption.
86. Large reports do not require unbounded application memory.
87. XLSX generation does not require unbounded application memory.
88. Report APIs remain within defined latency targets.
89. Notification APIs remain within defined latency targets.
90. Background report processing has measurable SLOs.
91. Notification processing has measurable SLOs.
92. Report metrics must avoid uncontrolled high-cardinality labels.
93. Notification metrics must avoid uncontrolled high-cardinality labels.
94. Report generation failures are observable.
95. Export failures are observable.
96. Notification delivery failures are observable.
97. File storage failures are distinguishable from report generation failures.
98. Cache failure cannot corrupt Report Versions.
99. Cache failure cannot authorize unauthorized File access.
100. Cache failure cannot expose another Employee's notifications.
101. Report APIs preserve Business isolation.
102. File APIs preserve Business isolation.
103. Notification APIs preserve Business isolation.
104. Report APIs preserve Branch isolation.
105. File access preserves Branch restrictions where applicable.
106. Notification APIs preserve Branch isolation where applicable.
107. API idempotency protects retryable report operations.
108. API idempotency protects retryable export operations.
109. API error codes remain stable.
110. API responses expose only authorized report data.
111. API responses expose only authorized file metadata.
112. API responses expose only authorized notification data.
113. Report Versions remain immutable.
114. Generated files remain associated with their source Report Version.
115. Notifications remain separate from authoritative transaction state.
116. Historical report integrity has priority over cache freshness.
117. File convenience has lower priority than authorization.
118. Notification convenience has lower priority than recipient isolation.
119. Report, File and Notification APIs preserve the modular monolith boundary.
120. Performance optimization must not weaken historical integrity, security or Business isolation.

---

# 122. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/17_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`

### Database

* `docs/05_Database/19_Notification_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/12_Reporting_and_Export_Architecture.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/14_API_Payment_Cash_and_Financial_Endpoints.md`
* `docs/04_Architecture/09_API/16_API_Employee_Attendance_and_Payroll_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`

---

# 123. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `17_API_Report_File_and_Notification_Endpoints.md`

**Previous Document:** `16_API_Employee_Attendance_and_Payroll_Endpoints.md`

**Next Document:** `18_API_Configuration_and_Subscription_Endpoints.md`

---

## Final Principle

> Report, File and Notification APIs must provide useful operational information without becoming an alternative source of truth. Report Versions preserve historical analytical state, Files provide controlled representations of generated content, and Notifications communicate important events while authoritative Business state remains in the underlying transactional domains.

