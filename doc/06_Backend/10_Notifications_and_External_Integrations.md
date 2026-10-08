# Notifications and External Integrations

**Document ID:** BE-10
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the backend architecture for:

* in-app notifications;
* notification generation;
* notification delivery;
* notification preferences;
* printer integrations;
* file storage;
* Excel exports;
* email integrations;
* future external service integrations;
* integration failures;
* retry behavior;
* integration security;
* external system boundaries;
* auditability.

The architecture must ensure that external systems cannot compromise the integrity of core FastFood ERP business transactions.

---

## 2. Core Principle

The system follows:

> External systems are secondary dependencies unless explicitly defined as part of a core business transaction.

For example:

```text id="ext001"
Order Acceptance
      ↓
Core transaction
      ↓
COMMIT
      ↓
Printer / Notification / Email
```

A printer, notification provider or email provider failure must not normally roll back an already committed Order.

---

# 3. Integration Categories

FastFood ERP distinguishes the following integration types:

```text
Internal Notification
Printer
File Storage
Excel Export
Email
External API
Future Payment Provider
Future Government Integration
Future Customer Platform
```

Each integration must have an explicit boundary.

---

# 4. Internal Notification

The initial notification system is primarily in-app.

Notifications may be generated for:

* low stock;
* out of stock;
* subscription expiration;
* salary due;
* large refund;
* large inventory variance;
* branch loss;
* cash discrepancy;
* correction request;
* security event;
* synchronization conflict;
* important system failure.

---

# 5. Notification Architecture

The notification flow is:

```text id="ntf001"
Business Event
      ↓
Outbox
      ↓
Notification Job
      ↓
Notification Service
      ↓
Notification Record
      ↓
User Interface
```

Notification creation must not normally block the core business transaction.

---

# 6. Notification Record

A notification record should contain information similar to:

```text id="ntf002"
notification_id
business_id
branch_id
recipient_employee_id
type
title
message
severity
reference_type
reference_id
created_at
read_at
status
```

Exact fields may evolve.

---

# 7. Notification Identity

Every notification must have a unique identifier.

The identifier should remain stable for its lifecycle.

---

# 8. Notification Types

Notification types should use stable machine-readable codes.

Examples:

```text
LOW_STOCK
OUT_OF_STOCK
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_EXPIRED
SALARY_DUE
LARGE_REFUND
INVENTORY_VARIANCE
BRANCH_LOSS
CASH_DISCREPANCY
CORRECTION_REQUEST
SYNC_CONFLICT
SECURITY_ALERT
```

The exact catalog may grow over time.

---

# 9. Notification Severity

Notifications may use severity levels such as:

```text
INFO
WARNING
IMPORTANT
CRITICAL
```

Severity must represent operational importance, not implementation failure.

---

# 10. Notification Recipient

Recipients are determined by business rules and permission/scope.

Examples:

```text id="ntf003"
Cash discrepancy
    ↓
Previous Cashier
    +
Owner / authorized employee
```

or:

```text id="ntf004"
Branch stock warning
    ↓
Authorized Branch employees
```

The system must not send notifications to employees outside the relevant Business or Branch scope.

---

# 11. Permission-Aware Notifications

A notification does not grant permission.

For example:

```text id="ntf005"
Employee receives:
"Inventory variance detected"
```

This does not automatically grant inventory-management permission.

The user must still pass authorization when opening or modifying the referenced resource.

---

# 12. Branch Scope

Branch-scoped notifications must contain Branch context.

A Branch A notification must not accidentally appear as a Branch B operational notification.

Business-level notifications may omit Branch scope when appropriate.

---

# 13. Notification Reference

Notifications should reference the relevant business object where useful.

Examples:

```text id="ntf006"
reference_type = CASH_SESSION
reference_id = UUID
```

or:

```text id="ntf007"
reference_type = ORDER
reference_id = UUID
```

The referenced object must still be authorization-checked when opened.

---

# 14. Notification Payload

The notification should store enough information to remain meaningful.

If historical information is important, a snapshot or immutable reference should be used.

Current mutable data must not silently change the meaning of an already-created historical notification.

---

# 15. Notification Creation

Notifications should normally be generated asynchronously through the Outbox.

Example:

```text id="ntf008"
Inventory Transaction
      ↓
COMMIT
      ↓
Outbox Event
      ↓
Notification Job
      ↓
Create Notification
```

---

# 16. Notification Failure

If notification creation or delivery fails:

