# API Employee, Attendance and Payroll Endpoints

**Document ID:** API-16
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the public API contract for Employee, Role, Permission, Attendance and Payroll operations in FastFood ERP.

The API must support:

* employee lifecycle management;
* employee-to-Business membership;
* Branch assignment;
* role assignment;
* permission configuration;
* employee permission overrides;
* attendance recording;
* attendance corrections;
* work schedules where applicable;
* payroll calculation;
* salary structures;
* bonuses;
* deductions;
* payroll periods;
* payroll finalization;
* payroll history;
* employee salary visibility;
* offline attendance compatibility.

The API must preserve employee identity, authorization boundaries and historical payroll integrity.

---

# 2. Scope

This document covers:

* Employee endpoints;
* employee activation/deactivation;
* employee Branch assignments;
* Role endpoints;
* Permission endpoints;
* employee permission overrides;
* Manager authority;
* Attendance endpoints;
* attendance correction;
* attendance approval where required;
* payroll configuration;
* salary structures;
* fixed salary;
* percentage-based salary;
* shift-based salary;
* daily salary;
* hybrid salary;
* bonuses;
* deductions;
* payroll periods;
* payroll calculation;
* payroll finalization;
* payroll payment state;
* payroll history;
* payroll corrections;
* employee salary visibility;
* Business and Branch isolation;
* subscription restrictions;
* offline attendance;
* synchronization;
* idempotency;
* concurrency;
* audit;
* historical integrity;
* performance and SLOs.

Generic API authentication, authorization, validation, error handling, idempotency and pagination are defined by the preceding API documents.

---

# 3. Architectural Position

The API follows the standard application architecture:

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
Domain Rules
   ↓
Repository
   ↓
PostgreSQL
```

The API must not directly modify Employee, Attendance or Payroll database records.

---

# 4. Resource Model

The primary resources are:

```text
Business
   ↓
Employee
   ├── Branch Assignment
   ├── Role
   ├── Permission Override
   ├── Attendance
   └── Payroll
         ├── Payroll Period
         ├── Earnings
         ├── Bonus
         └── Deduction
```

An Employee belongs to a Business context.

An Employee may work in multiple Branches.

Branch-specific permissions and operational context are evaluated separately.

---

# 5. Employee Resource

An Employee represents a person authorized to perform Business operations.

Example:

```json
{
  "id": "018f...",
  "employee_number": "EMP-001",
  "name": "Employee",
  "status": "ACTIVE"
}
```

The Employee UUID is not an authentication credential.

---

# 6. Employee Creation

Endpoint:

```http
POST /api/v1/employees
```

Example request:

```json
{
  "name": "Employee",
  "phone": "+998901234567",
  "employee_number": "EMP-001"
}
```

The server determines:

* Business ownership;
* initial status;
* Employee UUID;
* creation timestamp.

The client cannot create an Employee in another Business.

---

# 7. Employee Read

Endpoint:

```http
GET /api/v1/employees/{employee_id}
```

The response may include:

* Employee identity;
* status;
* Branch assignments;
* role information;
* employment metadata;
* relevant operational configuration.

Sensitive salary and permission information must only be returned when authorized.

---

# 8. Employee List

Endpoint:

```http
GET /api/v1/employees
```

Supported filters may include:

```text
status
branch_id
role_id
search
employee_number
```

Results must respect Business and Branch scope.

Large results use bounded pagination.

---

# 9. Employee Update

Endpoint:

```http
PATCH /api/v1/employees/{employee_id}
```

Allowed fields depend on permission and employee state.

The endpoint must not allow arbitrary modification of:

* historical attendance;
* finalized payroll;
* audit records;
* historical salary calculations.

Business operations requiring special lifecycle changes use explicit commands.

---

# 10. Employee Activation

Endpoint:

```http
POST /api/v1/employees/{employee_id}/activate
```

The operation requires appropriate permission.

Activation does not automatically assign:

* Branches;
* roles;
* permissions;
* devices.

These remain separate configuration operations.

---

# 11. Employee Deactivation

Endpoint:

```http
POST /api/v1/employees/{employee_id}/deactivate
```

After deactivation:

* new protected operations are blocked;
* new attendance operations are blocked unless explicitly allowed for correction workflows;
* new payroll configuration changes are blocked;
* historical records remain available.

Historical attendance and payroll records remain attributed to the Employee.

---

# 12. Employee Branch Assignment

Endpoint:

```http
GET /api/v1/employees/{employee_id}/branches
```

Assignment mutation:

```http
POST /api/v1/employees/{employee_id}/branches
```

Removal:

```http
DELETE /api/v1/employees/{employee_id}/branches/{branch_id}
```

The server must validate that the Branch belongs to the same Business.

---

# 13. Branch Assignment Rules

An Employee may work in multiple Branches.

Example:

```text
Employee A
 ├── Branch 1
 └── Branch 2
