# Attendance and Payroll UI

**Document ID:** FA-15
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `14_Menu_and_Pricing_UI.md`
**Next Document:** `16_Reports_and_Dashboard_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture and user interface behavior for employee attendance and payroll.

The system must allow authorized users to:

* view employee attendance;
* record attendance where permitted;
* manage attendance corrections;
* view employee work periods;
* configure payroll-related information where permitted;
* review calculated payroll;
* apply bonuses where authorized;
* distinguish payroll states;
* preserve historical payroll information.

The main principle is:

> Attendance and payroll UI must be simple for daily operations while preserving financial, employee and historical integrity.

---

# 2. Scope

This document covers:

* Attendance;
* employee work records;
* shifts;
* branch scope;
* employee scope;
* attendance status;
* attendance correction;
* payroll;
* fixed salary;
* percentage salary;
* shift-based salary;
* daily salary;
* hybrid salary;
* bonuses;
* payroll periods;
* payroll calculation;
* payroll review;
* payroll finalization;
* payroll history;
* permissions;
* employee visibility;
* subscription restrictions;
* offline behavior;
* synchronization;
* audit;
* notifications;
* reports;
* performance;
* accessibility.

---

# 3. Attendance and Payroll Relationship

The Frontend must distinguish attendance from payroll.

```text id="att101"
Employee
   ↓
Attendance
   ↓
Payroll Calculation
   ↓
Payroll Review
   ↓
Payroll Finalization
```

Attendance provides relevant work information.

Payroll uses authoritative Backend calculations.

---

# 4. Employee Context

Attendance and payroll screens operate within:

```text id="att202"
Business
   ↓
Branch
   ↓
Employee
   ↓
Attendance / Payroll
```

Employee access must respect Business and Branch scope.

---

# 5. Employee Visibility

A user may only see employees allowed by:

* Business scope;
* Branch scope;
* employee permissions;
* role authority;
* subscription entitlement.

---

# 6. Attendance Overview

The Attendance page should provide:

* date;
* employee;
* Branch;
* attendance status;
* check-in;
* check-out;
* worked duration;
* correction status where applicable.

---

# 7. Attendance Period

Users should be able to select:

* day;
* week;
* month;
* custom supported period.

The Frontend must use Business/Branch timezone rules.

---

# 8. Date and Time

Attendance timestamps must be displayed according to the applicable Business/Branch timezone.

The Frontend must not independently reinterpret server timestamps.

---

# 9. Attendance Calendar

A calendar view may display:

```text id="att303"
Present
Absent
Late
Leave
Off
Correction Pending
```

Exact statuses are Backend-authoritative.

---

# 10. Attendance Table

A table view should provide:

| Employee | Date | Status | Check-in | Check-out | Worked |
| -------- | ---- | ------ | -------- | --------- | ------ |

Additional columns may be shown according to permissions.

---

# 11. Employee Attendance Detail

Employee attendance detail may include:

* employee;
* Branch;
* selected period;
* attendance records;
* total worked time;
* corrections;
* notes;
* payroll relevance where authorized.

---

# 12. Attendance Status

The Frontend must not hard-code business rules around attendance status.

Backend configuration is authoritative.

---

# 13. Check-In

If the business process allows Frontend check-in, the action must require:

* authenticated employee;
* valid Branch context;
* appropriate permission;
* valid employee status;
* applicable operational conditions.

---

# 14. Check-Out

Check-out should be available only when the relevant attendance record permits it.

The Frontend must prevent obvious duplicate submission.

---

# 15. Attendance Duplicate Protection

Repeated check-in/check-out actions must not create duplicate authoritative attendance records.

Operation UUIDs should be used where the operation is retryable.

---

# 16. Attendance Feedback

After an attendance operation:

```text id="att404"
Check-in recorded successfully.
```

or:

```text id="att405"
Attendance result is being confirmed...
```

must be shown according to the actual operation state.

---

# 17. Unknown Attendance Result

If the request times out:

```text id="att506"
The result of this attendance operation is unknown.

Checking current attendance...
```

The UI must reconcile before offering another submission.

---

# 18. Attendance Correction

Authorized users may request or perform corrections according to permission.

Example:

```text id="att607"
Original:
08:12

Corrected:
08:00

Reason:
Device was unavailable.
```

---

# 19. Correction Permission

Attendance correction requires explicit permission where defined.

The Frontend must not allow ordinary employees to modify protected historical records merely because they can view them.

---

# 20. Correction Reason

A correction reason should be required where the System Analysis rules require it.

---

# 21. Correction Workflow

Recommended flow:

```text id="att708"
Correction Request
      ↓
