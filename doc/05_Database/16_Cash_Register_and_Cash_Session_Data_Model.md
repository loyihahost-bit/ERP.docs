# Cash Register and Cash Session Data Model

**Document ID:** DB-16
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Cash Registers;
* Cash Sessions;
* cashier session ownership;
* opening and closing cash;
* expected cash;
* actual cash;
* cash discrepancies;
* cash payments;
* cash refunds;
* cash corrections;
* session reports;
* session lifecycle;
* cashier handover boundaries;
* offline sessions;
* synchronization;
* historical financial integrity.

The model must support fast POS operation while preserving an auditable financial history.

---

## 2. Design Principles

The Cash Register model follows these principles:

1. A Branch normally has one primary Cash Register.
2. The architecture must not prevent future multiple registers.
3. A Cash Register belongs to exactly one Branch.
4. A Cash Session belongs to exactly one Cash Register.
5. A Cash Session belongs to one cashier at opening.
6. A Cash Session has a permanent UUID.
7. A closed Cash Session never becomes an active session again.
8. Corrections are separate from reopening.
9. Cashier handover creates a new Cash Session.
10. Open Orders survive cashier handover.
11. Cash counting is performed at session close/handover.
12. Expected cash is hidden until actual cash is entered.
13. Difference is calculated from expected and actual cash.
14. Shortage and overage remain historically recorded.
15. Cash Session history is immutable after closure except through controlled corrections.
16. Cash Payments are linked to the relevant Cash Session.
17. Cash refunds affect the relevant Cash Session.
18. Card and Debt values do not represent physical cash.
19. Offline sessions are allowed only for trusted authorized devices.
20. Synchronization is UUID-based and idempotent.
21. Session state changes must be concurrency-safe.
22. Session reports must remain historically reconstructable.

---

## 3. Cash Register Ownership

A Cash Register belongs to one Branch.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Session
```

A Cash Register must never belong to a different Business than its Branch.

---

## 4. Primary Cash Register

The current operational model assumes:

```text
1 Branch
    ↓
1 Primary Cash Register
```

This is a business rule, not a limitation of the database architecture.

The schema should allow future multiple registers without requiring a fundamental redesign.

---

## 5. Cash Register Identity

Every Cash Register has a permanent UUID.

Suggested fields:

```text
id
business_id
branch_id
code
name
status
created_at
updated_at
```

The UUID is never reused.

---

## 6. Cash Register Status

Suggested states:

```text
ACTIVE
INACTIVE
ARCHIVED
```

An inactive or archived Cash Register must not accept new Cash Sessions.

Historical Sessions remain available.

---

## 7. Cash Register Code

The Cash Register code should be unique within the Branch.

Example:

```text
BR01-CASH-01
```

The code is an operational identifier.

The UUID remains the authoritative database identity.

---

## 8. Cash Register Branch Integrity

The database must enforce:

```text
cash_register.business_id
=
branch.business_id
```

A Cash Register cannot be assigned to a different Business.

---

## 9. Cash Session Identity

Every Cash Session has a permanent UUID:

```text
cash_session.id
```

The UUID:

* is globally unique;
* may be generated offline;
* remains unchanged after synchronization;
* is used for idempotency;
* is never reused.

---

## 10. Cash Session Context

Suggested fields:

```text
id
business_id
branch_id
cash_register_id
cashier_employee_id
opening_device_id
closing_device_id
status
opened_at
closed_at
created_at
updated_at
```

Additional fields may store opening/closing metadata.

---

## 11. Cash Session Lifecycle

The core lifecycle is:

```text
CLOSED
   ↑
OPEN
```

For creation:

```text
CREATE
  ↓
OPEN
  ↓
CLOSING
  ↓
CLOSED
```

`CLOSING` may be an implementation state used while the close transaction is executing.

The authoritative business states are:

```text
OPEN
CLOSED
```

---

## 12. One Active Session per Register

At most one Cash Session may be active for a Cash Register.

Database/application protection must prevent:

```text
Register A
 ├── Session 1 OPEN
 └── Session 2 OPEN