```

The Employee may have different operational permissions in each Branch.

Branch assignment does not automatically grant every Branch permission.

---

# 14. Branch Assignment Removal

An Employee must not be removed from a Branch if doing so would invalidate historical attribution.

The assignment may be deactivated or ended while preserving historical records.

Historical attendance and payroll remain associated with the original Branch context.

---

# 15. Role Resource

A Role represents a reusable permission configuration.

Typical endpoints:

```http
GET   /api/v1/roles
POST  /api/v1/roles
GET   /api/v1/roles/{role_id}
PATCH /api/v1/roles/{role_id}
POST  /api/v1/roles/{role_id}/archive
```

Role configuration is Business-scoped unless explicitly defined as platform-level.

---

# 16. Role Assignment

Endpoint:

```http
POST /api/v1/employees/{employee_id}/roles
```

Example:

```json
{
  "role_id": "018f...",
  "branch_id": "018f..."
}
```

The server validates:

* Employee scope;
* Role scope;
* Branch scope;
* assigning employee authority;
* subscription entitlement.

---

# 17. Role Removal

Endpoint:

```http
DELETE /api/v1/employees/{employee_id}/roles/{role_id}
```

Where historical authorization attribution is required, the role assignment is ended rather than physically erased.

Historical operations remain attributable to the permissions applicable at the time.

---

# 18. Permission Model

Effective permissions are derived from:

```text
Role Permission
+
Employee Permission Override
+
Branch Scope
+
Employee Status
+
Subscription Entitlement
+
Operational Rules
```

The API must not allow the client to directly declare itself authorized.

---

# 19. Employee Permission Overrides

Endpoint:

```http
GET /api/v1/employees/{employee_id}/permissions
```

Override creation:

```http
POST /api/v1/employees/{employee_id}/permission-overrides
```

Removal:

```http
DELETE /api/v1/employees/{employee_id}/permission-overrides/{permission}
```

The server validates the authority of the actor making the change.

---

# 20. Manager Permission Authority

A Manager cannot grant permissions beyond their own authority.

The server must compare:

```text
Actor Effective Authority
        vs
Requested Permission
```

If the requested permission exceeds the actor's authority:

```text
403 ACCESS_DENIED
```

The frontend must not be relied upon for this restriction.

---

# 21. Bulk Permission Updates

Where supported:

```http
POST /api/v1/employees/permissions/bulk-update
```

The operation must:

* have a bounded number of Employees;
* validate each Employee;
* validate actor authority;
* preserve Branch scope;
* produce auditable changes.

A large unbounded permission update is prohibited.

---

# 22. Permission Change Versioning

Permission configuration changes should expose a version.

Example:

```json
{
  "permission_version": 8
}
```

Changes invalidate or update relevant authorization caches.

Historical business operations remain attributable to the Employee and context that existed at the time.

---

# 23. Attendance Resource

Attendance records represent an Employee's work attendance.

An attendance record may contain:

```text
Employee
Business
Branch
Work Date
Clock In
Clock Out
Source
Status
Correction State
```

Server timestamps are authoritative for online events.

---

# 24. Attendance Endpoint

Clock-in:

```http
POST /api/v1/attendance/clock-in
```

Example:

```json
{
  "branch_id": "018f..."
}
```

The server determines the Employee from authenticated context.

The client must not submit another Employee UUID to impersonate another worker.

---

# 25. Clock-Out

Endpoint:

```http
POST /api/v1/attendance/clock-out
```

The server identifies the active attendance record.

The operation must validate:

* Employee;
* Business;
* Branch;
* attendance state;
* device/session context where required.

---

# 26. Attendance Read

Current Employee:

```http
GET /api/v1/attendance/me
```

Specific record:

```http
GET /api/v1/attendance/{attendance_id}
```

List:

```http
GET /api/v1/attendance
```

The list endpoint must respect authorization and Branch scope.

---

# 27. Attendance Filters

Supported filters may include:

```text
employee_id
branch_id
from
to
status
source
correction_status
```

Access to another Employee's attendance requires appropriate permission.

---

# 28. Attendance Status

Initial attendance states may include:

```text
OPEN
COMPLETED
MISSED
CORRECTED
CANCELLED
```

The Domain controls valid transitions.

Clients must not arbitrarily assign attendance status through generic PATCH.

---

# 29. Duplicate Clock-In

An Employee must not create multiple active attendance records for the same operational context unless the Business explicitly permits multiple shifts.

A duplicate request should be idempotent where the same operation UUID is reused.

Possible error:

```text
ATTENDANCE_ALREADY_OPEN
```

---

# 30. Clock-Out Without Clock-In

A clock-out without a valid active attendance record is rejected.

Possible error:

```text
NO_ACTIVE_ATTENDANCE
```

The system must not silently create a missing clock-in record.

---

# 31. Attendance Correction

Endpoint:

```http
POST /api/v1/attendance/{attendance_id}/corrections
```

Example:

```json
{
  "clock_in": "2026-10-07T08:00:00Z",
  "clock_out": "2026-10-07T17:00:00Z",
  "reason": "Forgot to clock in"
}
```

Correction requires:

* permission;
* reason;
* valid Employee/Branch context;
* business rule validation.

---

# 32. Attendance Correction History

Corrections must not silently overwrite the original attendance event.

The system should preserve:

```text
Original Attendance
      ↓
