# Employee Attendance and Payroll Data Model

**Document ID:** DB-18
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Employee attendance;
* Work sessions;
* Attendance corrections;
* Salary configuration;
* Salary calculation;
* Payroll periods;
* Payroll records;
* Bonuses;
* Deductions;
* Payroll finalization;
* Branch-specific employment;
* Role-aware attendance;
* Offline attendance;
* Payroll history;
* Corrections;
* Audit;
* Reporting.

The model must support flexible salary models while preserving finalized payroll history.

---

## 2. Design Principles

The Employee Attendance and Payroll model follows these principles:

1. Employee identity is defined by the Identity and Access domain.
2. Attendance records belong to a Business and Branch.
3. An Employee may work in multiple Branches.
4. Branch assignment determines operational scope.
5. Attendance records preserve Employee identity.
6. Attendance corrections never silently overwrite original records.
7. Salary configuration is separate from calculated payroll.
8. Supported salary models are Fixed, Percentage, Shift, Hybrid, and Daily Pay.
9. Bonuses are supported.
10. Payroll is period-based.
11. Payroll calculations create historical snapshots.
12. Finalized payroll is immutable.
13. Corrections are separate from finalized payroll.
14. Salary configuration changes do not rewrite previous payroll.
15. Payroll calculations must preserve the exact inputs used.
16. Offline attendance is allowed for trusted authorized devices.
17. Payroll finalization requires appropriate authorization.
18. Payroll must remain Business and Branch isolated.
19. Subscription limits may restrict new employee creation without deleting historical payroll.
20. Payroll and attendance must remain auditable.

---

## 3. Employee Ownership

Employee records are owned by the Identity and Access model.

Conceptually:

```text id="q6m2v8"
Business
   ↓
Employee
   ↓
Branch Assignment
   ↓
Attendance
   ↓
Payroll
```

Attendance and Payroll must reference the existing Employee identity.

They must not create a second employee identity.

---

## 4. Employee Branch Scope

An Employee may be assigned to one or multiple Branches.

Each assignment determines whether the Employee can:

* record attendance;
* work shifts;
* receive branch payroll;
* operate within that Branch.

Historical attendance remains associated with the Branch where the work occurred.

---

## 5. Attendance Identity

Every Attendance record should have a permanent UUID.

Suggested:

```text id="x8p4m1"
attendance.id
```

The UUID:

* is globally unique;
* supports offline creation;
* is used for synchronization idempotency;
* remains unchanged;
* is never reused.

---

## 6. Attendance Record

Suggested conceptual fields:

```text id="m3q7v2"
id
business_id
branch_id
employee_id
device_id
attendance_type
status
started_at
ended_at
source
created_at
updated_at
```

Additional fields may store correction/version information.

---

## 7. Attendance Types

The current model may use:

```text id="p8n4x6"
CLOCK_IN
CLOCK_OUT
```

or a work-session model:

```text id="v2m7q5"
WORK_SESSION
```

The implementation should avoid duplicating the same attendance event through multiple representations.

---

## 8. Recommended Work Session Model

A Work Session may represent one continuous working period:

```text id="k5q8m2"
Work Session
    ↓
Clock In
    ↓
Clock Out
```

Suggested fields:

```text id="r7v3n9"
id
business_id
branch_id
employee_id
device_id
started_at
ended_at
status
source
version
created_at
updated_at
```

---

## 9. Work Session Status

Suggested states:

```text id="c8m4p1"
OPEN
CLOSED
CORRECTED
CANCELLED
```

A finalized historical Work Session must not be silently deleted.

---

## 10. One Open Work Session

The system should normally prevent one Employee from having multiple active Work Sessions in the same Branch.

Example invalid state:

```text id="x4n8q2"
Employee A
 ├── Work Session 1 OPEN
 └── Work Session 2 OPEN
```

If multi-role or cross-branch simultaneous work is introduced later, the uniqueness rule may be scoped accordingly.

---

## 11. Branch Requirement

Attendance must reference the Branch where the employee is working.

Cross-Branch attendance must not be created accidentally through a client-provided Branch UUID.

The server validates Employee Branch assignment.

---

## 12. Attendance Source

Attendance may originate from:

```text id="v7m2q8"
ONLINE
OFFLINE
ADMIN_CORRECTION
SYSTEM
```

The original source must remain historically available.

---

## 13. Device Attribution

Attendance should preserve the Device used for the operation where applicable.

This supports:

* offline validation;
* security investigation;
* audit;
* synchronization;
* device revocation.

---

## 14. Attendance Timestamp

Attendance timestamps must be timezone-aware.

The system should preserve:

* client event time;
* server receipt time where applicable;
* server authoritative time.

Clock anomalies must be detectable.

---

## 15. Offline Attendance

Trusted devices may record Attendance offline when authorized.

Offline attendance must contain:

* Employee UUID;
* Branch UUID;
* Device UUID;
* Attendance UUID;
* local timestamp;
* offline authorization context.

Synchronization later validates the event.

---

## 16. Inactive Employee

If an Employee becomes inactive while an offline Attendance event exists, synchronization must not silently reactivate the Employee.

The event must be:

* accepted if valid under the business rules at event time;
* rejected;
* or placed into an explicit conflict state.

---

## 17. Attendance Correction

Attendance may require correction because of:

* forgotten clock-out;
* incorrect time;
* wrong Branch;
* duplicate attendance;
* administrative correction.

The original event must remain available.

---

## 18. Attendance Correction Model

Suggested:

```text id="q5m8v3"
Attendance
   ↓
Attendance Correction
```

Suggested fields:

```text id="n7p2x4"
id
attendance_id
actor_id
device_id
previous_value
new_value
reason
authorization_id
created_at
```

---

## 19. Attendance Correction Authorization

Attendance correction must require appropriate permission.

The original Employee attendance record must not be directly overwritten by unauthorized users.

---

## 20. Attendance History

Historical attendance should preserve:

* Employee;
* Branch;
* Device;
* original time;
* corrected time;
* source;
* correction actor;
* correction reason;
* correction timestamp.

This supports payroll reconstruction.

---

## 21. Role Relationship

Attendance may be associated with the Employee's effective role at the relevant time.

Current role configuration must not rewrite historical payroll or attendance.

If historical role snapshots are needed for payroll, the payroll calculation should store the effective role/input snapshot.

---

## 22. Salary Configuration

Salary configuration defines how an Employee's compensation is calculated.

It is separate from Payroll results.

Suggested:

```text id="f6m3q8"
Salary Configuration
       ↓
Payroll Calculation
       ↓
Payroll Record
```

---

## 23. Supported Salary Models

The system supports:

```text id="y2v7n4"
FIXED
PERCENTAGE
SHIFT
HYBRID
DAILY_PAY
```

Bonuses may be applied independently.

---

## 24. Fixed Salary

Fixed salary represents a predefined amount for a payroll period.

Example:

```text id="m8q3p5"
Monthly salary = 4,000,000
```

The amount is stored using an exact monetary type.

---

## 25. Percentage Salary

Percentage salary is based on a defined business measure.

Examples may include:

* sales;
* employee-attributed sales;
* branch sales;
* other configured eligible revenue.

The calculation source must be explicit.

The system must not infer the percentage base from arbitrary data.

---

## 26. Shift Salary

Shift salary calculates compensation based on completed eligible shifts.

Conceptually:

```text id="v5n2m8"
Eligible Shifts × Shift Rate
```

Only valid attendance/work sessions may contribute.

---

## 27. Hybrid Salary

Hybrid salary may combine multiple components.

Example:

```text id="q8m4x2"
Fixed Base
+
Percentage Component
+
Bonuses
```

Each component should be stored separately.

---

## 28. Daily Pay

Daily Pay is calculated from eligible work days.

Conceptually:

```text id="p3m7v9"
Eligible Days × Daily Rate
```

Attendance rules determine eligible days.

---

## 29. Bonus

Bonuses may be added to Payroll.

Suggested fields:

```text id="x6q2m8"
id
payroll_id
type
amount
reason
created_by
created_at
```

Bonuses require appropriate authorization.

---

## 30. Salary Configuration Identity

Every Salary Configuration should have a permanent UUID.

Suggested:

```text id="k4v8n3"
id
business_id
branch_id
employee_id
salary_type
effective_from
effective_to
status
version
created_at
updated_at
```

---

## 31. Salary Configuration Versioning

