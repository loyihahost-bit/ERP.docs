# Employee and Payroll Domain

**Document ID:** DA-12
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Employee and Payroll domain manages employees, employment state, branch assignments, attendance, salary configuration, payroll periods, salary calculations, bonuses, and payroll history.

The domain is responsible for:

* employee lifecycle;
* employee-to-branch assignments;
* role association;
* salary configuration;
* salary calculation;
* attendance;
* payroll periods;
* payroll snapshots;
* bonuses;
* payroll finalization;
* payroll corrections;
* historical employee and payroll integrity.

The domain does not own:

* authentication credentials;
* role permission definitions;
* subscription entitlements;
* Orders;
* Payments;
* Cash Sessions;
* Inventory;
* Reports.

Those concerns remain owned by their respective domains.

---

# 2. Employee Context

An Employee represents a business-level worker who can operate within one or more Branches.

The logical relationship is:

```text
Business
   ↓
Employee
   ↓
Branch Assignment
   ↓
Role / Permission Context
```

An Employee may have different effective permissions in different Branches.

---

# 3. Employee Identity

Each Employee has a stable Employee UUID.

Employee identity remains stable throughout the employee's lifecycle.

Deactivation does not require creating a replacement identity.

Historical records continue referencing the original Employee UUID.

---

# 4. Employee Lifecycle

The logical lifecycle is:

```text
Created
   ↓
Active
   ↓
Inactive
```

An inactive Employee remains part of historical data.

An inactive Employee is not automatically deleted.

---

# 5. Created State

Created means the Employee record exists but has not necessarily become operationally active.

The employee may still require:

* account setup;
* Branch assignment;
* role assignment;
* salary configuration;
* activation.

The exact activation workflow is controlled by the relevant application and access domains.

---

# 6. Active State

An Active Employee may perform operations allowed by:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

Active status alone does not grant operational permission.

---

# 7. Inactive State

An inactive Employee cannot perform new normal business operations.

Historical information remains accessible according to permission and retention rules.

Examples of retained history include:

* Orders created by the employee;
* Payments;
* Cash Sessions;
* attendance;
* payroll;
* corrections;
* audit events.

---

# 8. Employee and Authentication

Authentication is owned by the Identity and Access domain.

The Employee domain provides the business identity referenced by authentication.

The Employee domain must not store authentication secrets as its primary responsibility.

---

# 9. Employee and Permissions

Permissions are owned by the Identity and Access domain.

Employee data provides:

* Employee identity;
* role association;
* Branch assignments;
* employment state.

The effective permission calculation remains outside the payroll model.

---

# 10. Branch Assignment

An Employee may be assigned to multiple Branches.

Each assignment may contain its own operational context.

For example:

```text
Employee A
 ├── Branch 1 → Manager permissions
 └── Branch 2 → Cashier permissions
```

Branch-specific access must not be inferred from employment alone.

---

# 11. Branch Assignment Lifecycle

A Branch assignment may conceptually be:

```text
Assigned
   ↓
Active
   ↓
Removed
```

Removing an assignment does not remove historical operations performed while the assignment was active.

---

# 12. Multiple Branch Employment

When an Employee switches Branches, the system recalculates:

* Branch scope;
* effective permissions;
* available operational functions;
* relevant attendance context;
* payroll scope where applicable.

The previous Branch history remains unchanged.

---

# 13. Role Association

Employee records reference roles configured by the business.

Role configuration belongs to the Identity and Access domain.

Payroll may use role information when a salary model depends on role or when attendance/reporting requires role context.

Payroll must not modify permissions through salary configuration.

---

# 14. Attendance Context

Attendance records track Employee work presence.

Attendance may include:

* Employee UUID;
* Branch;
* work date;
* start time;
* end time;
* status;
* correction information.

The exact attendance UI is an application concern.

---

# 15. Attendance Lifecycle

The conceptual attendance lifecycle is:

```text
Not Started
   ↓
Present / Started
   ↓
Ended
```

Correction may occur through a separate controlled process.