```

This is invalid.

---

## 13. One Active Session per Branch

Under the current one-register-per-branch model:

```text
Branch
   ↓
one active Cash Session
```

If multiple registers are introduced later, this invariant becomes:

```text
one active session per Cash Register
```

---

## 14. Session Opening

Opening a Cash Session requires:

* active Cash Register;
* active Branch;
* active Employee;
* valid authentication;
* valid permission;
* trusted device;
* valid subscription entitlement;
* no conflicting active session.

Opening may occur online or offline when the device has valid offline authorization.

---

## 15. Session Opening Attribution

The database must preserve:

* cashier Employee UUID;
* opening Device UUID;
* Cash Register UUID;
* Branch UUID;
* Business UUID;
* opening timestamp.

The original cashier identity must never be lost.

---

## 16. Opening Cash

The initial physical cash amount may be recorded as:

```text
opening_cash_amount
```

The amount must use an exact monetary type.

It cannot be negative.

---

## 17. Opening Cash Integrity

Suggested constraints:

```text
opening_cash_amount >= 0
```

The opening amount becomes part of the session's expected cash calculation.

---

## 18. Cash Session Expected Cash

Expected cash should be derived from the session's authoritative cash movements.

Conceptually:

```text
Expected Cash =
Opening Cash
+ Cash Sales
+ Cash Debt Repayments
+ Other Cash In
- Cash Refunds
- Other Cash Out
± Approved Cash Corrections
```

Card, Debt creation, and non-cash transactions must not be counted as physical cash.

---

## 19. Expected Cash Is Authoritative

The database may store a calculated expected amount for fast reporting.

However, the authoritative source remains the underlying financial transactions.

A stored summary must not silently diverge from Payment/Cash records.

---

## 20. Actual Cash

At session close, the cashier physically counts cash.

The actual amount is recorded as:

```text
actual_cash_amount
```

It must use an exact monetary type and cannot be negative.

---

## 21. Hidden Expected Amount

Before the cashier submits the physical count, the UI should not expose the expected cash amount if the business process requires blind counting.

The database itself may calculate/store expected cash.

This is an application/UI behavior rather than a database secrecy mechanism.

---

## 22. Cash Difference

After actual cash is entered:

```text
Difference =
Actual Cash
-
Expected Cash
```

Therefore:

```text
Difference > 0 → Overage
Difference < 0 → Shortage
Difference = 0 → Balanced
```

The calculated result must be persisted for historical reporting.

---

## 23. Difference Snapshot

At session closure, the database should preserve:

```text
expected_cash_amount
actual_cash_amount
cash_difference_amount
```

These values form the historical close snapshot.

---

## 24. Session Closing

Closing requires:

* active Cash Session;
* authorized cashier or authorized employee;
* physical cash count;
* valid device/authentication;
* close operation;
* optional comment.

The close operation must be atomic.

---

## 25. Closing Comment

The cashier may provide a closing comment.

Example:

```text
"Small shortage caused by incorrect change."
```

The comment is historical session data.

It must not be overwritten silently.

---

## 26. Closing Notification

A significant discrepancy or configured close condition may generate a notification to:

* Owner;
* authorized Manager.

Notification failure must not roll back the closed Cash Session.

---

## 27. Cash Shortage

A shortage occurs when:

```text
actual_cash_amount
<
expected_cash_amount
```

The shortage amount is preserved.

The system must not automatically rewrite the session to eliminate the discrepancy.

---

## 28. Cash Overage

An overage occurs when:

```text
actual_cash_amount
>
expected_cash_amount
```

The overage is preserved as a historical discrepancy.

It must not silently increase sales revenue.

---

## 29. Balanced Session

A balanced session has:

```text
actual_cash_amount
=
expected_cash_amount
```

The difference is zero.

The session remains historically recorded as closed.

---

## 30. Cash Session Closure Immutability

Once closed:

* the session does not reopen;
* original expected cash remains preserved;
* original actual cash remains preserved;
* original difference remains preserved;
* original cashier remains preserved.

Any correction is represented separately.

---

## 31. Correction vs Reopen

The system must distinguish:

```text
Session Reopen
```

from:

```text
Correction Opportunity
```

The current system does not reopen a closed Cash Session.

An authorized correction creates a separate correction record.

---

## 32. Session Correction Limit

The current business rule allows:

```text
Maximum normal corrections = 3
```

After three corrections, one additional correction requires explicit privileged authorization.

That authorization is consumed when used.

---

## 33. Correction Authorization

Authorized correction may be performed by:

* Owner;
* authorized Manager;
* another employee with the required permission.

The authorization must be auditable.

---

## 34. Cash Correction Record

Suggested fields:

```text
id
business_id
branch_id
cash_register_id
cash_session_id
actor_id
device_id
correction_type
amount
previous_state
new_state
reason
authorization_id
created_at
```

The original Session values remain historical.

---

## 35. Correction Types

Possible correction types include:

```text
CASH_IN
CASH_OUT
EXPECTED_ADJUSTMENT
OTHER
```

The exact set may be configured through the Cash domain rules.

---

## 36. Cash Transaction Relationship

Cash movements should have explicit transaction records.

Conceptually:

```text
Cash Session
   ↓