Salary configuration changes should create a new version rather than rewriting historical configuration.

Example:

```text id="m2q7p5"
Version 1
    ↓
Version 2
    ↓
Version 3
```

Previous versions remain available.

---

## 32. Effective Date

A Salary Configuration should have an effective date.

Payroll calculation uses the configuration effective for the relevant Payroll Period.

Changing the current salary must not alter finalized historical payroll.

---

## 33. Branch Salary Scope

Salary configuration may be Branch-specific.

An Employee working at multiple Branches may have different compensation configurations if permitted by the business.

The configuration must clearly identify its Branch scope.

---

## 34. Salary Configuration Authorization

Salary configuration changes require appropriate permission.

Normal employees must not be able to change their own salary configuration unless a specific business rule explicitly permits it.

---

## 35. Payroll Period

Payroll is calculated for a defined period.

Suggested fields:

```text id="r8m3q6"
id
business_id
branch_id
period_start
period_end
status
created_at
finalized_at
```

---

## 36. Payroll Period Status

Suggested lifecycle:

```text id="n5v8x2"
OPEN
CALCULATING
CALCULATED
FINALIZED
CORRECTED
CANCELLED
```

Finalization creates a historical financial snapshot.

---

## 37. Period Integrity

The following must hold:

```text id="q7m2k4"
period_start <= period_end
```

A Payroll Period must belong to one Business.

Branch-scoped Payroll Periods must belong to one Branch.

---

## 38. Payroll Record

A Payroll Record represents one Employee's compensation for a Payroll Period.

Suggested fields:

```text id="p4m8v1"
id
business_id
branch_id
payroll_period_id
employee_id
salary_configuration_id
base_amount
percentage_amount
shift_amount
daily_amount
bonus_amount
deduction_amount
gross_amount
net_amount
status
created_at
finalized_at
```

Not every field is required for every salary type.

---

## 39. Payroll Input Snapshot

At calculation time, the system should preserve the inputs used.

Examples:

* salary configuration version;
* eligible days;
* eligible shifts;
* percentage base;
* percentage rate;
* bonus values;
* deductions;
* attendance totals.

This prevents later configuration changes from rewriting historical calculations.

---

## 40. Payroll Calculation Snapshot

A Payroll Record should preserve a calculation snapshot or reference to an immutable calculation snapshot.

Conceptually:

```text id="x9q3m7"
Salary Config Version
        +
Attendance Data
        +
Sales/Eligible Base
        +
Bonuses
        ↓
Payroll Calculation Snapshot
        ↓
Payroll Record
```

---

## 41. Gross Payroll

Gross payroll is calculated before deductions.

Conceptually:

```text id="v4m8p2"
Gross =
Base
+
Percentage
+
Shift
+
Daily
+
Bonuses
```

Only applicable components participate.

---

## 42. Deductions

The current model may support payroll deductions as separate records.

Suggested fields:

```text id="k7n3q5"
id
payroll_id
type
amount
reason
created_by
created_at
```

Deductions must be permission-controlled.

---

## 43. Net Payroll

Conceptually:

```text id="m8q2v6"
Net =
Gross
-
Deductions
```

Net payroll cannot become negative unless a future explicit business rule allows it.

The current default should prevent negative net payroll.

---

## 44. Payroll Finalization

Finalization requires appropriate authorization.

After finalization:

* payroll values become immutable;
* calculation inputs remain reconstructable;
* salary configuration changes do not rewrite it;
* attendance changes do not silently rewrite it.

---

## 45. Finalized Payroll Correction

If finalized payroll is wrong:

```text id="q5v8m3"
Finalized Payroll
      ↓
Payroll Correction
      ↓
Corrected Financial State
```

The original payroll remains historically available.

---

## 46. Payroll Correction Fields

Suggested:

```text id="n2m7x4"
id
payroll_id
actor_id
device_id
previous_value
new_value
reason
authorization_id
created_at
```

---

## 47. Payroll Correction Authorization

Payroll correction requires appropriate permission.

The correction actor and reason must be preserved.

Large or unusual corrections may generate notifications.

---

## 48. Payroll and Attendance

Payroll calculation may use Attendance records.

The calculation must use the attendance state valid for the Payroll Period.