```text id="ntf009"
Core Business State
      ↓
Remains committed
```

The notification job may retry independently.

---

# 17. Notification Idempotency

Repeated event processing must not create duplicate notifications where uniqueness is required.

A logical notification key may contain:

```text id="ntf010"
business_id
notification_type
reference_type
reference_id
recipient_employee_id
```

The exact uniqueness rule depends on the notification type.

---

# 18. Notification Read State

Reading a notification is separate from the underlying business event.

A user may:

* mark notification as read;
* leave it unread;
* open the referenced object.

Reading a notification must not modify the underlying business transaction.

---

# 19. Notification Retention

Notifications are operational data.

They may have a configurable retention period.

Retention cleanup must not delete:

* audit records;
* historical transactions;
* required compliance history.

---

# 20. Notification Preferences

Future versions may allow employees to configure notification preferences.

Preferences must not override mandatory security or operational notifications.

For example:

```text id="ntf011"
Security Alert
```

may remain mandatory even if ordinary notification preferences are disabled.

---

# 21. Email Integration

Email is considered a secondary delivery channel.

Example:

```text id="ntf012"
Business Event
      ↓
Outbox
      ↓
Notification / Email Job
      ↓
Email Provider
```

Email failure must not roll back the original business operation.

---

# 22. Email Provider Boundary

The application should use an abstraction such as:

```text
EmailService
```

rather than directly coupling business logic to a specific provider.

Conceptually:

```text id="ntf013"
Application
    ↓
Email Interface
    ↓
Provider Adapter
    ↓
External Email Provider
```

---

# 23. Email Provider Failure

Provider failure may be:

* timeout;
* connection failure;
* rate limit;
* authentication failure;
* rejected message;
* provider outage.

The integration layer classifies the failure and applies the appropriate retry policy.

---

# 24. Email Retry

Temporary failures may be retried.

Permanent failures should not be retried indefinitely.

Examples:

```text id="ntf014"
Provider timeout
→ Retry

Invalid recipient
→ Permanent failure

Provider rate limit
→ Delayed retry
```

---

# 25. Email Idempotency

Important emails should use a stable logical message identity where duplicate delivery would be problematic.

Example:

```text id="ntf015"
email_event_id = UUID
```

Provider-level idempotency should be used if supported.

---

# 26. Printer Integration

Printers are external operational devices.

They are not authoritative for Order state.

The architecture must treat printing as asynchronous secondary work.

---

# 27. Printer Flow

Example:

```text id="prt001"
Order Accepted
      ↓
COMMIT
      ↓
Print Job Created
      ↓
Printer Routing
      ↓
Target Printer
      ↓
Print Result
```

---

# 28. Printer Routing

Products may be routed to different printers.

Example:

```text id="prt002"
Pizza
  ↓
Pizza Printer

Lavash
  ↓
Lavash Printer

Drinks
  ↓
Drinks Printer
```

Routing configuration must be Business/Branch scoped.

---

# 29. Printer Configuration

Printer configuration may include:

* Branch;
* printer identity;
* connection type;
* address/port where applicable;
* product/category routing;
* active state;
* timeout;
* retry policy.

Sensitive connection credentials must be protected.

---

# 30. Printer Connection Types

The architecture should support common local printer connection models, such as:

* network printer;
* USB-connected printer through local print service;
* other supported local transport.

The backend should not assume that every printer is directly reachable from the cloud server.

---

# 31. Local Printer Agent

Where a printer is physically located inside a Branch and cannot be directly reached by the central backend, a local print agent may be used.

Conceptually:

```text id="prt003"
ERP Backend
      ↓
Print Job
      ↓
Branch Print Agent
      ↓
Local Printer
```

The print agent is responsible for local hardware communication.

---

# 32. Print Agent Trust

A local print agent must be authenticated as a trusted Branch device.

It must not be able to execute arbitrary Business operations.

Its permissions should be limited to its assigned print responsibilities.

---

# 33. Printer Failure

Possible printer failures:

* printer offline;
* connection refused;
* timeout;
* paper unavailable;
* device error;
* malformed print job;
* agent unavailable.

These failures must be visible to operators.

---

# 34. Printer Retry

Temporary printer failures may be retried.

Retry count must be bounded.

A permanently unavailable printer must move the job to a failed/dead-letter state rather than retrying forever.

---

# 35. Print Job Status

A print job may use:

```text
PENDING
PROCESSING
PRINTED
RETRYING
FAILED
CANCELLED
```

