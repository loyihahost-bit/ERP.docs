# Attendance and Payroll

**Document ID:** SA-19
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for employee attendance and payroll.

The system must support multiple salary models while preserving calculation history, employee attribution, branch scope and payroll integrity.

Attendance and payroll data must remain auditable and must not be silently rewritten after finalization.

---

## 2. Scope

This document covers:

* employee attendance;
* attendance records;
* employee status;
* Branch scope;
* attendance corrections;
* salary configuration;
* salary models;
* bonuses;
* payroll periods;
* payroll calculation;
* payroll snapshots;
* payroll finalization;
* payroll corrections;
* payroll permissions;
* Branch payroll;
* offline attendance/payroll operations;
* subscription entitlement;
* audit;
* concurrency;
* historical integrity;
* notifications.

---

## 3. Employee Context

Attendance and payroll operations are always associated with an Employee.

Every relevant record must identify:

* Business;
* Employee;
* Branch where applicable;
* actor;
* timestamp;
* source.

An inactive Employee remains visible in historical attendance and payroll records.

---

## 4. Employee Status

Employee lifecycle is:

```text id="emp314"
Created
  ↓
Active
  ↓
Inactive
```

Only an Active Employee may create new operational attendance records.

Changing an Employee to Inactive does not delete:

* attendance history;
* payroll history;
* salary history;
* bonuses;
* finalized payroll.

---

## 5. Branch Context

Attendance and payroll may be Branch-scoped.

The system must preserve the Branch where the work occurred.

An Employee may work at multiple Branches.

The same Employee may have different effective permissions and salary configuration by applicable scope.

---

## 6. Attendance Purpose

Attendance records provide the operational basis for employee work tracking and, where configured, payroll calculation.

Attendance data must remain separate from salary configuration.

A change in salary configuration must not rewrite historical attendance.

---

## 7. Attendance Record Identity

Every attendance record has a stable UUID.

The UUID provides:

* unique identity;
* synchronization identity;
* idempotency;
* audit reference.

The UUID must not be reused.

---

## 8. Attendance Record Context

An attendance record should contain sufficient context to identify:

* Business;
* Employee;
* Branch;
* attendance type/state;
* start time;
* end time where applicable;
* actor/device context where applicable;
* source;
* creation time.

---

## 9. Attendance State

Attendance may be represented using a controlled lifecycle such as:

```text id="att812"
Open
  ↓
Closed
```

Additional business-specific attendance states may be supported without changing the historical identity model.

---

## 10. Attendance Creation

Creating attendance requires:

* active Employee;
* valid Business;
* valid Branch where required;
* appropriate permission;
* valid time data;
* subscription entitlement.

Invalid or unauthorized attendance creation is rejected.

---

## 11. Attendance Time

Attendance timestamps must preserve the original recorded time.

The system must distinguish between:

* Employee/event time;
* server received time;
* synchronization time where applicable.

Offline records retain their original event time.

---

## 12. Duplicate Attendance Prevention

Repeated requests caused by network retry must not create duplicate attendance records.

Attendance operations must use UUID-based idempotency.

A repeated operation returns the existing result where possible.

---

## 13. Attendance Correction

Attendance corrections are controlled operations.

A correction may change an attendance record only through a correction process.

The system must preserve:

* original value;
* corrected value;
* correction reason;
* actor;
* timestamp;
* source.

The original attendance record must remain reconstructable.

---

## 14. Attendance Correction Permission

Attendance correction requires explicit permission.

An Employee must not automatically be allowed to modify their own historical attendance unless the configured permission model explicitly permits it.

Self-modification of attendance must not create an authorization bypass.

---

## 15. Attendance and Employee Status

If an Employee becomes inactive:

* new attendance operations are blocked;
* existing attendance remains historical;
* open attendance requires controlled handling;
* payroll can still use historical attendance for the applicable period.

The system must not delete or silently close historical attendance merely because the Employee became inactive.

---

## 16. Attendance and Branch Switching

When an Employee changes Branch context, the system validates the Employee's Branch assignment and effective permissions.

A Branch change must not rewrite previously recorded attendance.