Review
      ↓
Approve / Reject
      ↓
Effective Attendance State
```

Exact approval requirements depend on Backend business rules.

---

# 22. Attendance History

Historical attendance records must remain traceable.

The UI may display:

* original value;
* corrected value;
* actor;
* correction reason;
* correction time;
* approval;
* source.

---

# 23. Attendance Immutability

The Frontend must not provide normal edit functionality that silently overwrites protected historical attendance records.

Corrections should use the defined correction mechanism.

---

# 24. Branch Attendance

Branch-specific attendance must respect the current Branch context.

A user with access to multiple Branches may switch Branch and view the corresponding authorized employees.

---

# 25. Multi-Branch Employee

An employee may work in multiple Branches.

The UI must distinguish attendance records by Branch.

---

# 26. Employee Branch Assignment

Attendance UI must use the employee's valid Branch assignment.

The Frontend must not allow arbitrary Branch selection for an employee.

---

# 27. Branch Switching

When switching Branch:

1. validate the new Branch;
2. recalculate permissions;
3. reload authorized employees;
4. reload attendance;
5. invalidate stale filters where necessary.

---

# 28. Unsaved Attendance Changes

If an attendance form has unsaved changes, Branch or page navigation should warn the user.

---

# 29. Attendance Search

Search may support:

* employee name;
* employee code;
* supported employee identifiers.

Search must respect authorization scope.

---

# 30. Attendance Filters

Recommended filters:

* employee;
* Branch;
* date range;
* attendance status;
* correction status;
* payroll period.

---

# 31. Attendance Sorting

Supported sorting may include:

* date;
* employee;
* check-in;
* check-out;
* worked duration;
* status.

---

# 32. Attendance Pagination

Large attendance datasets must use pagination.

Cursor pagination should be preferred where appropriate.

---

# 33. Attendance Summary

A summary may show:

```text id="att809"
Employees:
24

Present:
20

Absent:
2

Late:
2

Correction Pending:
1
```

Values must come from authoritative data.

---

# 34. Payroll

Payroll represents employee compensation calculated according to the configured salary model.

Payroll is financial data.

---

# 35. Payroll Salary Types

The UI must support the accepted salary models:

* fixed;
* percentage;
* shift-based;
* daily;
* hybrid.

The exact calculation remains Backend-authoritative.

---

# 36. Fixed Salary

Fixed salary may represent a configured amount for the applicable payroll period.

The UI should display the configured basis without independently calculating final financial truth.

---

# 37. Percentage Salary

Percentage salary may depend on an applicable business metric.

The UI may display:

* percentage;
* calculation basis;
* calculated result.

The authoritative result comes from Backend.

---

# 38. Shift-Based Salary

Shift-based salary may use valid shift/work records.

The Frontend should display the relevant shift count or basis where permitted.

---

# 39. Daily Salary

Daily salary may use applicable worked days.

The Frontend should distinguish:

```text id="pay101"
Worked Days
```

from:

```text id="pay102"
Paid Days
```

where the domain model supports both.

---

# 40. Hybrid Salary

Hybrid salary may combine multiple salary components.

Example:

```text id="pay203"
Base:
3,000,000

Shift component:
450,000

Bonus:
300,000

Total:
3,750,000
```

The exact calculation remains Backend-authoritative.

---

# 41. Payroll Period

Payroll operates over a defined period.

The UI should clearly display:

* period start;
* period end;
* Branch or Business scope;
* payroll status.

---

# 42. Payroll States

Recommended states:

```text id="pay304"
DRAFT
CALCULATED
UNDER_REVIEW
FINALIZED
PAID
CANCELLED
```

Exact state names remain Backend-authoritative.

---

# 43. Payroll Draft

Draft payroll may be recalculated or modified by authorized users.

It must not be presented as finalized financial truth.

---

# 44. Payroll Calculation

Calculation may use:

* attendance;
* salary configuration;
* shifts;
* percentage basis;
* bonuses;
* approved adjustments.

The Frontend displays Backend-provided results.

---

# 45. Payroll Recalculation

If recalculation is permitted, the UI should clearly indicate that values may change.

Example:

```text id="pay405"
Recalculate payroll?