Correction
      ↓
Corrected Effective Attendance
```

The correction must be auditable.

---

# 33. Attendance Approval

If Business rules require approval:

```http
POST /api/v1/attendance/{attendance_id}/corrections/{correction_id}/approve
```

Rejection:

```http
POST /api/v1/attendance/{attendance_id}/corrections/{correction_id}/reject
```

Approval requires appropriate authority.

---

# 34. Attendance Source

Attendance may identify its source:

```text
ONLINE
OFFLINE
ADMIN_CORRECTION
IMPORT
SYSTEM
```

The source is historical metadata.

It must not change the underlying attendance rules.

---

# 35. Offline Attendance

Trusted devices may record authorized attendance operations while offline where Business policy allows.

Offline operation must include:

```text
operation_id
device_id
employee_id
branch_id
client_created_at
operation_type
```

The server validates the operation during synchronization.

---

# 36. Offline Attendance Authorization

An offline device cannot create a new trusted Employee identity.

Offline attendance requires:

* previously trusted device;
* valid offline authorization;
* valid Employee/device relationship;
* non-expired authorization;
* valid Branch scope.

A new device cannot bootstrap offline attendance.

---

# 37. Attendance Synchronization

Duplicate offline attendance operations must not create duplicate records.

The synchronization contract follows:

`19_API_Offline_Synchronization_and_Reconciliation.md`

The server remains authoritative after synchronization.

---

# 38. Attendance Time Integrity

Online server timestamps are authoritative for important attendance events.

Offline client timestamps may be retained as metadata.

The server must detect suspicious:

* clock rollback;
* impossible sequence;
* invalid future timestamps;
* expired offline authorization.

---

# 39. Attendance and Branch Context

Attendance records retain the Branch where the attendance operation occurred.

Changing an Employee's current Branch assignment must not rewrite historical attendance.

---

# 40. Attendance Reports

Endpoint:

```http
GET /api/v1/attendance/reports
```

Possible filters:

```text
employee_id
branch_id
period
status
```

Large reports should use asynchronous report processing where required.

The report API follows:

`17_API_Report_File_and_Notification_Endpoints.md`

---

# 41. Payroll Resource

Payroll represents compensation calculated for an Employee over a defined payroll period.

A payroll record may contain:

```text
Employee
Business
Branch
Period
Salary Structure
Base Earnings
Bonuses
Deductions
Adjustments
Gross Amount
Net Amount
Status
```

---

# 42. Payroll Period

Typical endpoints:

```http
GET  /api/v1/payroll/periods
POST /api/v1/payroll/periods
GET  /api/v1/payroll/periods/{period_id}
POST /api/v1/payroll/periods/{period_id}/close
```

A payroll period must have deterministic start and end dates.

---

# 43. Payroll Period States

Initial states:

```text
OPEN
CALCULATING
CALCULATED
FINALIZED
CLOSED
```

The Domain controls state transitions.

Finalized payroll cannot be silently recalculated.

---

# 44. Salary Configuration

Salary configuration may support:

```text
FIXED
PERCENTAGE
SHIFT
DAILY
HYBRID
```

The salary structure must be explicit.

---

# 45. Fixed Salary

A fixed salary represents a configured amount for the relevant payroll period.

Example:

```json
{
  "type": "FIXED",
  "amount": "5000000.00"
}
```

The server validates the amount and effective period.

---

# 46. Percentage Salary

Percentage salary may be based on an explicitly defined Business metric.

Example:

```json
{
  "type": "PERCENTAGE",
  "percentage": "5.00"
}
```

The API must not allow the client to define an arbitrary calculation base.

The Domain determines the authoritative base.

---

# 47. Shift Salary

Shift-based compensation may be configured as:

```json
{
  "type": "SHIFT",
  "amount_per_shift": "100000.00"
}
```

Payroll calculation uses authoritative attendance/shift data.

Client-provided shift counts are not authoritative.

---

# 48. Daily Salary

Daily salary may be configured as:

```json
{
  "type": "DAILY",
  "amount_per_day": "120000.00"
}
```

The calculation uses authoritative attendance/business rules.

---

# 49. Hybrid Salary

Hybrid salary combines supported components.

Example:

```text
Fixed Base
+
Shift Earnings
+
Percentage Component
+
Bonuses
-
Deductions
```

The server must calculate the authoritative result.

The client must not submit a final net salary as an authoritative value.

---

# 50. Salary Configuration Endpoint

Endpoint:

```http
GET /api/v1/employees/{employee_id}/salary
```

Configuration mutation:

```http
PUT /api/v1/employees/{employee_id}/salary
```

The response must respect salary visibility permissions.

---

# 51. Salary Effective Dates

Salary configuration changes should have an effective period.

A new salary configuration must not retroactively modify finalized payroll.

Example:

```text
Salary Version 3
Effective: October 1