Corrections after finalization must not silently alter finalized payroll.

---

## 49. Payroll and Sales

Percentage-based salary must explicitly define its calculation base.

Possible bases may include:

```text id="w4p8n2"
EMPLOYEE_SALES
BRANCH_SALES
OTHER_CONFIGURED_BASE
```

The selected base must be stored in the Salary Configuration and calculation snapshot.

---

## 50. Payroll and Orders

Orders themselves remain operational records.

Payroll should not directly modify Orders.

Sales data is read as an input to the payroll calculation.

---

## 51. Payroll and Cash

Payroll is separate from Cash Sessions.

Paying salary is a financial operation that may later be connected to expenses or Cash Transactions, but payroll calculation itself does not automatically change POS cash.

---

## 52. Payroll Payment

If salary payment is implemented as a separate financial transaction, it should reference the finalized Payroll Record.

The Payroll Record must remain the authoritative salary calculation.

---

## 53. Payroll Status and Payment Status

Payroll calculation status and actual salary payment status must remain separate.

For example:

```text id="x7m2q4"
Payroll = FINALIZED
Payment = NOT_PAID
```

is valid.

---

## 54. Employee Deactivation

Deactivating an Employee must not delete:

* attendance;
* salary configuration history;
* payroll;
* bonuses;
* deductions;
* corrections.

Historical data remains available.

---

## 55. Subscription Employee Limits

If subscription limits the number of Employees:

* existing Employees remain;
* historical payroll remains;
* new Employee creation may be blocked;
* payroll for existing valid Employees remains accessible according to subscription rules.

Downgrade must not silently delete employees or payroll.

---

## 56. Payroll and Branch Deactivation

When a Branch becomes inactive:

* historical payroll remains;
* historical attendance remains;
* new attendance may be blocked;
* new payroll operations may be blocked according to business rules.

Historical records remain associated with the original Branch.

---

## 57. Offline Payroll

Offline devices may not need to perform complete payroll calculations.

The preferred model is:

* attendance may be recorded offline;
* payroll calculation/finalization remains server-authoritative where possible.

If offline calculation is supported later, the final server result remains authoritative.

---

## 58. Offline Attendance Synchronization

Offline attendance uses:

* Attendance UUID;
* Device UUID;
* Employee UUID;
* Branch UUID;
* local event time;
* durable local queue;
* synchronization state.

Duplicate synchronization must not create duplicate attendance.

---

## 59. Attendance Conflict

Possible conflicts:

* Employee inactive;
* Branch assignment removed;
* duplicate Work Session;
* overlapping Work Session;
* Device revoked;
* clock rollback;
* attendance already corrected;
* Payroll Period already finalized.

Conflicts must be explicit.

---

## 60. Payroll Calculation Concurrency

Only one authoritative Payroll calculation/finalization operation should control a Payroll Period at a time.

Concurrent finalization attempts must be serialized.

---

## 61. Payroll Version

Payroll Period and Payroll Record may use optimistic concurrency.

Suggested:

```text id="q8m4v2"
version
```

Stale modifications must be rejected.

---

## 62. Payroll Calculation Idempotency

Repeated calculation requests must not create duplicate Payroll Records.

A unique identity may be based on:

```text id="m3p7x5"
Payroll Period
+
Employee
+
Calculation Version
```

The exact implementation may use a dedicated calculation UUID.

---

## 63. Payroll Period Employee Uniqueness

Within a Payroll Period:

```text id="v6q2n8"
one active Payroll Record
per Employee
```

is the default rule.

Corrections create additional historical records rather than duplicate active payroll records.

---

## 64. Attendance Indexing

Recommended indexes:

```text id="p8m3q5"
attendance(business_id, branch_id, employee_id, started_at)
attendance(employee_id, started_at)
attendance(branch_id, started_at)
attendance(status, started_at)
attendance(device_id, created_at)
```

---

## 65. Salary Configuration Indexing

Recommended:

```text id="x4v8m2"
salary_configurations(business_id, employee_id, effective_from)
salary_configurations(branch_id, employee_id, effective_from)
salary_configurations(status, effective_from)
```

---

## 66. Payroll Indexing

Recommended:

```text id="n7q3m5"
payroll_periods(business_id, branch_id, period_start, period_end)
payroll_periods(status, period_start)

payroll_records(payroll_period_id, employee_id)
payroll_records(employee_id, created_at)
payroll_records(branch_id, created_at)

payroll_bonuses(payroll_id)
payroll_deductions(payroll_id)
payroll_corrections(payroll_id, created_at)
```

---

## 67. Monetary Types

All salary and payroll monetary values must use exact monetary types.

Floating-point values must not be used for:

* salary;
* bonus;
* deduction;
* gross payroll;
* net payroll;
* percentage calculation result.

---

## 68. Percentage Precision

Percentage rates should use an exact decimal representation.

Example:

```text id="q2m7v4"
7.50%
```

must not be stored using binary floating-point arithmetic.

---

## 69. Payroll Snapshot Integrity

A finalized Payroll Record must preserve enough information to answer:

* which salary configuration was used;
* which version was used;
* which attendance was included;
* which sales base was used;
* which bonuses were included;
* which deductions were included;
* who calculated it;
* who finalized it;
* when it was finalized.

---

## 70. Audit Requirements

Important operations must create Audit Events:

* Employee salary configuration created/changed;
* Attendance correction;
* Payroll calculation;
* Payroll finalization;
* Payroll correction;
* Bonus creation;
* Deduction creation;
* authorization;
* conflict resolution.

Routine attendance reads do not normally require audit events.

---

## 71. Notification Requirements

Notifications may be generated for:

* salary due;
* payroll finalized;
* payroll correction;
* abnormal payroll discrepancy;
* significant deduction;
* attendance conflict;
* repeated attendance correction.

Notification failure must not roll back payroll or attendance transactions.

---

## 72. Data Lifecycle

When subscription expires:

* historical attendance remains readable;
* historical payroll remains readable;
* modifying payroll operations may be blocked.

During Business deletion:

* attendance;
* salary configurations;
* payroll periods;
* payroll records;
* bonuses;
* deductions;
* corrections

are deleted according to the controlled dependency-aware lifecycle.

---

## 73. Historical Integrity

The system must preserve or reconstruct:

* Employee;
* Branch;
* attendance time;
* salary configuration version;
* payroll calculation inputs;
* gross amount;
* deductions;
* net amount;
* bonuses;
* correction history;
* finalization actor;
* finalization time.

Current salary configuration must never rewrite historical payroll.

---

## 74. Suggested `work_sessions` Fields

```text id="v8m2q5"
id
business_id
branch_id
employee_id
device_id
started_at
ended_at
status
source
version
created_at
updated_at
```

---

## 75. Suggested `attendance_corrections` Fields

```text id="m4q7x2"
id
business_id
branch_id
attendance_id
actor_id
device_id
previous_value
new_value
reason
authorization_id
created_at
```

---

## 76. Suggested `salary_configurations` Fields

```text id="q8v3m5"
id
business_id
branch_id
employee_id
salary_type
fixed_amount
percentage_rate
percentage_base
shift_rate
daily_rate
effective_from
effective_to
status
version
created_at
updated_at
```

Not every field applies to every salary type.

---

## 77. Suggested `payroll_periods` Fields

```text id="n5m2x8"
id
business_id
branch_id
period_start
period_end
status
calculation_version
calculated_at
finalized_at
finalized_by
version
created_at
updated_at
```

---

## 78. Suggested `payroll_records` Fields

```text id="p7q4m2"
id
business_id
branch_id
payroll_period_id
employee_id
salary_configuration_id
base_amount
percentage_amount
shift_amount
daily_amount
bonus_amount
deduction_amount
gross_amount
net_amount
calculation_snapshot
status
finalized_at
finalized_by
created_at
updated_at
```

---

## 79. Suggested `payroll_bonuses` Fields

```text id="x3m8v5"
id
business_id
branch_id
payroll_id
employee_id
type
amount
reason
created_by
created_at
```

---

## 80. Suggested `payroll_deductions` Fields

```text id="q6n2m8"
id
business_id
branch_id
payroll_id
employee_id
type
amount
reason
created_by
created_at
```

---

## 81. Suggested `payroll_corrections` Fields

```text id="v4p7x2"
id
business_id
branch_id
payroll_id
actor_id
device_id
previous_state
new_state
reason
authorization_id
created_at
```