Current draft values may change based on the latest valid attendance and payroll configuration.
```

---

# 46. Payroll Review

Authorized users may review:

* employee;
* salary type;
* calculation basis;
* attendance basis;
* bonuses;
* deductions where supported;
* total.

---

# 47. Payroll Review Table

Example:

| Employee | Salary Type | Base | Bonus | Total | Status |
| -------- | ----------- | ---: | ----: | ----: | ------ |

Sensitive financial columns require appropriate permission.

---

# 48. Payroll Detail

Employee payroll detail may include:

```text id="pay506"
Employee
Period
Salary Type
Base
Attendance Basis
Shift Basis
Percentage Basis
Bonus
Adjustments
Total
Status
```

Only permitted fields should be shown.

---

# 49. Payroll Calculation Breakdown

Where permitted, the UI should show a readable calculation breakdown.

Example:

```text id="pay607"
Base salary:
3,000,000

Shift amount:
450,000

Bonus:
300,000

Total:
3,750,000
```

---

# 50. Financial Authority

The Frontend must never become the authoritative payroll calculator.

Client-side calculations may support:

* preview;
* input validation;
* display.

Final payroll values come from Backend.

---

# 51. Payroll Configuration

Authorized users may manage salary configuration.

Configuration may include:

* salary type;
* base amount;
* percentage;
* shift rate;
* daily rate;
* hybrid components;
* bonus rules where supported.

---

# 52. Salary Configuration Permission

Salary configuration requires explicit permission.

---

# 53. Salary Configuration History

Changes to salary configuration must preserve:

* previous value;
* new value;
* actor;
* timestamp;
* effective period;
* reason where applicable.

---

# 54. Historical Payroll Integrity

Changing an employee's current salary configuration must not rewrite finalized historical payroll.

---

# 55. Payroll Snapshot

Finalized payroll should reference the applicable financial/configuration snapshot.

The UI should use that snapshot when displaying historical payroll.

---

# 56. Employee Salary Change

Example:

```text id="pay708"
Previous:
3,000,000

New:
3,500,000

Effective:
Next Payroll Period
```

The exact effective rule is Backend-authoritative.

---

# 57. Salary Change Confirmation

Important salary changes should require explicit confirmation.

---

# 58. Bonus

The system supports employee bonuses.

Bonus may be:

* fixed amount;
* another supported configured type.

The exact supported bonus model is Backend-authoritative.

---

# 59. Bonus Permission

Bonus application requires appropriate permission.

---

# 60. Bonus Reason

A bonus should have a reason where required.

Example:

```text id="bon101"
Bonus:
300,000

Reason:
Monthly performance bonus
```

---

# 61. Bonus History

Bonus history must remain traceable.

The UI may show:

* amount;
* employee;
* actor;
* date;
* reason;
* payroll period.

---

# 62. Payroll Correction

Authorized users may request or apply payroll corrections according to the correction model.

---

# 63. Payroll Correction Reason

Protected payroll corrections must require a reason where required.

---

# 64. Payroll Correction History

The UI should preserve:

```text id="pay809"
Original:
3,750,000

Corrected:
4,000,000

Difference:
+250,000

Reason:
Approved attendance correction
```

Historical finalized values must remain reconstructable.

---

# 65. Payroll Finalization

Finalization is a protected financial operation.

The UI should show a confirmation step.

Example:

```text id="pay910"
Finalize payroll for September 2026?

Finalized payroll cannot be changed through ordinary editing.

[Cancel] [Finalize]
```

---

# 66. Finalized Payroll

After finalization:

* ordinary editing is disabled;
* configuration changes do not rewrite it;
* historical snapshot remains available.

---

# 67. Payroll Payment

If payment tracking is part of the accepted domain, the UI may show:

```text id="pay1011"
UNPAID
PAID
```

The exact payment workflow is Backend-authoritative.

---

# 68. Payroll Payment Integrity

Changing current salary configuration must not change historical paid payroll.

---

# 69. Payroll Approval

If payroll approval is required:

```text id="pay111"
Draft
  ↓
Calculated
  ↓
Under Review
  ↓
Approved
  ↓