Payroll September
→ Version 2

Payroll October
→ Version 3
```

---

# 52. Salary Versioning

Salary configurations should be versioned when changes affect payroll calculation.

A salary version should preserve:

* configuration;
* effective date;
* creator;
* approval where required;
* Business;
* Employee;
* Branch scope where applicable.

---

# 53. Bonus Resource

Bonuses are separate payroll adjustments.

Endpoint:

```http
POST /api/v1/payroll/{payroll_id}/bonuses
```

Example:

```json
{
  "amount": "300000.00",
  "reason": "Performance bonus"
}
```

The server validates:

* permission;
* Employee;
* payroll period;
* amount;
* Business scope.

---

# 54. Bonus Removal

A committed bonus must not be silently deleted from finalized payroll.

Before finalization, a permitted correction may modify the draft payroll calculation.

After finalization, a separate correction/adjustment must be created.

---

# 55. Deduction Resource

Endpoint:

```http
POST /api/v1/payroll/{payroll_id}/deductions
```

Example:

```json
{
  "amount": "100000.00",
  "reason": "Approved deduction"
}
```

The deduction must be permission-controlled and auditable.

---

# 56. Payroll Calculation

Endpoint:

```http
POST /api/v1/payroll/periods/{period_id}/calculate
```

The calculation uses authoritative:

* salary configuration;
* attendance;
* approved bonuses;
* deductions;
* relevant Business rules.

The client does not provide the authoritative final amount.

---

# 57. Payroll Calculation Result

Example:

```json
{
  "period_id": "018f...",
  "status": "CALCULATED",
  "employee_count": 24,
  "total_gross": "120000000.00",
  "total_deductions": "5000000.00",
  "total_net": "115000000.00"
}
```

Sensitive Employee-level salary details require appropriate authorization.

---

# 58. Employee Payroll Read

Endpoint:

```http
GET /api/v1/employees/{employee_id}/payroll
```

Employees may only see their own payroll unless explicitly authorized to see others.

Owner and authorized payroll users may access broader Business-scoped data.

---

# 59. Payroll List

Endpoint:

```http
GET /api/v1/payroll
```

Filters may include:

```text
employee_id
branch_id
period_id
status
from
to
```

The server enforces salary visibility and Branch scope.

---

# 60. Payroll Finalization

Endpoint:

```http
POST /api/v1/payroll/{payroll_id}/finalize
```

Finalization means the calculation becomes an authoritative historical payroll result.

Before finalization the server must validate:

* salary version;
* attendance completeness;
* approved bonuses;
* deductions;
* calculation integrity;
* Employee state;
* authorization.

---

# 61. Payroll Finalization Integrity

After finalization:

* original payroll amounts are immutable;
* salary configuration changes do not rewrite it;
* attendance changes do not silently rewrite it;
* current Employee role does not reinterpret it.

Corrections require explicit adjustment mechanisms.

---

# 62. Payroll Payment State

Where payroll payment tracking is included, states may include:

```text
UNPAID
PARTIALLY_PAID
PAID
```

Payment processing itself follows the financial architecture.

Payroll payment must not be confused with payroll calculation.

---

# 63. Payroll Payment Endpoint

Where supported:

```http
POST /api/v1/payroll/{payroll_id}/payments
```

The endpoint validates:

* payroll state;
* amount;
* payment authority;
* duplicate payment prevention;
* Business scope.

Financial payment rules follow:

`14_API_Payment_Cash_and_Financial_Endpoints.md`

---

# 64. Payroll Corrections

Finalized payroll must not be edited directly.

Correction endpoint:

```http
POST /api/v1/payroll/{payroll_id}/corrections
```

Example:

```json
{
  "reason": "Approved attendance correction",
  "adjustment_amount": "150000.00"
}
```

The correction becomes a separate historical event.

---

# 65. Payroll Correction Approval

Where required:

```http
POST /api/v1/payroll/{payroll_id}/corrections/{correction_id}/approve
```

The approval must be performed by an authorized actor.

---

# 66. Payroll Historical Integrity

Historical payroll must preserve:

```text
Employee
Branch
Payroll Period
Salary Version
Attendance Basis
Bonuses
Deductions
Gross Amount
Net Amount
Finalization State
Correction History
```

Current configuration must not reinterpret historical payroll.

---

# 67. Attendance and Payroll Relationship

Payroll may use attendance as a calculation input.

However:

```text
Attendance
   ↓
Payroll Calculation
```

does not mean payroll owns or mutates attendance.

Attendance remains its own authoritative domain resource.

---

# 68. Attendance Correction and Payroll

If attendance changes before payroll finalization:

```text
Attendance Correction
      ↓
Payroll Recalculation
```

may be permitted.

If payroll is already finalized:

```text
Attendance Correction
      ↓