Cash Transaction
```

This prevents the session itself from becoming an unstructured ledger.

---

## 37. Suggested `cash_transactions`

Suggested fields:

```text
id
business_id
branch_id
cash_register_id
cash_session_id
transaction_type
payment_id
refund_id
employee_id
device_id
amount
direction
reason
created_at
```

Transaction UUID is permanent.

---

## 38. Cash Transaction Types

Suggested types:

```text
OPENING_BALANCE
CASH_SALE
DEBT_REPAYMENT
CASH_REFUND
CASH_IN
CASH_OUT
CORRECTION_IN
CORRECTION_OUT
CLOSING_ADJUSTMENT
```

The exact operational list may evolve without changing the core identity model.

---

## 39. Cash Transaction Direction

A Cash Transaction may use:

```text
IN
OUT
```

The amount itself remains positive.

This avoids ambiguity around negative monetary values.

---

## 40. Cash Transaction Amount

For a normal transaction:

```text
amount > 0
```

The direction determines whether physical cash increases or decreases.

---

## 41. Cash Sale Relationship

Every Cash Payment must reference the relevant Cash Session.

Conceptually:

```text
Order
 ↓
Payment
 ↓
Cash Transaction
 ↓
Cash Session
```

The Payment remains the financial event.

The Cash Transaction represents its physical cash effect.

---

## 42. Cash Debt Repayment

A Cash Debt Repayment creates a physical cash inflow.

Therefore it creates or references a Cash Transaction:

```text
DEBT_REPAYMENT
IN
```

The original Debt creation does not create this transaction.

---

## 43. Cash Refund

A Cash Refund creates:

```text
CASH_REFUND
OUT
```

It must reference the relevant Refund/Payment context.

---

## 44. Card Payment

Card Payment must not create a physical cash transaction.

It contributes to:

* payment reports;
* card totals;
* financial reports;

but not physical Cash Session balance.

---

## 45. Debt Creation

Debt creation does not create physical cash.

The Debt becomes an outstanding financial obligation.

---

## 46. Mixed Payment

For a Mixed Payment:

```text
Cash portion
    ↓
Cash Session

Card portion
    ↓
Card financial state
```

Only the Cash portion affects expected physical cash.

---

## 47. Cash Session and Orders

A Cash Session may be associated with many Orders.

Order UUIDs remain unchanged during cashier changes.

The Session records which cashier/session performed the financial operation.

---

## 48. Open Orders at Session Close

A cashier may have open Orders when closing a session.

The system must not require all Orders to be paid or served merely to close the Cash Session.

Open Orders continue operationally.

Their later operations may occur under a new Cash Session.

---

## 49. Cashier Handover

Cashier handover follows:

```text
Previous Cashier
      ↓
Close Previous Session
      ↓
Physical Cash Count
      ↓
New Cashier Authentication
      ↓
Cash Acceptance
      ↓
Open New Session
```

The same physical Cash Register remains in use.

---

## 50. Handover Session Identity

Handover creates a new Cash Session UUID.

Example:

```text
Register: R1