Finalized
```

Exact states remain Backend-authoritative.

---

# 70. Approval Permission

Payroll approval must require appropriate authority.

Editing payroll does not automatically grant approval authority.

---

# 71. Payroll Visibility

Payroll is sensitive information.

The UI must restrict visibility according to:

* role;
* permission;
* Business scope;
* Branch scope;
* employee scope.

---

# 72. Employee Self-View

If configured, an employee may see their own:

* attendance;
* salary information;
* payroll;
* bonuses.

They must not automatically see other employees' payroll.

---

# 73. Owner Payroll View

Owner may view authorized Business/Branch payroll according to the permission model.

---

# 74. Manager Payroll View

Manager payroll access is permission-based.

A Manager must not automatically see all payroll merely because they manage employees.

---

# 75. Payroll Data Masking

If partial visibility is required, sensitive fields may be masked.

Example:

```text id="pay121"
Salary:
••••••••
```

The exact masking policy remains security-authoritative.

---

# 76. Branch Payroll

Branch payroll should remain Branch-scoped unless the user has broader Business authority.

---

# 77. Business Payroll

Business-level payroll may aggregate authorized Branch payroll.

Aggregations must not bypass employee-level privacy rules.

---

# 78. Payroll Period Filters

Users may filter by:

* period;
* Branch;
* employee;
* salary type;
* status;
* payment state.

---

# 79. Payroll Search

Search should support:

* employee name;
* employee code;
* supported identifiers.

---

# 80. Payroll Sorting

Supported sorting may include:

* employee;
* total;
* period;
* status;
* payment state.

---

# 81. Payroll Pagination

Large payroll datasets must use pagination.

---

# 82. Payroll Summary

Authorized users may see:

```text id="pay131"
Employees:
48

Gross Payroll:
125,000,000

Bonuses:
8,500,000

Finalized:
42

Pending:
6
```

Exact values come from Backend.

---

# 83. Payroll Reports

Payroll data may be consumed by Reports.

The Payroll UI must not create an independent reporting truth.

---

# 84. Attendance-to-Payroll Link

The UI should allow authorized users to navigate from payroll calculation basis to relevant attendance data.

Example:

```text id="pay141"
Attendance Basis
→ View Attendance
```

---

# 85. Payroll-to-Attendance Navigation

Navigation must preserve:

* Business;
* Branch;
* employee;
* payroll period.

---

# 86. Attendance Change After Payroll Calculation

If attendance changes after payroll calculation:

* the UI must indicate that payroll may be affected;
* finalized payroll must not be silently rewritten;
* draft payroll may require recalculation.

---

# 87. Attendance Change After Finalization

If a correction affects finalized payroll:

* the system must use the defined correction mechanism;
* historical finalized payroll remains traceable;
* a new correction/recalculation state may be created.

---

# 88. Payroll Warning

Example:

```text id="pay151"
Attendance changed after payroll calculation.

Payroll requires review.
```

---

# 89. Notification Integration

Relevant notifications may include:

* salary due;
* payroll ready for review;
* payroll correction request;
* attendance correction request;
* payroll finalization;
* payroll-related conflict.

---

# 90. Notification Navigation

Notification links must open the relevant:

* Business;
* Branch;
* employee;
* payroll period;
* attendance record.

Authorization must be revalidated.

---

# 91. Offline Attendance

Trusted devices may support attendance operations if explicitly allowed by the system.

---

# 92. Offline Payroll

Payroll calculation and finalization should generally require authoritative server state unless the System Analysis explicitly allows offline execution.

The UI must not simulate finalized payroll offline.

---

# 93. Offline Attendance Operation

Where supported:

```text id="off101"
Local Attendance Operation
      ↓
Operation UUID
      ↓
Encrypted Local Storage
      ↓
Synchronization
```

---

# 94. Offline Attendance Freshness

The UI should show the offline state and configuration freshness where relevant.

---

# 95. Offline Synchronization

Attendance synchronization must preserve:

* employee;
* Business;
* Branch;
* device;
* operation UUID;
* timestamp;
* original operation data.

---

# 96. Sync Conflict

Attendance conflicts may occur because of:

* duplicate check-in;
* duplicate check-out;
* server-side correction;
* stale device state.

---

# 97. Attendance Conflict UI

Example:

```text id="off202"
Attendance conflict

Server:
08:05 check-in

Local:
08:00 check-in

The server record is authoritative.

[View Details]
```

---

# 98. Payroll Synchronization

Payroll configuration changes must synchronize through authoritative configuration mechanisms.

Historical payroll must not be rewritten by stale device state.

---

# 99. Subscription Read-Only

When the Business is read-only:

* historical attendance remains viewable;
* historical payroll remains viewable;
* permitted exports remain available;
* modifying operations are blocked.

---

# 100. Subscription UI

Example:

```text id="sub101"
Business is in read-only mode.