Payroll Correction / Adjustment
```

must preserve the finalized payroll version.

---

# 69. Payroll and Branch

Payroll may be associated with:

* Employee;
* Branch;
* Business.

If an Employee works across multiple Branches, the payroll calculation must use the configured Business rule for allocating earnings.

The API must not silently assign all earnings to the currently selected Branch.

---

# 70. Payroll and Role Changes

Changing an Employee's role does not rewrite historical payroll.

If compensation depends on role:

```text
Role Version
+
Salary Version
```

must be identifiable for the relevant payroll period.

---

# 71. Employee Deactivation and Payroll

Deactivating an Employee does not delete:

* attendance;
* salary history;
* payroll;
* bonuses;
* deductions.

Pending payroll obligations remain available according to Business rules.

---

# 72. Subscription READ_ONLY

When Business subscription enters `READ_ONLY`:

Allowed:

* Employee read;
* historical attendance read;
* payroll read;
* permitted exports.

Blocked:

* Employee creation;
* Employee activation/deactivation;
* permission changes;
* attendance mutation;
* salary changes;
* payroll calculation mutation;
* payroll finalization;
* payroll corrections.

Offline devices cannot bypass these restrictions.

---

# 73. Deleted Business

A Business in `DELETED` state must not accept normal Employee, Attendance or Payroll API operations.

Historical data lifecycle follows:

`24_Data_Lifecycle_and_Deletion_Data_Model.md`

---

# 74. Attendance Authorization

Typical permissions:

```text
attendance.view
attendance.clock_in
attendance.clock_out
attendance.correct
attendance.approve
attendance.report
```

The exact permission registry remains centralized.

---

# 75. Payroll Authorization

Typical permissions:

```text
payroll.view
payroll.view_all
payroll.configure
payroll.calculate
payroll.finalize
payroll.adjust
payroll.pay
```

Employees normally receive only their own payroll information unless broader access is granted.

---

# 76. Salary Visibility

Salary information is sensitive Business data.

The API must distinguish:

```text
Own Salary
Other Employee Salary
Business Payroll Summary
Detailed Payroll
```

An Employee must not gain access to another Employee's salary by changing:

```text
employee_id
```

in the URL.

---

# 77. Manager Payroll Authority

A Manager's ability to access or modify payroll depends on explicit permissions.

Manager role alone must not imply unrestricted salary access.

---

# 78. Employee and Device Context

Attendance operations may require trusted device context.

For example:

```text
Employee
+
Branch
+
Trusted Device
```

The API may apply stricter device validation for attendance than for ordinary read operations.

---

# 79. Offline Payroll

Payroll calculation should normally remain server-side.

Offline devices should not independently finalize payroll.

Offline clients may collect permitted attendance events that are later synchronized.

---

# 80. Offline Attendance Synchronization

An offline attendance operation must include a stable operation UUID.

Example:

```json
{
  "operation_id": "018f...",
  "operation_type": "CLOCK_IN",
  "employee_id": "018f...",
  "branch_id": "018f...",
  "device_id": "018f...",
  "client_created_at": "2026-10-07T08:00:00Z"
}
```

The server validates the Employee/device relationship and offline authorization.

---

# 81. Offline Attendance Conflict

Possible conflicts include:

```text
ATTENDANCE_ALREADY_OPEN
INVALID_BRANCH_SCOPE
DEVICE_NOT_AUTHORIZED
OFFLINE_AUTHORIZATION_EXPIRED
CLOCK_SEQUENCE_CONFLICT
EMPLOYEE_INACTIVE
```

The synchronization API returns a structured per-operation result.

---

# 82. Payroll Concurrency

Payroll calculation and finalization must use concurrency control.

Two users must not be able to finalize the same payroll independently.

Example:

```text
User A → Finalize
User B → Finalize
```

Only one authoritative finalization succeeds.

The second operation receives a conflict or already-finalized result.

---

# 83. Salary Configuration Concurrency

Salary changes should use optimistic concurrency.

Example:

```http
If-Match: "5"
```

If the current version is `6`:

```text
409 STALE_VERSION
```

The server must not silently overwrite the newer salary configuration.

---

# 84. Attendance Concurrency

Clock-in and clock-out operations must be idempotent and concurrency-safe.

Two simultaneous clock-in requests must not create two active attendance records.

---

# 85. Payroll Idempotency

Retryable payroll operations require idempotency.

Examples:

* calculate;
* finalize;
* correction;
* bonus;
* deduction;
* payroll payment.

Repeated requests with the same operation UUID must not duplicate the effect.

---

# 86. Audit

The following operations must be auditable:

* Employee creation;
* Employee deactivation;
* Branch assignment;
* role assignment;
* permission changes;
* attendance correction;
* salary change;
* bonus;
* deduction;
* payroll calculation where required;
* payroll finalization;
* payroll correction;
* payroll payment.

Audit context should include:

```text
Business
Branch
Employee
Actor
Device where applicable
Operation UUID
Request ID
Timestamp
```

---

# 87. Error Codes

Relevant error codes include:

```text
EMPLOYEE_NOT_FOUND
EMPLOYEE_INACTIVE
BRANCH_ASSIGNMENT_INVALID
ROLE_NOT_FOUND
ROLE_ASSIGNMENT_DENIED
PERMISSION_ASSIGNMENT_DENIED
ATTENDANCE_NOT_FOUND
ATTENDANCE_ALREADY_OPEN
NO_ACTIVE_ATTENDANCE
ATTENDANCE_CORRECTION_DENIED
ATTENDANCE_CORRECTION_CONFLICT
OFFLINE_AUTHORIZATION_EXPIRED
DEVICE_NOT_AUTHORIZED
PAYROLL_PERIOD_NOT_FOUND
PAYROLL_PERIOD_CLOSED
PAYROLL_ALREADY_FINALIZED
PAYROLL_NOT_CALCULATED
SALARY_CONFIGURATION_NOT_FOUND
SALARY_VERSION_CONFLICT
INVALID_SALARY_TYPE
INVALID_SALARY_AMOUNT
INVALID_BONUS
INVALID_DEDUCTION
PAYROLL_CORRECTION_DENIED
PAYROLL_ALREADY_PAID
PAYROLL_PAYMENT_CONFLICT
STALE_VERSION
DUPLICATE_OPERATION
SUBSCRIPTION_READ_ONLY
ACCESS_DENIED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
```

Canonical error formatting is defined in:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 88. API Response Security

Employee APIs must expose only fields authorized for the requesting actor.

For example:

```text
Employee
→ own profile + own attendance + own payroll