Historical attendance must not be silently overwritten.

---

# 16. Attendance and Branch

Attendance is Branch-scoped.

An Employee working in multiple Branches must have attendance attributable to the correct Branch.

Cross-Branch attendance must not be merged into an unrelated Branch.

---

# 17. Attendance and Role

Attendance may preserve the Employee's effective role context at the time of the attendance event.

This supports historical reconstruction if the Employee's role later changes.

---

# 18. Attendance Correction

Attendance corrections require appropriate permission.

A correction should preserve:

* original value;
* corrected value;
* actor;
* timestamp;
* reason;
* affected Employee;
* affected Branch.

The original attendance record remains historically reconstructable.

---

# 19. Salary Models

The system supports the following salary models:

* Fixed;
* Percentage;
* Shift;
* Hybrid;
* Daily Pay;
* Bonuses.

A Business may configure the applicable salary model according to its operational needs.

---

# 20. Fixed Salary

Fixed salary represents a predefined amount for the relevant payroll period.

The calculation does not depend directly on the number of completed shifts unless additional business configuration explicitly introduces such a dependency.

---

# 21. Percentage Salary

Percentage salary is based on an applicable business-defined percentage.

The exact calculation base must be defined by salary configuration and preserved in the payroll snapshot.

---

# 22. Shift Salary

Shift salary is based on qualifying shifts.

The Payroll domain uses valid attendance/shift information according to the configured salary rules.

---

# 23. Hybrid Salary

Hybrid salary combines multiple configured components.

Examples may include:

```text
Base Amount
+
Shift Component
+
Percentage Component
+
Bonus
```

Each component must remain separately identifiable in the payroll calculation.

---

# 24. Daily Pay

Daily Pay calculates compensation based on qualifying work days.

The payroll snapshot must retain the values used in the calculation.

---

# 25. Bonuses

Bonuses are separate payroll components.

A bonus may include:

* amount;
* reason/comment;
* Employee;
* Branch where applicable;
* payroll period;
* actor;
* timestamp.

Bonuses must not silently modify the base salary configuration.

---

# 26. Salary Configuration

Salary configuration is separate from permissions.

A salary configuration may include:

* salary model;
* amount or rate;
* effective date;
* Branch scope where applicable;
* additional parameters;
* status.

---

# 27. Salary Change

When salary configuration changes, the system preserves:

* previous configuration;
* new configuration;
* effective date;
* actor;
* reason where required.

Historical payroll must continue using the configuration captured for its period.

---

# 28. Effective Date

A salary configuration becomes effective according to its configured effective date.

A later salary change must not retroactively modify finalized payroll periods.

---

# 29. Payroll Period

Payroll is calculated by period.

A payroll period may be:

* monthly;
* or another configured business period where supported.

The exact period configuration belongs to business configuration.

---

# 30. Payroll Calculation

Payroll calculation uses the applicable historical inputs for the period.

Possible inputs include:

* salary configuration;
* attendance;
* shifts;
* percentage base;
* daily work;
* bonuses.

The calculation must produce a reproducible result.

---

# 31. Payroll Snapshot

When payroll is calculated, the system creates a calculation snapshot.

The snapshot should preserve:

* Employee;
* Branch;
* payroll period;
* salary model;
* applicable rate/amount;
* attendance inputs;
* calculation inputs;
* bonuses;
* calculated amount;
* calculation timestamp.

This prevents future configuration changes from silently changing historical payroll.

---

# 32. Payroll Finalization

Payroll may be finalized after calculation and review.

A finalized payroll record is treated as historical financial information.

Finalization prevents ordinary modification.

---

# 33. Payroll Correction

If a finalized payroll requires correction, the system must use a separate correction mechanism.

The correction must preserve:

* original payroll;
* corrected value;
* reason;
* actor;
* timestamp;
* relationship between original and correction.

The original payroll snapshot remains immutable.

---

# 34. Payroll Recalculation

A payroll calculation may be repeated before finalization.