Exact state names may vary.

---

# 36. Duplicate Printing

Duplicate printing is a hardware integration problem.

The system must use stable print-job identifiers.

If the printer/agent cannot guarantee deduplication, the UI should make retry consequences clear.

---

# 37. Order State vs Print State

These states must remain separate.

Example:

```text
Order:
ACCEPTED

Print:
FAILED
```

The Order remains accepted.

The system may provide a retry-print action without changing Order state.

---

# 38. File Storage

File storage may be used for:

* Product images;
* report files;
* Excel exports;
* future documents.

The database stores metadata and references rather than large binary content where appropriate.

---

# 39. File Storage Abstraction

Application code should depend on a storage interface.

Conceptually:

```text id="fil001"
Application
    ↓
FileStorage Interface
    ↓
Local Storage / Object Storage
```

This allows future migration without rewriting business logic.

---

# 40. File Metadata

File metadata may include:

```text id="fil002"
file_id
business_id
branch_id
owner_type
owner_id
storage_key
file_name
content_type
size
checksum
created_at
status
```

---

# 41. File Ownership

Every Business-owned file must have a clear ownership relationship.

A file must not be accessible merely because its storage key is known.

Authorization must be checked before serving the file.

---

# 42. File Access

File access must validate:

1. authenticated identity;
2. Business scope;
3. Branch scope where applicable;
4. resource ownership;
5. permission.

Direct uncontrolled public storage URLs should not be used for sensitive files.

---

# 43. Product Images

Product images are configuration data.

Changing an image must not change Product identity.

Historical transactions do not need to be recalculated because a Product image changed.

---

# 44. Excel Export

Excel export is a background operation.

Example:

```text id="xls001"
User requests export
      ↓
Create Export Job
      ↓
Worker generates XLSX
      ↓
Store file
      ↓
Mark export READY
      ↓
User downloads file
```

---

# 45. Export Failure

If export generation fails:

* business state remains unchanged;
* report state remains unchanged;
* export job may retry;
* failed export is visible to the user;
* temporary files are cleaned up.

---

# 46. Export Authorization

Export permission must be checked when the export is requested.

The generated file must also remain protected after generation.

A user must not gain access to another Business's export by guessing a file ID.

---

# 47. Export Audit

Important exports should be auditable.

Audit may contain:

```text id="xls002"
employee_id
business_id
branch_scope
report_type
period
export_type
timestamp
result
```

---

# 48. Export Data Snapshot

Exports must use the correct report or data snapshot.

If an export is generated from a versioned report:

```text id="xls003"
Report Version 7
      ↓
Excel Export
      ↓
Same Report Version 7
```

The export must not silently use a different report version.

---

# 49. External API Integration

Future external APIs should be accessed through dedicated adapters.

Business logic should not directly call third-party HTTP APIs.

Conceptually:

```text id="api001"
Application
      ↓
Integration Interface
      ↓
External Adapter
      ↓
HTTP/API
```

---

# 50. External API Timeout

Every external request must have a defined timeout.

An external provider must never be allowed to block a core transaction indefinitely.

---

# 51. External API Retry

Retries should occur only when the operation is safely retryable.

Examples:

```text id="api002"
GET request timeout
→ Usually retryable

POST payment without idempotency
→ Must not blindly retry

Provider rate limit
→ Delayed retry
```

---

# 52. External API Idempotency

For external commands that may change state, the integration should use an idempotency key where supported.

Example:

```text id="api003"
operation_id
      ↓
External Idempotency-Key
```

This protects against duplicate external actions after network failures.

---

# 53. External API Response

External responses must be translated into internal application models.

Do not expose provider-specific response structures directly throughout the application.

---

# 54. External API Errors

Provider errors should be classified as:

```text
Authentication Failure
Validation Failure
Rate Limit
Temporary Failure
Permanent Failure
Conflict
Unknown Failure
```

The integration adapter translates them into internal error types.

---

# 55. External Integration Security

External integrations must protect:

* API keys;
* access tokens;
* client secrets;
* certificates;
* private keys.

Secrets must not be stored in source code.

---

# 56. Secret Management

Secrets should be supplied through secure configuration/secret management.

Examples:

```text id="sec001"
Environment Secret
Secret Manager
Encrypted Configuration
```

The exact mechanism depends on deployment architecture.

---

# 57. Secret Rotation

External credentials should support rotation without requiring application code changes.

Old credentials should be revoked when appropriate.