New attendance records use the new applicable Branch context.

---

## 17. Attendance and Offline Operation

Trusted devices may create permitted attendance records while offline.

Offline attendance must:

* use a local UUID;
* preserve event time;
* retain Employee and Branch context;
* be stored securely;
* enter the synchronization queue.

The server validates the record during synchronization.

---

## 18. Offline Attendance Conflict

A conflict may occur if server state changed while the device was offline.

Examples include:

* Employee became inactive;
* Branch assignment changed;
* attendance record already exists;
* conflicting attendance period exists.

The system creates an explicit conflict.

It must not silently overwrite the server record.

---

## 19. Attendance Conflict Resolution

Only an authorized user may resolve attendance conflicts.

Resolution records:

* original state;
* conflicting state;
* selected resolution;
* reason;
* actor;
* timestamp.

The resolution is separately auditable.

---

## 20. Salary Configuration

Salary configuration defines how an Employee's compensation is calculated.

Salary configuration is separate from:

* Employee permissions;
* attendance permissions;
* Product permissions.

Changing a permission must not automatically change salary configuration.

---

## 21. Salary Configuration Identity

Each salary configuration has a stable UUID.

Salary configuration changes create a new historical configuration where the change affects payroll calculation.

The previous configuration remains available for historical reconstruction.

---

## 22. Supported Salary Models

The system supports:

1. Fixed salary;
2. Percentage salary;
3. Shift-based salary;
4. Daily pay;
5. Hybrid salary;
6. Bonuses.

The exact formula parameters are configurable by authorized Business users.

---

## 23. Fixed Salary

Fixed salary represents a predefined compensation amount for the applicable payroll period.

The system stores:

* amount;
* effective date;
* applicable scope;
* configuration;
* actor;
* historical version.

Changing the amount does not rewrite previous payroll periods.

---

## 24. Percentage Salary

Percentage salary calculates compensation from an applicable business metric according to configured rules.

The configuration must explicitly define:

* percentage;
* calculation base;
* scope;
* effective period.

The system must not assume that every percentage salary uses total Business revenue.

The configured calculation basis must be identifiable.

---

## 25. Shift-Based Salary

Shift-based salary calculates compensation from eligible shifts.

The system must identify:

* applicable shift;
* applicable Employee;
* Branch;
* salary rate;
* number of qualifying shifts;
* payroll period.

Historical shift calculations remain reconstructable.

---

## 26. Daily Pay

Daily pay calculates compensation based on eligible work days.

The system must identify the attendance/work record used to determine eligibility.

A day must not be counted twice because of duplicate synchronization or repeated processing.

---

## 27. Hybrid Salary

Hybrid salary combines multiple configured salary components.

For example:

```text id="hyb541"
Base Salary
+
Shift Pay
+
Percentage Component
+
Bonuses
=
Payroll Amount
```

The exact components are configuration-driven.

---

## 28. Bonuses

Bonuses are separate payroll components.

A bonus record should include:

* Employee;
* Branch where applicable;
* amount or calculation basis;
* reason;
* applicable period;
* creator;
* timestamp.

A bonus must not silently modify the base salary configuration.

---

## 29. Salary Effective Date

Salary configuration has an effective date.

A new salary configuration applies only from its effective point.

Historical payroll calculations continue using the salary configuration that was effective for the relevant period.

---

## 30. Salary Configuration Change

A salary change preserves:

* previous configuration;
* new configuration;
* effective date;
* actor;
* reason;
* timestamp.

The previous configuration is immutable.

---

## 31. Payroll Period

Payroll is calculated for a defined period.

A payroll period identifies:

* Business;
* Branch where applicable;
* start date;
* end date;
* Employee scope;
* calculation configuration.

Invalid periods are rejected.

The end date must not precede the start date.

---

## 32. Payroll Calculation

Payroll calculation uses a consistent snapshot of relevant data.

The calculation may include:

* attendance;
* salary configuration;
* salary model;
* eligible shifts;
* percentage base;
* bonuses;
* applicable deductions where configured.

The exact inputs must be identifiable in the payroll snapshot.