Attendance and payroll records can be viewed, but protected modifications are disabled.
```

---

# 101. Employee Deactivation

Deactivating an employee must not delete:

* attendance history;
* payroll history;
* salary history;
* bonus history.

---

# 102. Employee Historical Identity

Historical attendance and payroll remain associated with the original employee identity.

---

# 103. Employee Reassignment

If an employee changes Branch, historical records must retain their original Branch context.

---

# 104. Branch Transfer

The UI should clearly distinguish:

```text id="br101"
Previous Branch
Current Branch
Effective Date
```

where applicable.

---

# 105. Attendance Correction Audit

Corrections should retain:

* actor;
* timestamp;
* old value;
* new value;
* reason;
* approval;
* device;
* operation UUID where applicable.

---

# 106. Payroll Audit

Important payroll operations should be audited:

* salary configuration;
* bonus;
* calculation;
* correction;
* approval;
* finalization;
* payment state change.

---

# 107. Audit Display

Authorized users may see:

```text id="aud101"
Actor:
Manager A

Action:
Payroll Correction

Employee:
Employee B

Old:
3,750,000

New:
4,000,000

Reason:
Approved attendance correction
```

---

# 108. Configuration Conflict

Salary configuration conflicts must use optimistic concurrency.

Example:

```text id="cfg101"
Current version:
v12

Your version:
v11

The salary configuration was changed by another user.
```

---

# 109. Conflict Resolution

Conflict resolution must:

* show current state;
* preserve existing version;
* preserve user draft where possible;
* identify resolving actor;
* create a new valid version where required.

---

# 110. Duplicate Payroll Commands

Repeated requests must not create duplicate:

* payroll calculations;
* bonuses;
* corrections;
* finalizations;
* payment operations.

---

# 111. Operation UUID

Retryable payroll/attendance commands should use operation UUIDs.

---

# 112. Unknown Payroll Result

If payroll finalization times out:

```text id="pay161"
Payroll finalization result is unknown.

Checking payroll status...
```

The UI must reconcile before retrying.

---

# 113. Loading States

Attendance and payroll pages should provide:

* initial loading;
* table loading;
* detail loading;
* calculation loading;
* correction loading;
* finalization loading;
* synchronization state.

---

# 114. Empty Attendance

Example:

```text id="emp101"
No attendance records found for this period.
```

---

# 115. Empty Payroll

Example:

```text id="emp202"
No payroll records exist for the selected period.
```

---

# 116. Partial Loading

If attendance loads successfully but a secondary summary fails:

```text id="err101"
Attendance loaded.