---

# 58. External Integration Logging

Logs may include:

* provider;
* operation ID;
* request ID;
* endpoint category;
* duration;
* result;
* error category.

Logs must not contain:

* API keys;
* access tokens;
* full authorization headers;
* unnecessary personal data.

---

# 59. External Integration Observability

The system should track:

* request count;
* success rate;
* failure rate;
* latency;
* timeout count;
* retry count;
* rate-limit count;
* provider availability.

---

# 60. Integration Circuit Protection

If an external provider repeatedly fails, the system should avoid creating excessive load.

A circuit-breaker or equivalent protection may be introduced where justified.

The core application must remain usable when the external provider is unavailable.

---

# 61. External Integration and Transactions

Never perform an unnecessary external call inside a core database transaction.

Bad:

```text id="api004"
BEGIN
  ↓
Update Order
  ↓
Call External API
  ↓
Wait
  ↓
COMMIT
```

Preferred:

```text id="api005"
BEGIN
  ↓
Update Order
  ↓
Create Outbox
  ↓
COMMIT
      ↓
Worker
      ↓
External API
```

---

# 62. When External Integration Is Core

Some future integrations may be defined as part of a business transaction.

If so, the architecture must explicitly define:

* timeout;
* failure behavior;
* compensation;
* idempotency;
* reconciliation;
* audit;
* retry policy.

The integration must never become an accidental synchronous dependency.

---

# 63. Compensation

Some external operations cannot be rolled back.

Example:

```text id="api006"
ERP → External Provider
       ↓
Success
       ↓
ERP crashes before recording result
```

The system must reconcile the external state using the original operation ID rather than blindly sending a duplicate command.

---

# 64. Integration Reconciliation

Reconciliation may compare:

```text id="api007"
Internal State
      ↕
External State
```

Differences must be recorded and resolved explicitly.

---

# 65. Integration Health

Each important integration should expose health information.

Examples:

```text
Printer Agent: Healthy
Email Provider: Healthy
Storage: Healthy
External API: Degraded
```

Health checks must not expose secrets.

---

# 66. Health Check Types

The system should distinguish:

### Liveness

Is the process running?

### Readiness

Can it process requests?

### Dependency Health

Can required infrastructure be reached?

External provider availability should not necessarily make the whole API unready if the integration is non-critical.

---

# 67. Graceful Degradation

When a secondary integration fails, the system should continue operating where possible.

Examples:

```text id="gd001"
Notification unavailable
→ Core POS continues

Printer unavailable
→ Order remains accepted

Email unavailable
→ In-app notification remains available

Excel generation unavailable
→ Report remains available
```

---

# 68. Integration Queue Isolation

A large backlog in one integration should not block unrelated work.

For example:

```text id="gd002"
Printer Queue overloaded
```

must not stop:

```text
Order API
Cash API
Inventory API
```

from operating normally.

---

# 69. Worker Isolation by Job Type

Where workload justifies it, workers may be separated by job type:

```text id="wrk001"
Notification Worker
Print Worker
Report Worker
Sync Worker
Maintenance Worker
```

Initially these may run in one worker process with logical queues.

---

# 70. Integration Rate Limits

Each external provider may have its own rate limit.

The adapter should handle provider-specific rate limits without leaking provider implementation into business logic.

---

# 71. Integration Configuration

Integration settings must be scoped correctly.

Examples:

```text
Business-level:
Email configuration

Branch-level:
Printer configuration

Platform-level:
Global provider configuration
```

Configuration must not cross Business boundaries.

---

# 72. Branch Printer Isolation

A Branch printer must only process jobs belonging to its assigned Branch.

Example:

```text id="prt004"
Branch A Print Job
       ↓
Branch A Printer Agent
```

Branch B must not receive the job.

---

# 73. Device Trust and Print Agents

A print agent is a trusted device category.

It should have:

* unique Device UUID;
* secure authentication;
* revocation;
* Branch association;
* limited permissions;
* audit context.

A revoked print agent must not process new jobs.

---

# 74. Offline Print Agent

If Branch operations support offline printing:

* print jobs may be queued locally;
* job identifiers must remain stable;
* duplicate handling must be considered;
* synchronization must report success/failure;
* the server remains authoritative for business state.

---

# 75. Integration with Offline POS

Offline POS operations must not depend on real-time external APIs.

Core offline operations should remain available within the approved offline authorization rules.

Secondary integration work may be queued for later processing.

---

# 76. Notification and Offline Operation