---

## 33. Payroll Snapshot

A payroll calculation creates a snapshot containing the relevant calculation state.

The snapshot should preserve:

* Employee;
* Branch;
* payroll period;
* salary configuration version;
* attendance inputs;
* calculation inputs;
* bonuses;
* calculated result;
* creation time;
* calculation source.

The snapshot prevents future configuration changes from rewriting historical payroll.

---

## 34. Payroll Calculation Repeatability

Given the same historical input snapshot and calculation rules, the system should produce the same payroll result.

Current salary configuration must not be used to recalculate historical finalized payroll.

---

## 35. Payroll Status

Payroll may follow:

```text id="pay762"
Draft
  ↓
Calculated
  ↓
Finalized
```

Additional operational states may be introduced where required, but finalized payroll must remain immutable.

---

## 36. Draft Payroll

Draft payroll is not final.

Authorized users may recalculate or correct draft data according to permissions.

Draft payroll must still maintain calculation traceability.

---

## 37. Calculated Payroll

Calculated payroll contains a complete calculation result but is not yet final.

Authorized users may review the calculation before finalization.

The calculation source and snapshot remain identifiable.

---

## 38. Payroll Finalization

Finalization makes the payroll result historically authoritative.

After finalization:

* the payroll result cannot be silently edited;
* salary configuration cannot rewrite it;
* attendance changes do not silently rewrite it;
* bonuses do not silently rewrite it.

Any required change uses a separate correction process.

---

## 39. Payroll Correction

A payroll correction is a separate operation.

It must contain:

* original payroll reference;
* correction amount/state;
* reason;
* actor;
* timestamp;
* relevant source data.

The original finalized payroll remains unchanged.

---

## 40. Payroll Correction Chain

Corrections must preserve a traceable relationship:

```text id="cor951"
Original Payroll
      ↓
Correction
      ↓
Additional Correction
```

The correction chain must remain immutable.

A correction must not overwrite the original payroll record.

---

## 41. Payroll Access

Payroll information is permission-controlled.

The system must validate:

* Business;
* Branch;
* Employee scope;
* permission;
* subscription state.

Unauthorized employees cannot access payroll information merely because they can access attendance.

---

## 42. Branch Payroll

Branch-scoped payroll calculations use the applicable Branch context.

A Branch Manager may only access payroll information permitted by:

* Branch scope;
* role;
* employee override;
* subscription entitlement.

Cross-Branch payroll access requires appropriate authority.

---

## 43. Business-Level Payroll

Authorized Owners may view and manage payroll across the Business subject to their permissions.

Business-level access does not remove the requirement for historical integrity.

Every Branch-specific payroll calculation remains identifiable by Branch.

---

## 44. Employee Payroll Privacy

Payroll information is more restricted than ordinary employee information.

Access must be permission-controlled.

The system should expose only the data necessary for the authorized operation.

---

## 45. Salary Self-Modification

Employees must not normally modify their own salary configuration.

If an exceptional administrative workflow allows such a change, it must require independent authorization and full audit.

Self-escalation is prohibited.

---

## 46. Attendance and Payroll Relationship

Attendance may be an input to payroll, but attendance and payroll remain separate entities.

Correcting attendance does not automatically modify a finalized payroll.

If a correction affects a finalized payroll, the system creates a payroll correction workflow.

---

## 47. Salary Change During Payroll Period

If salary configuration changes during a payroll period:

* the old configuration applies to the period before its effective date;
* the new configuration applies from its effective date;
* the calculation must preserve the applicable configuration version for each portion.

The system must not apply the newest salary configuration retroactively.

---

## 48. Bonus During Payroll Period

A bonus applies according to its configured applicable period.

Adding a bonus does not rewrite finalized payroll.

If the payroll is already finalized, the bonus requires a correction process.

---

## 49. Attendance Change During Payroll Period

Attendance may be corrected before payroll finalization according to permission.

The system may recalculate draft/calculated payroll using the corrected attendance.

After finalization, the attendance correction does not silently change payroll.

---

## 50. Payroll and Reports

Payroll data may be included in authorized reports.