After finalization, recalculation must not silently replace the historical result.

A correction/revision process is required instead.

---

# 35. Payroll and Attendance

Attendance provides operational input for salary models that depend on work presence.

Attendance corrections after payroll calculation may make a payroll result outdated.

Such changes must therefore be handled through controlled recalculation or correction.

---

# 36. Payroll and Branch

Payroll records preserve Branch context where salary is Branch-specific.

If an Employee works in multiple Branches, the system must retain enough context to determine which Branch contributed to the payroll calculation.

---

# 37. Employee Transfer Between Branches

When an Employee changes Branch:

* historical attendance remains with the original Branch;
* historical payroll remains linked to its original context;
* future attendance uses the new Branch;
* future payroll uses the applicable new configuration.

Historical records must not be reassigned silently.

---

# 38. Employee Deactivation

When an Employee becomes inactive:

* new operational access is blocked;
* new normal attendance cannot begin;
* future payroll calculations do not treat the employee as actively employed unless explicitly required by the applicable payroll rules;
* historical payroll remains available;
* historical attendance remains available.

---

# 39. Employee Reactivation

If an Employee is reactivated, the existing Employee identity is reused.

Historical data is not recreated.

New permissions and Branch assignments are evaluated according to their current configuration.

---

# 40. Offline Employee Operations

Supported employee-related operations may continue offline only on trusted devices with valid offline authorization.

Offline operations must respect:

* Employee status;
* Branch scope;
* effective permissions;
* subscription entitlement;
* offline authorization expiry.

---

# 41. Employee Deactivation While Offline

If an Employee becomes inactive on the server while a device is offline, the device cannot indefinitely continue to authorize that Employee.

When synchronization or server validation occurs, operations after the effective deactivation point must be rejected or represented as conflicts according to the synchronization rules.

---

# 42. Permission Changes During Active Sessions

A change in Employee permissions may occur while the Employee has an active application session.

Important operations must be validated against the current effective permission state.

The Employee domain does not assume that an old UI state grants permanent authority.

---

# 43. Subscription Dependency

Employee creation and management are subject to subscription entitlements.

For example:

* employee count limit;
* enabled payroll functionality;
* enabled Branch count.

Subscription enforcement belongs to the Subscription domain.

The Employee domain consumes the resulting entitlement decision.

---

# 44. Subscription Downgrade

When a subscription downgrade reduces the permitted Employee count:

* existing Employees are preserved;
* existing historical data is preserved;
* new Employee creation is blocked when the limit is already reached;
* existing Employees are not silently deleted.

---

# 45. Payroll Access

Payroll information is sensitive business data.

Access requires appropriate permissions and Branch/business scope.

An Employee must not gain payroll access merely because the Employee belongs to the Business.

---

# 46. Salary Privacy

Salary information must be exposed only to authorized users.

The domain must avoid unnecessarily exposing:

* salary amount;
* salary rate;
* payroll result;
* bonuses;
* payroll corrections.

Sensitive payroll information must respect the established access model.

---

# 47. Payroll and Reports

The Reporting domain may consume finalized payroll data.

Payroll remains the authoritative source for payroll calculations.

Reports must not recalculate payroll independently.

---

# 48. Payroll and Audit

Important payroll operations should produce audit events.

Examples include:

* salary configuration change;
* attendance correction;
* bonus creation;
* payroll finalization;
* payroll correction;
* employee deactivation;
* Branch assignment change.

Audit remains owned by the Audit domain.

---

# 49. Domain Services

Potential Employee and Payroll domain services include:

```text
Employee Lifecycle Service
Branch Assignment Service
Attendance Service
Attendance Correction Service
Salary Configuration Service
Payroll Calculation Service
Payroll Finalization Service
Payroll Correction Service
Bonus Service
Payroll Snapshot Service
```

These are logical domain services and do not necessarily represent separate applications.

---

# 50. Domain Events

Potential events include:

```text
EmployeeCreated
EmployeeActivated
EmployeeDeactivated
EmployeeReactivated
EmployeeBranchAssigned
EmployeeBranchAssignmentRemoved
AttendanceStarted
AttendanceEnded
AttendanceCorrected
SalaryConfigurationChanged
BonusAdded
PayrollCalculated
PayrollFinalized
PayrollCorrectionCreated
```

Events represent facts that have already occurred.

---

# 51. Aggregate Boundaries

The Employee and Payroll domain may conceptually contain:

* Employee;
* Employee Branch Assignment;
* Attendance Record;
* Salary Configuration;
* Payroll Period;
* Payroll Record;
* Payroll Snapshot;
* Bonus;
* Payroll Correction.

It does not own:

* Authentication;
* Role definitions;
* Permission definitions;
* Subscription;
* Orders;
* Payments;
* Cash Sessions;
* Inventory;
* Reports;
* Audit infrastructure.

---

# 52. Concurrency

Employee and payroll operations must protect against concurrent modifications.

Examples include:

* two users changing salary configuration;
* two users correcting attendance;
* two users finalizing the same payroll period;
* duplicate bonus creation;
* duplicate payroll calculation requests.

The implementation must use appropriate transaction, uniqueness, idempotency, and concurrency controls.

---

# 53. Payroll Finalization Concurrency

Only one valid finalization operation may succeed for the same Employee/Branch/payroll-period scope.

Repeated requests must not create duplicate finalized payroll records.

---

# 54. Attendance Concurrency

Concurrent attendance operations for the same Employee and applicable Branch must respect the valid attendance state.

The system must prevent impossible duplicate active attendance states.

---

# 55. Salary Configuration Concurrency

Concurrent salary changes must preserve deterministic effective configuration.

The system must not silently lose one valid configuration change.

Conflicting changes should be rejected or resolved through explicit rules.

---

# 56. Offline Synchronization

Offline Employee and Payroll events use stable UUIDs.

Synchronization must:

* preserve original identities;
* validate Employee state;
* validate Branch scope;
* validate permissions;
* validate subscription;
* preserve historical timestamps;
* prevent duplicate payroll/attendance events.

---

# 57. Historical Integrity

Historical employee and payroll records must remain reconstructable.

The system must not silently rewrite historical:

* Employee identity;
* Branch context;
* salary configuration;
* attendance;
* payroll;
* bonus;
* correction information.

---

# 58. Employee and Audit History

Employee changes that affect business operations should be historically traceable.

Examples:

```text
Employee
   ↓
Role Change
Branch Assignment
Salary Change
Status Change
Attendance Correction
Payroll Correction
```

The exact audit event structure belongs to the Audit domain.

---

# 59. Employee and Notification

The Notification domain may generate notifications for:

* salary due;
* payroll completion;
* payroll correction;
* important employee status changes.

Notifications do not change Employee or Payroll state.

---

# 60. Error Boundary

Invalid Employee/Payroll operations must produce controlled domain errors.

Examples include:

* inactive Employee;
* unauthorized Branch;
* duplicate attendance;
* invalid salary configuration;
* payroll already finalized;
* invalid payroll period;
* duplicate payroll finalization;
* subscription limit reached;
* insufficient permission.

The global error model is defined by System Analysis.

---

# 61. Employee and Data Lifecycle

Employee and Payroll data follows Business data lifecycle rules.

If a Business enters deletion lifecycle:

* active operational access is blocked according to subscription/lifecycle rules;
* historical Employee and Payroll data remains available during the retention period;
* deletion follows the Data Lifecycle domain.

---

# 62. Performance

Employee and Payroll operations must not unnecessarily block POS operations.

Heavy payroll calculations may be executed asynchronously.

Simple employee/attendance operations should remain responsive on ordinary Branch hardware.

---

# 63. Invariants

### Employee Identity

1. Every Employee has a stable UUID.
2. Employee identity remains stable after deactivation.
3. Deactivation does not delete historical Employee references.
4. Historical operations continue referencing the original Employee UUID.

### Lifecycle