Session A → Cashier A
Session B → Cashier B
```

The physical register remains the same.

The Session UUIDs remain different.

---

## 51. Handover and Orders

Open Orders are not recreated.

Their UUIDs remain unchanged.

Later payments or modifications are attributed to the new cashier and new Cash Session where applicable.

---

## 52. Handover and Existing Cash

The incoming cashier confirms the physical cash received from the previous session.

The system must preserve the previous session's actual closing amount and the new session's opening amount separately.

---

## 53. Handover Discrepancy

A shortage or overage belongs to the session where it was identified.

The original shortage remains attributed to the previous cashier/session.

A new cashier cannot silently inherit or erase the historical discrepancy.

---

## 54. New Session Opening Cash

The new Cash Session may use the accepted physical cash as its opening cash.

The exact opening amount must be recorded independently.

---

## 55. Logout Without Closing

Logging out does not automatically close a Cash Session.

The session remains:

```text
OPEN
```

until an authorized close operation occurs.

---

## 56. Force Close

Owner or another authorized employee may force-close a session when necessary.

Force close must record:

* actor;
* reason;
* timestamp;
* device;
* original cashier;
* final session state.

Force close does not erase the original cashier attribution.

---

## 57. Concurrent Session Opening

Two devices attempting to open a session for the same active Register must be serialized.

Example:

```text
Device A → OPEN
Device B → OPEN
```

Only one may succeed.

The other receives a safe rejection.

---

## 58. Concurrent Session Closing

Only one close operation may successfully transition an active Session to Closed.

Repeated requests using the same Session UUID must be idempotent.

A stale close request must not overwrite the already closed Session.

---

## 59. Payment and Session Close Concurrency

The system must prevent inconsistent state when:

* Payment is being created;
* Session is being closed.

A payment must either:

1. become part of the session before close; or
2. be rejected/deferred according to the transaction boundary.

It must never disappear from both states.

---

## 60. Offline Cash Session

Trusted devices with valid offline authorization may:

* open a Cash Session;
* accept Cash Payments;
* record Cash Transactions;
* close a Session;
* perform authorized handover operations.

All operations remain subject to offline authorization and synchronization validation.

---

## 61. Offline Session UUID

The Cash Session UUID is generated locally when necessary.

When synchronized:

* the same UUID is used;
* duplicate creation is rejected;
* server validation determines authoritative state.

---

## 62. Offline Cash Conflict

Examples:

* another device already opened a session;
* employee became inactive;
* device was revoked;
* subscription expired;
* session was already closed elsewhere.

These conditions create explicit synchronization conflicts or safe rejection.

---

## 63. Cash Session Sync Ordering

Cash Session synchronization must respect dependencies.

Conceptually:

```text
Business
  ↓
Branch
  ↓
Cash Register
  ↓
Cash Session
  ↓
Cash Transactions
  ↓