Manager
→ explicitly permitted Branch employee information

Owner
→ Business-level employee and payroll information according to permissions

Super Admin
→ platform-level information according to administrative scope
```

Sensitive salary data must not be included in general Employee list responses unless required and authorized.

---

# 89. Pagination

The following endpoints must use bounded pagination when lists can grow:

```text
/employees
/roles
/attendance
/payroll
/payroll/periods
/payroll/corrections
```

Default and maximum page sizes follow:

`11_API_Pagination_Search_Filtering_and_Sorting.md`

---

# 90. Search and Filtering

Employee search may support:

```text
name
employee_number
phone
status
branch
role
```

Payroll and attendance filtering may support:

```text
employee
branch
period
date range
status
```

Search must remain Business and Branch scoped.

---

# 91. API Caching

Potentially cacheable:

* Role definitions;
* permission metadata;
* Employee non-sensitive reference data;
* Branch assignment metadata;
* payroll configuration metadata.

Highly sensitive or rapidly changing state should use bounded caching or authoritative reads.

Payroll amounts must not depend on stale cache.

---

# 92. Cache and Authorization

Permission-related cache must be invalidated when:

* role changes;
* Employee permission override changes;
* Employee deactivation occurs;
* Branch assignment changes;
* subscription state changes.

Cache failure must never become authorization bypass.

---

# 93. Attendance and Payroll Transactions

Core attendance mutation:

```text
Validate
 ↓
Lock / Concurrency Check
 ↓
Create or Update Attendance
 ↓
Audit / Outbox
 ↓
Commit
```

Core payroll finalization:

```text
Validate Payroll
 ↓
Validate Salary Version
 ↓
Validate Attendance Basis
 ↓
Calculate / Verify
 ↓
Finalize
 ↓
Audit / Outbox
 ↓
Commit
```

Secondary notifications occur after commit.

---

# 94. Payroll and External Services

Payroll calculation must not depend on an external notification provider.

Example:

```text
Payroll Finalization
       ↓
Database Commit
       ↓
Salary Notification
```

If notification fails, finalized payroll remains authoritative.

---

# 95. Performance Targets

Initial targets:

| Operation                       |                             Target |
| ------------------------------- | ---------------------------------: |
| Employee read p95               |                           ≤ 200 ms |
| Employee list p95               |                           ≤ 300 ms |
| Role/permission read p95        |                           ≤ 200 ms |
| Attendance clock-in p95         |                           ≤ 400 ms |
| Attendance clock-out p95        |                           ≤ 400 ms |
| Attendance read p95             |                           ≤ 250 ms |
| Attendance correction p95       |                           ≤ 500 ms |
| Salary configuration read p95   |                           ≤ 250 ms |
| Salary configuration update p95 |                           ≤ 400 ms |
| Payroll calculation p95         | ≤ 1 s for normal Business workload |
| Payroll read p95                |                           ≤ 300 ms |
| Payroll finalization p95        |                           ≤ 700 ms |
| Payroll correction p95          |                           ≤ 500 ms |
| Permission update p95           |                           ≤ 400 ms |

Large payroll calculations may be asynchronous when the Business size exceeds normal synchronous limits.

---

# 96. Availability Target

Employee, Attendance and Payroll APIs follow the platform target:

**≥ 99.9% monthly availability**

Security and historical integrity remain higher-priority requirements than availability during uncertain authorization or transactional states.

---

# 97. Observability

Metrics should include:

```text
employee_request_latency
attendance_clock_in_latency
attendance_clock_out_latency
attendance_correction_count
attendance_conflict_count
payroll_calculation_latency
payroll_finalization_latency
payroll_correction_count
salary_configuration_conflict_count
permission_update_count
offline_attendance_conflict_count
```

Metrics must not use uncontrolled Employee UUIDs as high-cardinality labels.

---

# 98. Testing Requirements

The API must test:

### Employee

* creation;
* update;
* activation;
* deactivation;
* Branch assignment;
* role assignment;
* permission override.

### Attendance

* clock-in;
* clock-out;
* duplicate requests;
* correction;
* approval;
* Branch scope;
* Employee deactivation;
* offline attendance;
* synchronization conflicts.

### Payroll

* fixed salary;
* percentage salary;
* shift salary;
* daily salary;
* hybrid salary;
* bonuses;
* deductions;
* payroll calculation;
* finalization;
* payment;
* correction;
* concurrency;
* historical integrity.

---

# 99. Security Testing

Security tests must verify:

* Employee isolation;
* salary confidentiality;
* Business isolation;
* Branch isolation;
* Manager authority;
* permission override restrictions;
* inactive Employee restrictions;
* subscription restrictions;
* trusted device requirements;
* offline authorization;
* unauthorized payroll access;
* unauthorized attendance correction.

---

# 100. Historical Integrity Testing

Tests must verify:

```text
Current Salary
      ≠