Reports must use the relevant payroll snapshot/version.

Historical reports must not calculate old payroll using current salary configuration.

---

## 51. Payroll Notifications

The system may generate notifications for configured payroll events, including:

* salary due;
* payroll calculation ready;
* payroll finalization;
* payroll correction;
* payroll processing failure.

Notification failure must not roll back payroll operations.

---

## 52. Payroll and Subscription

Payroll operations are subject to subscription entitlement.

When payroll functionality becomes unavailable:

* historical payroll remains stored;
* authorized read-only access follows subscription lifecycle;
* new modifying payroll operations are blocked.

Offline authorization cannot bypass the restriction.

---

## 53. Attendance and Subscription

Attendance operations are also subject to subscription entitlement where configured.

Historical attendance remains available according to the subscription lifecycle.

Expired or read-only Businesses cannot use offline operations to bypass entitlement restrictions.

---

## 54. Payroll Concurrency

Concurrent payroll calculation/finalization requests must be protected.

The system must prevent:

* duplicate finalization;
* duplicate payroll snapshots;
* duplicate correction application;
* conflicting simultaneous finalization.

Idempotency and appropriate locking/version checks must be used.

---

## 55. Payroll Idempotency

Payroll operations that may be retried must use stable operation UUIDs or equivalent idempotency protection.

Repeated requests must not create duplicate payroll results.

---

## 56. Attendance Concurrency

Concurrent attendance operations must not create contradictory duplicate records.

The system should validate the Employee's current attendance state before accepting a new state-changing operation.

---

## 57. Payroll Calculation Failure

If payroll calculation fails:

* the calculation is marked Failed;
* the failure is logged;
* the failed operation does not become Finalized;
* retry is possible according to the background job policy.

Partial payroll results must not be treated as authoritative.

---

## 58. Payroll Finalization Failure

Finalization is atomic.

If finalization fails:

* the payroll remains non-finalized;
* no partial finalization is accepted;
* the operation may be retried safely.

---

## 59. Background Payroll Processing

Heavy payroll calculations may run as background jobs.

Background processing must:

* use a job UUID;
* be idempotent;
* support retry;
* preserve failure state;
* maintain audit context.

Background processing must not block POS operations.

---

## 60. Offline Payroll

Normal payroll finalization should be server-authoritative.

Offline devices may retain and synchronize permitted attendance and supporting payroll data, but cannot bypass server payroll authorization and finalization rules.

---

## 61. Offline Attendance Synchronization

Offline attendance synchronization follows general synchronization rules:

```text id="off533"
Pending
  ↓
Syncing
  ↓
Synced
```

Possible failure states include:

* Retrying;
* Conflict;
* Failed.

The original local attendance event remains identifiable.

---

## 62. Audit

Important attendance and payroll operations must be audited.

Audit events include:

* attendance creation;
* attendance correction;
* salary configuration creation/change;
* bonus creation;
* payroll calculation;
* payroll finalization;
* payroll correction;
* conflict resolution;
* administrative intervention.

---

## 63. Audit Context

Relevant audit data includes:

* Event UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Actor UUID;
* Device UUID where applicable;
* Payroll UUID;
* Attendance UUID where applicable;
* salary configuration UUID/version;
* timestamp;
* old state;
* new state;
* reason;
* result;
* source.

Audit records are immutable.

---

## 64. Historical Integrity

Historical attendance and payroll records must remain reconstructable.

The system must not silently overwrite:

* attendance history;
* salary configuration history;
* bonus history;
* payroll snapshots;
* finalized payroll;
* correction history.

---

## 65. Error Handling

Attendance and payroll errors are classified as:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

The user receives a business-safe message.

Technical details remain in logs.

---

## 66. Recovery

Recovery relies on:

* transaction rollback;
* idempotency;
* retry;
* immutable snapshots;
* correction chains;
* audit;
* conflict resolution.

The system must not recover by deleting historical payroll or attendance data.

---

## 67. Performance

Attendance operations must remain lightweight.

Payroll calculation should be isolated from POS operations.

Heavy payroll calculations, exports and historical calculations may run asynchronously.