Offline-generated business events may result in notifications after synchronization.

The system must not create duplicate notifications merely because the event was synchronized more than once.

---

# 77. Integration Audit

Important external operations should be auditable.

Audit context may include:

```text id="aud001"
integration_type
provider
operation_id
event_id
business_id
branch_id
employee_id
device_id
result
timestamp
```

Secrets must never be included.

---

# 78. Integration Error Handling

Integration errors should use the common backend error architecture.

See:

`08_Error_Handling_and_Exception_Architecture.md`

External-specific errors are translated into internal stable error categories.

---

# 79. Integration Retry and Outbox

The normal flow is:

```text id="int001"
Business Transaction
      ↓
Outbox
      ↓
Background Job
      ↓
Integration Adapter
      ↓
External System
```

This ensures external integrations do not compromise core transaction integrity.

---

# 80. Integration Cancellation

Where supported, queued work may be cancelled before execution.

Already completed external operations must not be represented as cancelled merely because the local job was later cancelled.

---

# 81. Integration Timeout

Every external integration must have explicit timeout behavior.

Timeout must produce a classified result:

```text
TIMEOUT_RETRYABLE
```

or another appropriate internal error.

No external call may wait indefinitely.

---

# 82. Integration Result Storage

Where the external response is relevant to future reconciliation, store:

* operation ID;
* external reference;
* result;
* timestamp;
* provider;
* status.

Do not store unnecessary provider response data.

---

# 83. External Reference

If an external provider creates its own identifier, it should be stored separately from the internal UUID.

Example:

```text
Internal Operation UUID
        ↓
External Reference ID
```

The two identifiers must not be confused.

---

# 84. Provider Abstraction

Business logic must not contain provider-specific code.

Bad:

```python id="bad001"
if provider == "SomeProvider":
    ...
```

inside the Order or Payment domain.

Preferred:

```text id="good001"
Application
   ↓
Integration Interface
   ↓
Provider Adapter
```

---

# 85. Provider Switching

The system should be able to replace an external provider without rewriting core business logic.

Provider-specific behavior belongs inside the adapter.

---

# 86. External Integration Testing

Each integration should support:

### Unit Tests

* request mapping;
* response mapping;
* error classification;
* retry classification.

### Integration Tests

* real or sandbox provider;
* authentication;
* timeout;
* rate limit;
* duplicate request.

### Failure Tests

* provider unavailable;
* network timeout;
* malformed response;
* partial failure;
* duplicate response.

---

# 87. Printer Testing

Printer integration should be tested separately from Order business logic.

Test:

* routing;
* connection failure;
* timeout;
* retry;
* duplicate print;
* agent revocation;
* Branch isolation.

---

# 88. Notification Testing

Test:

* recipient selection;
* Branch scope;
* permission boundaries;
* duplicate prevention;
* read state;
* retry;
* retention.

---

# 89. Export Testing

Test:

* authorization;
* report version selection;
* XLSX generation;
* large report handling;
* failure recovery;
* file access;
* cleanup.

---

# 90. External API Testing

Test:

* authentication;
* idempotency;
* timeout;
* rate limits;
* retry;
* provider errors;
* reconciliation.

---

# 91. Performance

External integrations must not degrade normal POS performance.

The POS path should not wait for:

* notification delivery;
* email delivery;
* report generation;
* XLSX generation;
* printer response;
* non-critical external API calls.

---

# 92. Resource Limits

Background integrations must have controlled:

* worker concurrency;
* retry counts;
* queue size;
* payload size;
* external request timeout;
* memory usage.

A single integration must not consume all server resources.

---

# 93. Integration Backpressure

If an integration queue grows significantly:

* new work may be delayed;
* concurrency may be reduced;
* alerts may be generated;
* retries may be slowed.

The core application must remain protected.

---

# 94. Data Privacy

Only required data should be sent to external systems.

Before integration, the system should determine:

* what data is necessary;
* why it is necessary;
* whether Business authorization permits the transfer;
* how long external systems retain it.

---

# 95. External Data Ownership

The FastFood ERP remains authoritative for its own business records.

External systems may contain copies or references.

An external provider must not silently become the source of truth for internal business state unless explicitly designed as such.

---

# 96. Integration Versioning

Integration adapters should be version-aware where provider APIs evolve.

Provider API changes must not silently change business behavior.

---

# 97. Integration Failure Recovery

Recovery may use:

```text id="rec001"
Retry
Reconciliation
Manual Retry
Manual Reconciliation
Provider Switch
Dead Letter
```

The chosen mechanism depends on the integration.

---

# 98. Operational Dashboard

The backend should provide operational visibility for important integrations.

Useful metrics:

* pending notifications;
* failed notifications;
* pending print jobs;
* failed print jobs;
* export backlog;
* failed exports;
* external API failures;
* retry counts;
* dead-letter count.

---

# 99. Architecture Summary

The integration architecture is:

```text
                ┌─────────────────────┐
                │   Core ERP State    │
                │     PostgreSQL      │
                └──────────┬──────────┘
                           │
                      Transaction
                           │
                     ┌─────▼─────┐
                     │  Outbox   │
                     └─────┬─────┘
                           │
                    Background Jobs
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Notification         Printer          Report/Export
        │                  │                  │
   In-App/Email      Print Agent       File Storage
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    External Systems
```

The core ERP state remains authoritative.

---

# 100. System Invariants

1. External integrations do not normally determine core ERP transaction success.
2. Core business transactions are committed before secondary integrations execute.
3. Required Outbox events are created in the same transaction as their business state changes.
4. Notification failure does not normally roll back committed business state.
5. Printer failure does not roll back committed Orders.
6. Email failure does not roll back committed business operations.
7. Report generation failure does not corrupt report history.
8. Export failure does not corrupt operational data.
9. External calls do not unnecessarily remain inside core database transactions.
10. Every important integration operation has a stable operation identifier.
11. Provider-specific identifiers remain separate from internal UUIDs.
12. External provider errors are translated into internal error categories.
13. External credentials are never stored in source code.
14. External credentials are never written to ordinary logs.
15. External calls have explicit timeouts.
16. Retry policies are bounded.
17. Non-retryable failures are not retried indefinitely.
18. External state-changing commands use idempotency where supported and required.
19. Integration handlers are duplicate-safe where at-least-once processing applies.
20. Printer jobs have stable identifiers.
21. Printer routing is Branch-scoped.
22. A Branch printer cannot process another Branch's job.
23. Revoked print agents cannot process new authorized jobs.
24. Notification recipients are validated against Business and Branch scope.
25. Notifications do not grant permissions.
26. Opening a referenced notification resource requires normal authorization.
27. Export files remain protected after generation.
28. Export authorization is checked before file access.
29. Historical report versions remain immutable.
30. External systems do not silently rewrite internal historical transactions.
31. Background integrations respect Business lifecycle state.
32. Background integrations cannot resurrect deleted Businesses.
33. Offline POS does not depend on real-time external APIs for core operation.
34. Integration failures remain observable.
35. Dead-letter operations remain recoverable.
36. Manual recovery is auditable.
37. Integration queues cannot indefinitely block core POS operations.
38. One integration must not consume unlimited system resources.
39. Sensitive data is minimized before external transmission.
40. Business boundaries are preserved for every integration.
41. Branch boundaries are preserved for every Branch-scoped integration.
42. Provider implementations remain outside domain business logic.
43. Provider replacement should not require rewriting core business rules.
44. External provider outages should result in graceful degradation where possible.
45. Integration state and business state remain conceptually separate.
46. External integration success must not be assumed solely from a network response when reconciliation is required.
47. Integration architecture must remain compatible with future external services without coupling the core domain to them.

---

# 101. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `08_Error_Handling_and_Exception_Architecture.md`
* `09_Events_Outbox_and_Background_Jobs.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/19_Notification_Data_Model.md`
* `../05_Database/20_Audit_and_History_Data_Model.md`
* `../05_Database/21_Report_and_Report_Version_Data_Model.md`
* `../05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `../05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `../05_Database/29_Database_Security.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `../02_System_Analysis/18_Notifications_and_Alerts.md`
* `../02_System_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `../02_System_Analysis/22_Audit_and_History.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `../02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

---

# 102. Status

**Document ID:** BE-10

**Document Status:** Accepted

**Notification Model:** In-App First, Asynchronous Delivery

**Integration Model:** Adapter-Based

**Printer Model:** Asynchronous Print Jobs

**Export Model:** Background Generation

**External API Model:** Isolated Provider Adapters

**Transaction Principle:** Core State First, Secondary Integration After Commit

**Failure Model:** Retry + Dead Letter + Reconciliation

**Security Principle:** External Systems Never Bypass Business Authorization

**Next Document:** `11_Configuration_and_Environment_Management.md`