---

## 82. Transaction Boundaries

### Record Attendance

```text id="m8q3v5"
Validate Employee
Validate Branch Assignment
Validate Device
Validate Permission
Validate Open Work Session
Create Attendance/Work Session
Commit
```

### Correct Attendance

```text id="x2v7n4"
Validate Permission
Load Original Attendance
Create Correction
Commit
```

### Calculate Payroll

```text id="q5m8p2"
Load Payroll Period
Load Salary Configuration Version
Load Attendance Inputs
Load Eligible Sales Inputs
Load Bonuses/Deductions
Calculate
Persist Calculation Snapshot
Commit
```

### Finalize Payroll

```text id="n3m7x8"
Validate Payroll
Validate Authorization
Lock Final Calculation
Finalize Payroll
Commit
```

---

## 83. Failure Handling

If attendance creation fails:

```text id="v8q2m5"
No partial Work Session
```

If payroll calculation fails:

```text id="m4x7p3"
No partially finalized Payroll
```

If finalization fails before commit:

```text id="q7n2v8"
Payroll remains CALCULATED
```

If network response is lost:

```text id="p3m8x5"
Retry using Attendance/Payroll UUID
```

Idempotency must prevent duplicates.

---

## 84. Performance

Attendance and payroll operations must not slow POS operations.

Therefore:

* attendance writes should be short;
* payroll calculations should run outside POS-critical transactions;
* heavy payroll reports should use background processing;
* salary configuration lookup should be indexed;
* historical payroll queries should be paginated;
* payroll calculation must not lock Orders or Cash Sessions unnecessarily.

---

## 85. Security

Attendance and Payroll require:

```text id="x5m8q2"
Authentication
+
Employee Status
+
Branch Scope
+
Permission
+
Device Trust where applicable
+
Subscription Entitlement
```

Salary information is sensitive business data and must be permission-controlled.

Employees must not automatically have access to other employees' salaries.

---

## 86. Payroll Access

Access to payroll should be determined by:

* employee identity;
* role permissions;
* Branch scope;
* subscription entitlement.

Owner and explicitly authorized employees may access payroll.

A Manager can access payroll only if the required permission is granted.

---

## 87. Database Invariants

The following invariants are mandatory:

1. Every Attendance record has a permanent UUID.
2. Attendance UUIDs are globally unique.
3. Attendance UUIDs are never reused.
4. Attendance belongs to one Business.
5. Attendance belongs to one Branch.
6. Attendance Employee belongs to the same Business.
7. Attendance Employee has valid Branch scope unless explicitly corrected by authorized administration.
8. Attendance Device belongs to the correct Business where applicable.
9. Attendance timestamps are timezone-aware.
10. Attendance source is preserved.
11. Offline Attendance requires trusted authorization.
12. Repeated Attendance synchronization is idempotent.
13. Inactive employees cannot create new normal attendance.
14. Attendance corrections preserve original values.
15. Attendance corrections require authorization.
16. Attendance corrections require a reason.
17. Attendance corrections remain auditable.
18. Multiple active Work Sessions for the same Employee/Branch are normally forbidden.
19. Work Session UUIDs are permanent.
20. Work Session closing preserves original start time.
21. Employee role changes do not silently rewrite historical attendance.
22. Salary Configuration is separate from Payroll Record.
23. Salary Configuration has a permanent UUID.
24. Salary Configuration changes create new versions.
25. Previous Salary Configuration versions remain historically available.
26. Salary Configuration belongs to the correct Business.
27. Branch-specific Salary Configuration belongs to the correct Branch.
28. Salary Configuration Employee belongs to the same Business.
29. Salary Configuration effective dates are valid.
30. Salary amounts cannot be negative.
31. Shift rates cannot be negative.
32. Daily rates cannot be negative.
33. Percentage rates cannot be negative.
34. Percentage rates use exact decimal representation.
35. Payroll Period has a valid start date.
36. Payroll Period end date cannot precede start date.
37. Payroll Period belongs to one Business.
38. Branch Payroll Period belongs to one Branch.
39. Payroll Period status is controlled.
40. Payroll Record belongs to one Payroll Period.
41. Payroll Record belongs to one Employee.
42. Payroll Record Employee belongs to the same Business.
43. One active Payroll Record exists per Employee/Payroll Period by default.
44. Payroll calculation is idempotent.
45. Payroll calculation preserves its input snapshot.
46. Payroll calculation preserves Salary Configuration version.
47. Payroll calculation preserves relevant attendance inputs.
48. Percentage Payroll preserves its calculation base.
49. Bonus records are separately identifiable.
50. Bonus amounts cannot be negative.
51. Bonus creation requires authorization.
52. Deduction records are separately identifiable.
53. Deduction amounts cannot be negative.
54. Deduction creation requires authorization.
55. Gross payroll is reconstructable from its components.
56. Net payroll is reconstructable.
57. Net payroll cannot normally be negative.
58. Payroll finalization requires authorization.
59. Finalized Payroll is immutable.
60. Finalized Payroll cannot be silently recalculated.
61. Finalized Payroll corrections create separate records.
62. Payroll corrections require authorization.
63. Payroll corrections require a reason.
64. Payroll correction history remains available.
65. Historical payroll does not depend on current salary configuration.
66. Historical payroll does not depend on current employee role.
67. Employee deactivation does not delete payroll.
68. Employee deactivation does not delete attendance.
69. Branch deactivation does not delete historical payroll.
70. Subscription downgrade does not delete historical payroll.
71. Subscription downgrade does not delete historical attendance.
72. Payroll access is permission-controlled.
73. Salary data is Business isolated.
74. Salary data is Branch isolated where applicable.
75. Offline attendance cannot bypass authorization.
76. Offline attendance cannot reactivate an inactive Employee.
77. Offline attendance conflicts are explicit.
78. Payroll finalization is concurrency-safe.
79. Stale Payroll updates are rejected.
80. Duplicate Payroll finalization cannot create duplicate final records.
81. Payroll calculations do not block normal POS operations unnecessarily.
82. Attendance writes do not block normal POS operations unnecessarily.
83. Payroll reports use authoritative Payroll records.
84. Notification failure does not roll back Payroll.
85. Audit failure handling must not silently remove financial history.
86. Salary Configuration changes are auditable.
87. Attendance corrections are auditable.
88. Payroll finalization is auditable.
89. Payroll correction is auditable.
90. Payroll UUIDs are permanent.
91. Deleted Business payroll data cannot be accessed through stale clients.
92. Deleted UUIDs are never reused.
93. Historical payroll remains reconstructable.
94. Historical attendance remains reconstructable.
95. Salary calculations use exact monetary types.
96. Payroll percentage calculations use exact decimal types.
97. Database constraints and application validation enforce the same ownership boundaries.
98. Cache is not authoritative for finalized Payroll.
99. Original attendance and payroll events remain historically available.
100. The complete Employee Attendance and Payroll history must always be reconstructable from authoritative records.

---

## 88. Related Documents

### Database

* `02_Database_Architecture.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`
* `21_Report_and_Report_Version_Data_Model.md`
* `22_Offline_and_Synchronization_Data_Model.md`
* `24_Data_Lifecycle_and_Deletion_Data_Model.md`

### Domain

* `03_Identity_and_Access_Domain.md`
* `12_Employee_and_Payroll_Domain.md`
* `15_Audit_Domain.md`
* `16_Synchronization_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `05_Employees_Roles_and_Permissions.md`
* `19_Attendance_and_Payroll.md`
* `22_Audit_and_History.md`
* `23_Offline_Operation.md`
* `24_Synchronization_and_Conflict_Resolution.md`
* `25_Subscription_and_Entitlement.md`
* `27_System_Wide_Consistency_and_Concurrency.md`
* `29_Error_Handling_and_Failure_Recovery.md`

### Architecture

* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 89. Final Rule

The Employee Attendance and Payroll Data Model must preserve both operational attendance history and finalized compensation history.

The central rule is:

```text id="k7m3q8"
Attendance records what happened.
Salary Configuration defines how compensation is calculated.
Payroll Snapshot records what was calculated.
Finalized Payroll is immutable.
Corrections are separate.
Historical salary and attendance data must remain reconstructable.
```

The model must remain compatible with Identity, Branch, Permission, Device Trust, Subscription, Order, Reporting, Audit, Offline Synchronization, and Data Lifecycle domains.