Summary could not be loaded.
[Retry Summary]
```

The entire page should not fail unnecessarily.

---

# 117. Error Classification

Attendance/Payroll errors should distinguish:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

---

# 118. Validation Error

Example:

```text id="err202"
Check-out time cannot be earlier than check-in time.
```

---

# 119. Authorization Error

Example:

```text id="err303"
You do not have permission to modify payroll.
```

---

# 120. Business Rule Error

Example:

```text id="err404"
This payroll period has already been finalized.
```

---

# 121. Conflict Error

Example:

```text id="err505"
Payroll configuration changed by another user.
Refresh and continue from the latest version.
```

---

# 122. Safe Recovery

Recovery actions may include:

* refresh;
* retry safe operation;
* review conflict;
* open current record;
* return to list.

---

# 123. No Blind Retry

Finalization, payment and other financial operations must not be blindly retried after an unknown result.

---

# 124. Attendance Forms

Attendance forms should provide:

* employee;
* date;
* status;
* check-in;
* check-out;
* reason/comment where required.

---

# 125. Payroll Forms

Payroll configuration forms may provide:

* salary type;
* amount;
* percentage;
* shift rate;
* daily rate;
* hybrid components;
* effective period.

---

# 126. Form Validation

Client-side validation should catch obvious errors.

Backend remains authoritative.

---

# 127. Financial Formatting

Payroll amounts must use centralized currency formatting.

No feature-specific currency formatter should be created.

---

# 128. Time Formatting

Attendance timestamps must use centralized date/time formatting.

---

# 129. Precision

Payroll calculations must preserve the precision returned by the Backend.

Frontend must not use floating-point arithmetic to redefine authoritative financial values.

---

# 130. Attendance Duration

Worked duration may be displayed using Backend-provided values.

If the UI calculates a temporary preview, it must not replace the authoritative result.

---

# 131. Accessibility

Attendance and payroll UI must support:

* keyboard navigation;
* semantic tables;
* accessible forms;
* visible focus;
* screen reader labels;
* accessible dialogs;
* non-color-only statuses.

---

# 132. Attendance Table Accessibility

Column headers must be properly associated with data cells.

---

# 133. Payroll Table Accessibility

Sensitive payroll values must remain accessible to authorized users without relying on color or visual position alone.

---

# 134. Responsive Layout

Attendance and payroll are primarily administration interfaces.

On smaller screens:

* tables may reflow;
* secondary columns may move to detail views;
* local horizontal scrolling may be used where necessary.

---

# 135. State Management

Frontend state should separate:

```text id="state101"
Business Context
Branch Context
Employee Context
Attendance Query
Attendance Data
Attendance Form
Payroll Query
Payroll Data
Payroll Configuration
Payroll Calculation
Correction State
Permission State
Subscription State
Sync State
UI State
```

---

# 136. Authoritative State

Backend is authoritative for:

* attendance;
* attendance status;
* payroll calculation;
* salary configuration;
* bonuses;
* corrections;
* approval;
* finalization;
* payment state;
* historical values.

---

# 137. Local State

Frontend may own:

* filters;
* selected employee;
* form draft;
* calendar view;
* table sorting;
* selected payroll period;
* modal state.

---

# 138. Cache

Attendance and payroll read models may be cached where appropriate.

Cache must not become financial authority.

---

# 139. Sensitive Cache

Payroll cache must be:

* authorization-aware;
* Business-scoped;
* Branch-scoped where applicable;
* invalidated after relevant changes.

---

# 140. Cache Invalidation

Relevant cache must be invalidated after:

* attendance correction;
* salary configuration change;
* payroll calculation;
* bonus;
* payroll finalization;
* Branch context change;
* synchronization.

---

# 141. Performance

Targets:

* attendance list p95 ≤300 ms after API response;
* attendance search p95 ≤150 ms;
* employee attendance detail p95 ≤300 ms;
* payroll list p95 ≤300 ms after API response;
* payroll detail p95 ≤300 ms;
* local attendance interaction p95 ≤100 ms;
* local payroll form interaction p95 ≤100 ms;
* authoritative attendance update UI ≤2 s after server result.

---

# 142. Initial Page Performance

Targets:

* Attendance page first useful content p75 ≤1.5 s;
* Payroll page first useful content p75 ≤1.5 s;
* Attendance detail interactive p75 ≤2.0 s;
* Payroll detail interactive p75 ≤2.0 s.

---

# 143. Fatal Error Rate

Target:

**Fatal Attendance/Payroll UI error rate <0.1% sessions.**

---

# 144. Payroll Security

Payroll UI must treat salary information as sensitive business data.

The Frontend must not:

* expose payroll to unauthorized employees;
* place payroll values into public URLs;
* log salary values unnecessarily;
* send sensitive payroll information to generic telemetry.

---

# 145. Attendance Security

Attendance records must respect:

* Business isolation;
* Branch isolation;
* employee permissions;
* employee scope.

---

# 146. Export

Authorized users may export attendance/payroll data where supported.

Exports must respect:

* permissions;
* Business scope;
* Branch scope;
* subscription;
* sensitive data rules.

Large exports should be asynchronous.

---

# 147. Export Audit

Payroll and attendance exports must be auditable where required.

---

# 148. Testing

Frontend tests should cover:

### Attendance

* check-in;
* check-out;
* duplicate prevention;
* correction;
* history;
* Branch scope;
* employee scope.

### Payroll

* salary types;
* calculation display;
* bonus;
* correction;
* approval;
* finalization;
* payment state.

### Security

* Business isolation;
* Branch isolation;
* permission;
* subscription;
* sensitive data visibility.

### Offline

* supported attendance operations;
* synchronization;
* conflicts;
* unknown result.

---

# 149. Integration Testing

Integration tests should verify:

* attendance API contracts;
* payroll API contracts;
* salary configuration contracts;
* permission responses;
* correction workflow;
* payroll state transitions;
* audit events;
* synchronization.

---

# 150. Visual Testing

Visual regression should cover:

* Attendance calendar;
* Attendance table;
* Attendance detail;
* Correction dialog;
* Payroll list;
* Payroll detail;
* Salary configuration;
* Payroll calculation breakdown;
* Finalization dialog;
* read-only mode.

---

# 151. Observability

Frontend telemetry may measure:

* attendance page latency;
* payroll page latency;
* correction failures;
* payroll calculation failures;
* finalization failures;
* synchronization failures;
* permission failures;
* fatal UI errors.

Sensitive payroll values must not be included unnecessarily.

---

# 152. AI-Agent Development Rules

AI-assisted implementation must:

1. preserve Business scope;
2. preserve Branch scope;
3. preserve employee authorization;
4. preserve payroll financial authority;
5. preserve attendance history;
6. preserve payroll history;
7. avoid client-side authoritative calculations;
8. preserve correction workflows;
9. preserve approval boundaries;
10. preserve subscription restrictions;
11. use centralized date/time/currency formatting;
12. use operation UUID for retryable mutations;
13. protect against duplicate submissions;
14. preserve offline synchronization boundaries;
15. add tests for financial state transitions;
16. update related documentation when architecture changes.

---

# 153. Attendance and Payroll Invariants

The following invariants are mandatory:

1. Attendance belongs to a Business.
2. Attendance Branch scope is authoritative.
3. Employee identity remains stable.
4. Historical attendance remains associated with the original employee.
5. Historical attendance retains its Branch context where applicable.
6. Employee deactivation does not delete attendance history.
7. Attendance status is Backend-authoritative.
8. Attendance timestamps use authoritative server data.
9. Frontend does not redefine timezone semantics.
10. Duplicate attendance operations must not create duplicate records.
11. Retryable attendance operations use operation UUID.
12. Unknown attendance results are reconciled.
13. Attendance correction does not silently overwrite protected history.
14. Attendance correction is attributable.
15. Attendance correction requires appropriate permission.
16. Attendance correction reason is preserved where required.
17. Attendance correction approval is preserved where required.
18. Attendance search respects Business scope.
19. Attendance search respects Branch scope.
20. Attendance search respects employee visibility.
21. Attendance lists are paginated.
22. Payroll belongs to a Business.
23. Payroll Branch scope is authoritative.
24. Payroll employee scope is authoritative.
25. Payroll is sensitive financial information.
26. Payroll visibility is permission-controlled.
27. Employee self-view does not imply access to other employees.
28. Manager access is permission-based.
29. Salary configuration is permission-controlled.
30. Salary configuration changes are versioned where required.
31. Salary changes do not rewrite finalized payroll.
32. Historical payroll remains reconstructable.
33. Payroll uses authoritative Backend calculations.
34. Frontend calculations are never authoritative.
35. Fixed salary is supported.
36. Percentage salary is supported.
37. Shift-based salary is supported.
38. Daily salary is supported.
39. Hybrid salary is supported.
40. Salary type is Backend-authoritative.
41. Payroll periods are explicit.
42. Payroll state is Backend-authoritative.
43. Draft payroll may change according to valid rules.
44. Finalized payroll cannot be ordinarily edited.
45. Finalized payroll retains its financial snapshot.
46. Payroll recalculation does not silently finalize payroll.
47. Payroll approval is separate from editing where required.
48. Payroll approval requires appropriate authority.
49. Bonus requires appropriate permission.
50. Bonus reason is preserved where required.
51. Bonus history is immutable.
52. Payroll correction requires appropriate permission.
53. Payroll correction requires reason where required.
54. Payroll correction is attributable.
55. Payroll correction preserves historical values.
56. Payroll payment state is Backend-authoritative.
57. Current salary configuration cannot reinterpret historical payroll.
58. Current attendance cannot silently rewrite finalized payroll.
59. Attendance changes after calculation trigger the appropriate review/recalculation state.
60. Attendance changes after finalization use the correction mechanism.
61. Payroll finalization is an explicit protected operation.
62. Financial finalization requires confirmation.
63. Duplicate payroll commands do not create duplicate effects.
64. Unknown payroll mutation results are reconciled.
65. Blind retry of financial finalization is prohibited.
66. Subscription read-only blocks modifying attendance/payroll configuration where applicable.
67. Subscription read-only does not delete historical records.
68. Offline mode cannot bypass subscription restrictions.
69. Offline payroll finalization is not assumed to be supported.
70. Offline attendance is supported only where explicitly authorized.
71. Offline attendance preserves operation identity.
72. Offline synchronization preserves Business context.
73. Offline synchronization preserves Branch context.
74. Offline synchronization preserves employee identity.
75. Synchronization conflicts are explicit.
76. Server state remains authoritative after synchronization.
77. Payroll cache is not authoritative.
78. Attendance cache is not authoritative.
79. Sensitive payroll cache is authorization-aware.
80. Payroll cache is Business-isolated.
81. Branch payroll cache is Branch-isolated.
82. Cache invalidation follows authoritative changes.
83. Payroll export respects authorization.
84. Attendance export respects authorization.
85. Sensitive export operations are auditable where required.
86. Payroll data is not unnecessarily exposed in telemetry.
87. Attendance data is not unnecessarily exposed in telemetry.
88. Business switching recalculates employee visibility.
89. Branch switching recalculates employee visibility.
90. Stale Branch context cannot submit attendance/payroll mutations.
91. URL identifiers are not authorization.
92. Backend remains final authorization authority.
93. Inactive employees cannot create new valid payroll modifications.
94. Permission changes are reflected in the UI.
95. Unauthorized sensitive fields are not displayed.
96. Unsaved attendance changes are protected.
97. Unsaved payroll changes are protected.
98. Duplicate clicks are prevented.
99. Client validation does not replace Backend validation.
100. Financial values use centralized currency formatting.
101. Date/time values use centralized formatting.
102. Frontend does not use floating-point arithmetic as financial authority.
103. Attendance duration from Backend remains authoritative.
104. Payroll calculation basis remains traceable.
105. Payroll-to-attendance navigation preserves context.
106. Attendance-to-payroll navigation preserves context.
107. Historical attendance is not deleted by ordinary UI actions.
108. Historical payroll is not deleted by ordinary UI actions.
109. Employee Branch reassignment does not rewrite historical Branch context.
110. Salary configuration history remains attributable.
111. Payroll finalization remains attributable.
112. Payroll correction remains attributable.
113. Attendance correction remains attributable.
114. Device context is retained for important operations where applicable.
115. Attendance search target is p95 ≤150 ms.
116. Attendance list target is p95 ≤300 ms after API response.
117. Attendance detail target is p95 ≤300 ms.
118. Payroll list target is p95 ≤300 ms after API response.
119. Payroll detail target is p95 ≤300 ms.
120. Local attendance interaction target is p95 ≤100 ms.
121. Local payroll interaction target is p95 ≤100 ms.
122. Authoritative attendance update UI target is ≤2 s after server result.
123. Attendance first useful content target is p75 ≤1.5 s.
124. Payroll first useful content target is p75 ≤1.5 s.
125. Attendance detail interactive target is p75 ≤2.0 s.
126. Payroll detail interactive target is p75 ≤2.0 s.
127. Fatal Attendance/Payroll UI error rate target is <0.1% sessions.
128. Accessibility is mandatory.
129. Status is not communicated by color alone.
130. Keyboard navigation is supported.
131. Screen reader labels are supported.
132. Payroll configuration supports future salary models without breaking historical payroll.
133. Attendance and Payroll remain compatible with Reports architecture.
134. Attendance and Payroll remain compatible with Audit architecture.
135. Attendance and Payroll remain compatible with Offline/Sync architecture.
136. Attendance and Payroll remain compatible with Business/Branch architecture.
137. Financial history has priority over UI convenience.
138. Backend remains the final authority for Attendance and Payroll.
139. Frontend must never silently alter historical financial state.
140. Attendance and Payroll architecture must remain scalable for additional Branches and employees.

---

# 154. Recommended Frontend Structure

```text id="j8x7sz"
frontend/
└── src/
    ├── features/
    │   ├── attendance/
    │   │   ├── pages/
    │   │   ├── components/
    │   │   ├── forms/
    │   │   ├── queries/
    │   │   ├── mutations/
    │   │   ├── corrections/
    │   │   └── types/
    │   │
    │   └── payroll/
    │       ├── pages/
    │       ├── components/
    │       ├── forms/
    │       ├── queries/
    │       ├── mutations/
    │       ├── calculations/
    │       ├── corrections/
    │       └── types/
    │
    ├── entities/
    │   ├── employee/
    │   ├── attendance/
    │   └── payroll/
    │
    ├── synchronization/
    ├── state/
    ├── api/
    └── shared/
```

---

# 155. Dependency Rules

The Frontend must follow:

```text id="dep101"
Page
  ↓
Feature Component
  ↓
Feature Query / Mutation
  ↓
API / Data Layer
  ↓
Backend
```

Attendance and Payroll components must not directly access persistence.

Financial calculations must not be moved into UI components as authoritative logic.

---

# 156. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/13_Products_Recipes_and_Sets_UI.md`
* `docs/04_Architecture/07_Frontend/14_Menu_and_Pricing_UI.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`
* `docs/04_Architecture/07_Frontend/21_Frontend_API_and_Data_Layer.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_Security.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/10_Shift_Handover.md`
* `docs/02_System_Analysis/15_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 157. Status

**Document:** `15_Attendance_and_Payroll_UI.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `14_Menu_and_Pricing_UI.md`

**Next Document:** `16_Reports_and_Dashboard_UI.md`