The system must not require high-end POS hardware for ordinary attendance operations.

---

## 68. System Invariants

The following invariants apply to Attendance and Payroll:

1. Every attendance record has a stable UUID.
2. Every payroll record has a stable UUID.
3. Attendance is associated with an Employee.
4. Payroll is associated with an Employee.
5. Business context is preserved.
6. Branch context is preserved where applicable.
7. Inactive Employees remain historically visible.
8. Inactive Employees cannot normally create new attendance.
9. Attendance history is not deleted because of Employee deactivation.
10. Payroll history is not deleted because of Employee deactivation.
11. Attendance and salary configuration are separate entities.
12. Salary configuration changes do not rewrite historical attendance.
13. Attendance corrections preserve the original state.
14. Attendance correction requires appropriate permission.
15. Unauthorized self-modification is prohibited.
16. Offline attendance uses stable UUIDs.
17. Duplicate offline attendance synchronization does not create duplicate records.
18. Offline attendance preserves original event time.
19. Server validation remains authoritative after synchronization.
20. Attendance conflicts are explicit.
21. Attendance conflict resolution is authorized and audited.
22. Salary configurations are versioned when changes affect payroll.
23. Previous salary configurations remain historically available.
24. Salary configuration has an effective date.
25. Historical payroll uses the salary configuration effective for that period.
26. Supported salary models include Fixed, Percentage, Shift, Daily Pay and Hybrid.
27. Bonuses are separate payroll components.
28. Bonuses are attributable to an actor.
29. Payroll periods have valid start and end dates.
30. Payroll calculation uses a consistent snapshot.
31. Payroll snapshots preserve relevant calculation inputs.
32. Finalized payroll is immutable.
33. Finalized payroll cannot be silently recalculated from current configuration.
34. Payroll corrections are separate operations.
35. Corrections preserve the original payroll.
36. Payroll correction chains remain traceable.
37. Attendance corrections do not silently rewrite finalized payroll.
38. Salary changes do not silently rewrite finalized payroll.
39. Bonus changes do not silently rewrite finalized payroll.
40. A finalized payroll affected by later data requires a correction workflow.
41. Payroll access is permission-controlled.
42. Attendance access is permission-controlled.
43. Branch payroll is Branch-scoped.
44. Cross-Branch payroll access requires appropriate authority.
45. Payroll privacy is more restricted than ordinary employee information where configured.
46. Employees cannot normally modify their own salary configuration.
47. Payroll finalization is atomic.
48. Duplicate payroll finalization is prevented.
49. Duplicate payroll calculation is prevented.
50. Duplicate payroll correction is prevented.
51. Payroll failures do not produce finalized partial results.
52. Payroll retry is idempotent.
53. Heavy payroll processing must not block POS.
54. Offline devices cannot finalize payroll outside server authority.
55. Subscription entitlement controls payroll modification.
56. Subscription expiry does not delete historical payroll.
57. Subscription expiry does not delete historical attendance.
58. Audit records for important payroll and attendance operations are immutable.
59. Historical salary configuration remains reconstructable.
60. Historical attendance remains reconstructable.
61. Historical payroll remains reconstructable.
62. System-generated payroll operations use SYSTEM actor where applicable.
63. Device context is retained for important offline/administrative operations.
64. Configuration and attendance conflicts cannot be silently overwritten.
65. Payroll reports use the relevant payroll snapshot.
66. Current salary configuration cannot reinterpret finalized payroll.
67. Current attendance cannot silently alter finalized payroll.
68. Core payroll operations are transactionally consistent.
69. Secondary notification failure does not roll back payroll.
70. Payroll calculation failure is recoverable through retry.
71. Finalization failure leaves payroll non-finalized.
72. Historical integrity takes priority over UI convenience.
73. Payroll and attendance operations remain attributable to responsible actors.
74. Branch changes do not rewrite historical attendance or payroll.
75. Salary configuration changes become effective only from their defined effective point.

---

## 69. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 70. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `19_Attendance_and_Payroll.md`

**Next Document:** `20_Reports_and_Report_Versioning.md`