Payments / Refunds
```

The exact sync dependency graph may vary by event type.

---

## 64. Cash Transaction Idempotency

Every Cash Transaction must have a permanent UUID.

Repeated synchronization of the same transaction must not duplicate physical cash effects.

---

## 65. Cash Session Versioning

A Session may contain an optimistic concurrency version.

Suggested field:

```text
version
```

The version changes whenever mutable operational Session state changes before closure.

Stale updates must be rejected.

---

## 66. Session Close Snapshot

At closure, the system should preserve a close snapshot containing:

```text
opening_cash_amount
expected_cash_amount
actual_cash_amount
cash_difference_amount
cash_payment_total
cash_refund_total
cash_debt_repayment_total
cash_correction_total
order_count
payment_count
closing_comment
```

This supports fast historical reporting.

---

## 67. Session Report

A closed Cash Session should have a report containing at least:

* Session UUID;
* Branch;
* Cash Register;
* cashier;
* opening cash;
* expected cash;
* actual cash;
* difference;
* Cash Sales;
* Cash Refunds;
* Debt Repayments;
* corrections;
* order count;
* payment count;
* opening/closing timestamps;
* status.

---

## 68. Session Report Immutability

The historical Session report must not silently change after closure.

If a correction changes report-relevant data, a new report version may be generated according to the Report domain rules.

---

## 69. Cashier Report

Cashier reporting must support:

* cashier identity;
* sessions;
* cash sales;
* refunds;
* debt repayments;
* shortages;
* overages;
* corrections.

Historical attribution must remain intact.

---

## 70. Monthly Reporting Relationship

Monthly financial reports may aggregate Cash Sessions.

The report must reference the relevant Session UUIDs.

The report itself is versioned independently.

---

## 71. Suggested `cash_registers` Fields

```text
id
business_id
branch_id
code
name
status
created_at
updated_at
```

Recommended constraints:

```text
UNIQUE(branch_id, code)
```

---

## 72. Suggested `cash_sessions` Fields

```text
id
business_id
branch_id
cash_register_id
cashier_employee_id
opening_device_id
closing_device_id
status
opening_cash_amount
expected_cash_amount
actual_cash_amount
cash_difference_amount
closing_comment
opened_at
closed_at
version
created_at
updated_at
```

---

## 73. Suggested `cash_transactions` Fields

```text
id
business_id
branch_id
cash_register_id
cash_session_id
transaction_type
direction
payment_id
refund_id
employee_id
device_id
amount
reason
created_at
```

---

## 74. Suggested `cash_corrections` Fields

```text
id
business_id
branch_id
cash_register_id
cash_session_id
actor_id
device_id
correction_type
amount
previous_state
new_state
reason
authorization_id
created_at
```

---

## 75. Cash Register Foreign Keys

Important relationships:

```text
cash_register.business_id → business.id
cash_register.branch_id → branch.id

cash_session.business_id → business.id
cash_session.branch_id → branch.id
cash_session.cash_register_id → cash_register.id
cash_session.cashier_employee_id → employee.id
cash_session.opening_device_id → device.id
cash_session.closing_device_id → device.id
```

---

## 76. Cash Transaction Foreign Keys

Important relationships:

```text
cash_transaction.business_id → business.id
cash_transaction.branch_id → branch.id
cash_transaction.cash_register_id → cash_register.id
cash_transaction.cash_session_id → cash_session.id
cash_transaction.payment_id → payment.id
cash_transaction.refund_id → refund.id
cash_transaction.employee_id → employee.id
cash_transaction.device_id → device.id
```

All nullable relationships must be valid for the relevant transaction type.

---

## 77. Monetary Data Types

All cash amounts must use exact monetary types.

Floating-point types must not be used for:

* opening cash;
* expected cash;
* actual cash;
* differences;
* cash transactions;
* corrections.

---

## 78. Branch and Business Isolation

Every Cash Register and Cash Session must be Business and Branch scoped.

A client must never be able to select a Cash Register from another Branch merely by supplying its UUID.

---

## 79. Authorization Boundary

Cash Session access requires:

```text
Authentication
+
Employee Status
+
Branch Scope
+
Permission
+
Device Trust
+
Subscription Entitlement
```

Device trust alone does not authorize Cash operations.

---

## 80. Audit Requirements

Important events must create Audit records:

* Cash Register created;
* Cash Register activated/deactivated;
* Session opened;
* Session closed;
* Force close;
* Handover;
* Cash correction;
* discrepancy resolution;
* authorization;
* offline conflict resolution.

Routine reads do not require audit events unless otherwise classified as sensitive.

---

## 81. Notification Requirements

Notifications may be generated for:

* significant shortage;
* significant overage;
* force close;
* repeated correction;
* correction limit reached;
* abnormal session state.

Notification failure must never roll back the Cash transaction.

---

## 82. Cache Requirements

Current session summaries may be cached for POS performance.

Cache is not authoritative.

Financial calculations must ultimately use authoritative database records.

---

## 83. Indexing Strategy

Recommended indexes:

```text
cash_registers(branch_id, status)
cash_registers(business_id, branch_id)

cash_sessions(branch_id, status)
cash_sessions(cash_register_id, status)
cash_sessions(cashier_employee_id, opened_at)
cash_sessions(business_id, opened_at)
cash_sessions(business_id, closed_at)

cash_transactions(cash_session_id, created_at)
cash_transactions(payment_id)
cash_transactions(refund_id)
cash_transactions(employee_id, created_at)