Historical Finalized Payroll Salary
```

```text
Current Role
      ≠
Historical Payroll Context
```

```text
Current Attendance
      ≠
Historical Finalized Payroll Snapshot
```

Historical payroll must remain reconstructable.

---

# 101. Failure Recovery

If attendance mutation fails before commit:

```text
Rollback
```

If payroll finalization commits successfully but notification fails:

```text
Payroll remains FINALIZED
Notification retries separately
```

Recovery must never create duplicate payroll effects.

---

# 102. Endpoint Summary

### Employees

```text
GET    /employees
POST   /employees
GET    /employees/{id}
PATCH  /employees/{id}
POST   /employees/{id}/activate
POST   /employees/{id}/deactivate
GET    /employees/{id}/branches
POST   /employees/{id}/branches
DELETE /employees/{id}/branches/{branch_id}
GET    /employees/{id}/roles
POST   /employees/{id}/roles
DELETE /employees/{id}/roles/{role_id}
GET    /employees/{id}/permissions
POST   /employees/{id}/permission-overrides
DELETE /employees/{id}/permission-overrides/{permission}
GET    /employees/{id}/salary
PUT    /employees/{id}/salary
GET    /employees/{id}/payroll
```

### Roles

```text
GET    /roles
POST   /roles
GET    /roles/{id}
PATCH  /roles/{id}
POST   /roles/{id}/archive
```

### Attendance

```text
POST   /attendance/clock-in
POST   /attendance/clock-out
GET    /attendance/me
GET    /attendance
GET    /attendance/{id}
POST   /attendance/{id}/corrections
POST   /attendance/{id}/corrections/{correction_id}/approve
POST   /attendance/{id}/corrections/{correction_id}/reject
GET    /attendance/reports
```

### Payroll

```text
GET    /payroll
GET    /payroll/{id}
GET    /payroll/periods
POST   /payroll/periods
GET    /payroll/periods/{id}
POST   /payroll/periods/{id}/calculate
POST   /payroll/periods/{id}/close
POST   /payroll/{id}/finalize
POST   /payroll/{id}/bonuses
POST   /payroll/{id}/deductions
POST   /payroll/{id}/corrections
POST   /payroll/{id}/corrections/{correction_id}/approve
POST   /payroll/{id}/payments
```

---

# 103. API Invariants

The following invariants apply to Employee, Attendance and Payroll APIs:

1. Employee identity is Business-scoped.
2. Employee UUID is never an authentication credential.
3. Cross-Business Employee access is prohibited.
4. Employee Branch assignments are Business-scoped.
5. An Employee may belong to multiple Branches.
6. Branch assignment does not automatically grant every permission.
7. Employee deactivation blocks new protected operations.
8. Employee deactivation does not delete historical records.
9. Historical Employee attribution remains immutable.
10. Role assignment is authorization-controlled.
11. Manager authority cannot exceed the Manager's own authority.
12. Permission changes are server-authoritative.
13. Employee permission overrides are scope-aware.
14. Permission changes are auditable.
15. Permission cache cannot bypass current authorization.
16. Attendance is Employee-scoped.
17. Attendance retains Branch context.
18. Attendance history cannot be silently overwritten.
19. Online server timestamps are authoritative for important events.
20. Offline timestamps do not override server authority.
21. Duplicate clock-in operations cannot create multiple active attendance records.
22. Duplicate clock-out operations cannot create duplicate effects.
23. Clock-out without valid attendance is rejected.
24. Attendance correction requires explicit authority.
25. Attendance correction requires a reason where policy requires it.
26. Attendance corrections preserve historical context.
27. Attendance approval requires appropriate authority.
28. Offline attendance requires trusted-device authorization.
29. A new device cannot bootstrap offline attendance.
30. Expired offline authorization blocks new offline attendance operations.
31. Offline attendance operations use stable operation UUIDs.
32. Duplicate synchronization does not duplicate attendance.
33. Attendance synchronization cannot bypass Business scope.
34. Attendance synchronization cannot bypass Branch scope.
35. Inactive Employees cannot create normal new attendance operations.
36. Payroll belongs to the correct Business.
37. Payroll retains Employee context.
38. Payroll retains relevant Branch context.
39. Payroll periods have deterministic boundaries.
40. Payroll state transitions are server-controlled.
41. Finalized payroll cannot be silently edited.
42. Salary configuration is separate from finalized payroll.
43. Salary configurations are versioned where required.
44. Salary changes do not rewrite historical payroll.
45. Fixed salary uses server-authoritative configuration.
46. Percentage salary uses a server-defined calculation base.
47. Shift salary uses authoritative attendance/shift information.
48. Daily salary uses authoritative attendance/business rules.
49. Hybrid salary is calculated server-side.
50. Client-provided final salary is never authoritative.
51. Bonuses are separate payroll adjustments.
52. Deductions are separate payroll adjustments.
53. Bonuses and deductions require appropriate authorization.
54. Payroll calculation uses authoritative salary configuration.
55. Payroll calculation uses authoritative attendance.
56. Payroll calculation uses approved payroll inputs.
57. Payroll finalization is concurrency-safe.
58. Only one authoritative finalization may succeed.
59. Duplicate payroll finalization does not create duplicate effects.
60. Finalized payroll preserves its salary version.
61. Finalized payroll preserves its calculation basis.
62. Finalized payroll preserves bonuses and deductions.
63. Finalized payroll preserves correction history.
64. Current attendance does not silently rewrite finalized payroll.
65. Current salary configuration does not rewrite finalized payroll.
66. Current role configuration does not rewrite historical payroll.
67. Payroll correction creates a separate historical event.
68. Payroll correction requires authorization.
69. Payroll payment is distinct from payroll calculation.
70. Payroll payment follows financial API rules.
71. Payroll payment cannot duplicate through retry.
72. READ_ONLY subscription blocks Employee mutations.
73. READ_ONLY subscription blocks attendance mutations.
74. READ_ONLY subscription blocks salary mutations.
75. READ_ONLY subscription blocks payroll mutations.
76. Historical Employee data remains viewable according to authorization after subscription expiry.
77. Deleted Businesses cannot accept normal Employee operations.
78. Salary information is confidential and scope-controlled.
79. Employees cannot access another Employee's salary by changing a URL identifier.
80. Manager payroll access requires explicit permission.
81. General Employee list responses must not expose unnecessary salary information.
82. Attendance and Payroll APIs preserve Business isolation.
83. Attendance and Payroll APIs preserve Branch isolation.
84. Client-provided Employee UUID is never sufficient authority.
85. Client-provided Branch UUID is never sufficient authority.
86. Client-provided salary totals are never authoritative.
87. Client-provided attendance totals are never authoritative.
88. Client-provided payroll totals are never authoritative.
89. Important Employee operations are auditable.
90. Important attendance corrections are auditable.
91. Salary changes are auditable.
92. Payroll finalization is auditable.
93. Payroll corrections are auditable.
94. API idempotency protects retryable mutations.
95. Idempotency-key reuse with conflicting payload is rejected.
96. Salary configuration uses optimistic concurrency where required.
97. Attendance mutations are concurrency-safe.
98. Payroll finalization is concurrency-safe.
99. Payroll calculation cannot produce contradictory authoritative states.
100. Payroll correction cannot delete historical finalization.
101. Offline operations cannot bypass subscription restrictions.
102. Offline operations cannot bypass employee deactivation.
103. Trusted-device state is validated server-side.
104. Permission cache cannot authorize revoked access indefinitely.
105. Salary cache cannot become payroll authority.
106. Attendance cache cannot become attendance authority.
107. Payroll cache cannot become payroll authority.
108. Payroll calculation does not require external notification success.
109. Notification failure does not rollback finalized payroll.
110. Employee API performance must remain within defined SLOs.
111. Attendance API performance must remain within defined SLOs.
112. Payroll API performance must remain within defined SLOs.
113. Large payroll operations may be asynchronous.
114. Pagination remains bounded.
115. Salary visibility remains authorization-controlled.
116. Historical payroll remains reconstructable.
117. Historical attendance remains attributable.
118. Historical salary versions remain identifiable.
119. Audit records remain immutable.
120. Employee, Attendance and Payroll APIs must preserve the modular monolith boundary.

---

# 104. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/15_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/15_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

### Database

* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
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
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`

---

# 105. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `16_API_Employee_Attendance_and_Payroll_Endpoints.md`

**Previous Document:** `15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`

**Next Document:** `17_API_Report_File_and_Notification_Endpoints.md`

---

## Final Principle

> Employee, Attendance and Payroll APIs must preserve identity, authorization, salary confidentiality, Branch scope, attendance integrity and historical payroll correctness while providing simple operational contracts for everyday Business workflows.