5. Employee lifecycle supports Created, Active, and Inactive states.
6. Inactive Employees cannot perform new normal operational actions.
7. Reactivation reuses the existing Employee identity.
8. Historical data survives Employee deactivation.

### Branch

9. Employee Branch assignments are explicit.
10. An Employee may belong to multiple Branches.
11. Branch-specific scope is preserved.
12. Removing a Branch assignment does not rewrite historical records.
13. Future operations use current Branch assignment.
14. Historical operations retain their original Branch context.

### Permissions

15. Employee status does not itself grant permissions.
16. Effective permissions include Role Permission.
17. Employee Overrides may affect effective permissions.
18. Branch Scope affects effective permissions.
19. Subscription Entitlement affects available functionality.
20. Payroll configuration cannot silently grant operational permissions.

### Attendance

21. Attendance is attributable to an Employee.
22. Attendance is Branch-scoped.
23. Attendance state transitions are valid and deterministic.
24. Duplicate active attendance states are prevented.
25. Attendance corrections preserve the original state.
26. Attendance corrections record actor and reason.
27. Historical attendance remains reconstructable.

### Salary

28. Supported salary models include Fixed, Percentage, Shift, Hybrid, Daily Pay, and Bonuses.
29. Salary configuration is separate from permission configuration.
30. Salary changes preserve historical configuration.
31. Salary effective dates are explicit.
32. Future salary changes do not silently rewrite historical payroll.
33. Bonuses remain separately identifiable.

### Payroll

34. Payroll is period-based.
35. Payroll calculations use applicable historical inputs.
36. Payroll calculations are reproducible from their snapshots.
37. Finalized payroll is immutable through ordinary editing.
38. Finalized payroll corrections are separate records.
39. Payroll corrections preserve the original payroll result.
40. Duplicate payroll finalization is prevented.
41. Payroll access is permission-controlled.
42. Payroll scope is Business/Branch aware.

### Offline

43. Offline Employee operations require trusted-device authorization.
44. Offline operations respect Employee status known to the device.
45. Server-side deactivation ultimately prevents continued authorization.
46. Offline events use stable UUIDs.
47. Offline payroll/attendance events synchronize idempotently.

### Concurrency

48. Concurrent payroll finalization is controlled.
49. Concurrent attendance operations are controlled.
50. Concurrent salary changes are controlled.
51. Duplicate bonus creation is prevented.
52. Duplicate payroll calculation requests are handled idempotently.

### Historical Integrity

53. Employee status history is reconstructable.
54. Branch assignment history is reconstructable.
55. Salary configuration history is reconstructable.
56. Attendance correction history is reconstructable.
57. Payroll correction history is reconstructable.
58. Historical payroll does not depend on current salary configuration.

### Security

59. Salary information is sensitive.
60. Payroll information is permission-controlled.
61. Unauthorized employees cannot access payroll information.
62. Cross-Branch payroll access is rejected unless authorized.
63. Subscription restrictions are enforced.

### Integration

64. Reports consume payroll results rather than independently recalculating them.
65. Audit records important Employee/Payroll changes.
66. Notifications do not directly modify payroll state.
67. Employee domain does not own authentication secrets.
68. Payroll does not own subscription enforcement.
69. Payroll does not own permission definitions.
70. Employee/Payroll does not directly modify Orders, Payments, Inventory, or Cash Sessions.

---

# 64. Completion Criteria

The Employee and Payroll domain is complete when:

* Employee lifecycle is defined;
* Employee identity is stable;
* Branch assignments are defined;
* role/permission boundaries are defined;
* attendance lifecycle is defined;
* attendance corrections are defined;
* salary models are defined;
* salary configuration history is defined;
* payroll periods are defined;
* payroll calculation snapshots are defined;
* payroll finalization is defined;
* payroll corrections are defined;
* bonuses are defined;
* multi-Branch employment is defined;
* offline behavior is defined;
* synchronization behavior is defined;
* concurrency boundaries are defined;
* historical integrity is defined;
* sensitive payroll access is defined;
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

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