cash_corrections(cash_session_id, created_at)
```

A partial unique index should enforce one active Session per Cash Register.

---

## 84. Data Lifecycle

When a Business expires:

* existing Cash Sessions remain readable;
* historical reports remain readable;
* new modifying Cash operations may be blocked.

When a Business is deleted:

* Cash Registers;
* Cash Sessions;
* Cash Transactions;
* Cash Corrections

are removed according to the controlled dependency-aware deletion process.

---

## 85. Historical Integrity

The following values must remain reconstructable:

* Register UUID;
* Session UUID;
* Branch;
* cashier;
* opening cash;
* expected cash;
* actual cash;
* difference;
* cash transactions;
* corrections;
* handover;
* force close;
* device attribution;
* timestamps.

Historical session state must not depend on current configuration.

---

## 86. Failure Handling

If Session opening fails:

```text
No partial OPEN Session
```

If Session closing fails:

```text
Session remains OPEN
```

unless the transaction has already committed the Closed state.

If the database response is lost after successful close:

```text
Retry using the same Session UUID
```

The operation must remain idempotent.

---

## 87. Recovery

Recovery mechanisms must support:

* interrupted close;
* interrupted open;
* lost synchronization response;
* offline Session synchronization;
* device replacement;
* employee deactivation;
* forced administrative close.

Recovery must never create a second financial reality.

---

## 88. Performance

Cash Session operations are POS-critical.

Therefore:

* close transactions must remain short;
* session lookup must be indexed;
* active-session validation must be efficient;
* historical reporting must not lock POS tables for long periods;
* heavy reports must run outside the critical payment path.

---

## 89. Core Transaction Boundaries

### Open Session

```text
Validate Register
Validate Branch
Validate Employee
Validate Permission
Validate Device
Validate Subscription
Verify No Active Session
Create Session
Create Opening Transaction
Commit
```

### Close Session

```text
Validate Active Session
Validate Actor
Record Actual Cash
Calculate Difference
Persist Close Snapshot
Close Session
Commit
```

### Cash Payment

```text
Validate Payment
Validate Session
Create Payment
Create Cash Transaction
Commit
```

### Cash Refund

```text
Validate Refund
Validate Session
Create Refund
Create Cash-Out Transaction
Commit
```

---

## 90. Database Invariants

The following invariants are mandatory:

1. Every Cash Register belongs to exactly one Branch.
2. Every Cash Register belongs to exactly one Business.
3. Cash Register Business must match Branch Business.
4. Cash Register UUID is globally unique.
5. Cash Register UUID is never reused.
6. Cash Register code is unique within the Branch.
7. Archived Cash Registers cannot open new Sessions.
8. Every Cash Session belongs to one Cash Register.
9. Cash Session Branch must match Cash Register Branch.
10. Cash Session Business must match Cash Register Business.
11. Cash Session UUID is globally unique.
12. Cash Session UUID is never reused.
13. At most one active Session exists per Register.
14. Under the current model, at most one active Session exists per Branch.
15. A Session has one opening cashier.
16. Opening cashier must belong to the correct Business.
17. Opening cashier must have required Branch scope.
18. Opening requires valid authorization.
19. Opening requires trusted device authorization.
20. Opening requires valid subscription entitlement.
21. Opening cash cannot be negative.
22. Actual cash cannot be negative.
23. Expected cash is based on authoritative cash movements.
24. Card Payments do not increase physical cash.
25. Debt creation does not increase physical cash.
26. Cash Debt Repayment increases physical cash.
27. Cash Refund decreases physical cash.
28. Cash Sale increases physical cash.
29. Mixed Payment only contributes its Cash portion to physical cash.
30. Cash Transaction amount is positive.
31. Cash Transaction direction is explicit.
32. Every Cash Transaction belongs to one Cash Session.
33. Cash Transaction UUID is globally unique.
34. Repeated Cash Transaction synchronization is idempotent.
35. Cash Session close records expected cash.
36. Cash Session close records actual cash.
37. Cash Session close records difference.
38. Difference equals actual minus expected.
39. Positive difference represents overage.
40. Negative difference represents shortage.
41. Zero difference represents balanced state.
42. Closed Sessions cannot become OPEN again.
43. Closed Sessions retain original cashier.
44. Closed Sessions retain original closing values.
45. Closed Sessions retain original timestamps.
46. Corrections do not overwrite original close values.
47. Corrections require authorization.
48. Corrections require a reason.
49. Corrections are separately recorded.
50. Normal corrections are limited to three.
51. Additional correction requires privileged authorization.
52. Privileged authorization is consumed when used.
53. Correction history remains auditable.
54. Logout does not automatically close a Session.
55. Force close requires authorization.
56. Force close requires a reason.
57. Force close preserves original Session history.
58. Cashier handover creates a new Session UUID.
59. Handover does not change the physical Register UUID.
60. Handover does not recreate existing Orders.
61. Open Orders survive Session handover.
62. Later operations may belong to the new Session.
63. Previous Session discrepancy remains attributed to previous Session.
64. New Session opening cash is independently recorded.
65. Concurrent Session opening is serialized.
66. Concurrent Session closing is serialized.
67. Repeated close requests are idempotent.
68. Stale close requests cannot overwrite current state.
69. Payment and Session close concurrency cannot lose a financial transaction.
70. Offline Session creation requires trusted authorization.
71. Offline Session UUID remains unchanged after synchronization.
72. Offline Session synchronization is idempotent.
73. Revoked devices cannot continue authorized offline operation beyond allowed rules.
74. Inactive employees cannot create new Sessions.
75. Business isolation is mandatory.
76. Branch isolation is mandatory.
77. Register isolation is mandatory.
78. Device trust does not replace permission checks.
79. Subscription entitlement does not replace authorization.
80. Financial calculations cannot rely solely on cache.
81. Historical Sessions remain readable after subscription expiry.
82. Historical Sessions remain reconstructable after configuration changes.
83. Historical Sessions retain Device attribution.
84. Historical Sessions retain cashier attribution.
85. Historical Sessions retain Branch attribution.
86. Cash corrections retain actor attribution.
87. Cash corrections retain timestamp.
88. Cash reports reference authoritative Session records.
89. Report generation failure cannot roll back a closed Session.
90. Notification failure cannot roll back a closed Session.
91. Session close failure before commit leaves the Session OPEN.
92. Lost database responses can be safely retried using UUID identity.
93. Deleted Business Sessions cannot be accessed through stale clients.
94. Deleted Cash Session UUIDs are never reused.
95. Heavy reporting cannot block normal Cash Session operations unnecessarily.
96. Database constraints and application validation must enforce the same ownership boundaries.
97. Expected cash must not be silently changed after closure.
98. Actual cash must not be silently changed after closure.
99. Original discrepancies remain historically visible.
100. Cash Session history must always be reconstructable from authoritative records.

---

## 91. Related Documents

### Database

* `02_Database_Architecture.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `17_Shift_Handover_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`
* `21_Report_and_Report_Version_Data_Model.md`
* `22_Offline_and_Synchronization_Data_Model.md`

### Domain

* `07_Cash_Domain.md`
* `09_Payment_Domain.md`
* `15_Audit_Domain.md`
* `16_Synchronization_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `14_Cash_Register_and_Cash_Session.md`
* `15_Shift_Handover.md`
* `23_Offline_Operation.md`
* `24_Synchronization_and_Conflict_Resolution.md`
* `27_System_Wide_Consistency_and_Concurrency.md`
* `28_Background_Jobs_and_Recovery.md`
* `29_Error_Handling_and_Failure_Recovery.md`

### Architecture

* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 92. Final Rule

The Cash Register and Cash Session model must preserve the complete physical-cash history of each Branch while keeping POS operations fast.

The central rule is:

```text
Register identifies the physical cash point.
Session identifies one cashier operating period.
Cash Transactions identify physical cash movement.
Closing creates an immutable historical snapshot.
Handover creates a new Session.
Corrections never rewrite the original Session.
```

The model must remain compatible with offline operation, synchronization, payment processing, reporting, audit, and future multi-register expansion.

