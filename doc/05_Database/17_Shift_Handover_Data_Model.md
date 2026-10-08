# Shift Handover Data Model

**Document ID:** DB-17
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for cashier shift handover between Cash Sessions.

The model covers:

* outgoing cashier;
* incoming cashier;
* previous and new Cash Sessions;
* physical cash handover;
* cash counting;
* handover acceptance;
* discrepancies;
* open Orders;
* payment attribution;
* offline handover;
* synchronization;
* authorization;
* audit;
* correction;
* historical integrity.

The handover process must preserve the original financial responsibility of the outgoing cashier while allowing the incoming cashier to continue operating on the same physical Cash Register.

---

## 2. Design Principles

The Shift Handover model follows these principles:

1. Handover occurs between two Cash Sessions.
2. The outgoing Session is closed before the incoming Session becomes active.
3. The physical Cash Register remains the same.
4. The outgoing Session UUID is never reused.
5. The incoming Session receives a new UUID.
6. Open Orders are not recreated.
7. Open Orders retain their original UUIDs.
8. The outgoing cashier remains responsible for the outgoing Session history.
9. The incoming cashier becomes responsible for the new Session.
10. Physical cash is counted during handover.
11. Expected cash is hidden until the actual cash count is entered where the business workflow requires blind counting.
12. The original shortage/overage remains immutable.
13. A discrepancy is not silently transferred to the incoming cashier.
14. Corrections are separate from Session reopening.
15. Handover requires appropriate authentication and authorization.
16. Trusted devices are required for offline handover.
17. Synchronization uses UUID-based idempotency.
18. Handover state transitions are concurrency-safe.
19. All important handover actions are auditable.
20. Handover must not interrupt normal POS operation more than necessary.

---

## 3. Handover Concept

Conceptually:

```text
Outgoing Cashier
      ↓
Outgoing Cash Session
      ↓
Physical Cash Count
      ↓
Handover
      ↓
Incoming Cashier
      ↓
New Cash Session
```

The physical Cash Register remains unchanged.

---

## 4. Handover Identity

Every Shift Handover has its own permanent UUID:

```text id="m9x4q2"
handover.id
```

The UUID:

* is globally unique;
* may be generated offline;
* is immutable;
* is used for synchronization idempotency;
* is never reused.

---

## 5. Handover Context

A Handover belongs to:

* Business;
* Branch;
* Cash Register;
* outgoing Cash Session;
* incoming Cash Session;
* outgoing cashier;
* incoming cashier.

Suggested conceptual relationship:

```text id="p5v8n3"
Business
  ↓
Branch
  ↓
Cash Register
  ↓
Outgoing Session
  ↓
Shift Handover
  ↓
Incoming Session
```

---

## 6. Suggested `shift_handovers` Fields

```text id="r7m2k9"
id
business_id
branch_id
cash_register_id

outgoing_session_id
incoming_session_id

outgoing_employee_id
incoming_employee_id

initiated_by_employee_id
approved_by_employee_id

status

expected_cash_amount
actual_cash_amount
cash_difference_amount

outgoing_comment
incoming_comment

initiated_at
accepted_at
completed_at

device_id
version
created_at
updated_at
```

Some fields may remain nullable until the corresponding stage is reached.

---

## 7. Handover Lifecycle

Recommended lifecycle:

```text id="v3q8m1"
INITIATED
    ↓
COUNTING
    ↓
PENDING_ACCEPTANCE
    ↓
ACCEPTED
    ↓
COMPLETED
```

Exceptional states may include:

```text id="x6n4p2"
CANCELLED
FAILED
CONFLICT
```

The exact implementation may simplify these states while preserving the same business transitions.

---

## 8. Handover Initiation

The outgoing cashier or authorized employee initiates the handover.

The system validates:

* outgoing Session is OPEN;
* outgoing cashier is active;
* Register is active;
* Branch is active;
* required permission exists;
* device is trusted;
* subscription allows the operation.

---

## 9. Handover Initiator

The initiating employee is preserved separately from:

* outgoing cashier;
* incoming cashier.

This is necessary because an Owner or Manager may initiate or authorize a handover without being the cashier.

---

## 10. Outgoing Cashier

The outgoing cashier is the employee associated with the outgoing Cash Session.

The handover must preserve this identity permanently.

The outgoing cashier cannot be silently replaced in historical data.

---

## 11. Incoming Cashier

The incoming cashier must:

* authenticate;
* be active;
* have valid Branch scope;
* have required POS/Cash permissions;
* have valid subscription entitlement;
* use an authorized device.

The incoming employee becomes the cashier of the new Cash Session.

---

## 12. Same Branch Requirement

The outgoing and incoming Cashiers must operate within the same Branch for a normal handover.

Cross-Branch handover is not supported.

The database must enforce:

```text id="k2m7v4"
outgoing_session.branch_id
=
incoming_session.branch_id
```

---

## 13. Same Register Requirement

The outgoing and incoming Sessions must use the same physical Cash Register.

Therefore:

```text id="q8p3n6"
outgoing_session.cash_register_id
=
incoming_session.cash_register_id
```

A handover is not a Register transfer.

---

## 14. Session Ordering

The outgoing Session must precede the incoming Session.

Conceptually:

```text id="w5x2m8"
Outgoing Session
closed_at
<=
Incoming Session
opened_at
```

The exact timestamps may account for transaction processing latency.

---

## 15. Session Closure Before Acceptance

The incoming cashier cannot become the active cashier for the Register while the outgoing Session remains active.

The transition must ensure:

```text id="h4v7q2"
Outgoing Session → CLOSED
Incoming Session → OPEN
```

without creating an invalid intermediate state.

---

## 16. Physical Cash Count

During handover, the outgoing cashier physically counts the cash.

The actual count is stored as:

```text id="n8m3p5"
actual_cash_amount
```

It must be:

```text id="c7q2v9"
actual_cash_amount >= 0
```

---

## 17. Expected Cash

The system calculates expected cash from authoritative Cash Transactions.

Conceptually:

```text id="f3m8x1"
Expected =
Opening Cash
+ Cash In
- Cash Out
```

The exact calculation follows the Cash Session model.

---

## 18. Blind Cash Count

Where configured by the business workflow:

1. Cashier enters actual physical cash.
2. Expected amount remains hidden until the count is submitted.
3. System calculates the difference.
4. The result is shown after submission.

This prevents the cashier from adjusting the physical count to match the expected value.

---

## 19. Handover Difference

The difference is:

```text id="z5v2m7"
Difference =
Actual Cash
-
Expected Cash
```

Therefore:

```text id="x8q3n6"
Positive → Overage
Negative → Shortage
Zero → Balanced
```

---

## 20. Discrepancy Ownership

The discrepancy belongs to the outgoing Session.

Example:

```text id="m7p4q2"
Expected = 500,000
Actual = 480,000

Shortage = -20,000
```

The shortage remains associated with the outgoing cashier/session.

It must not automatically become the incoming cashier's shortage.

---

## 21. Handover Acceptance

After the outgoing cash count:

1. The incoming cashier verifies the physical cash.
2. The incoming cashier accepts the handover.
3. The new Cash Session is opened.
4. The handover becomes completed.

The incoming cashier's acceptance is separately recorded.

---

## 22. Incoming Acceptance

The incoming cashier may provide an optional comment.

Example:

```text id="c4n8m2"
"Cash counted and accepted."
```

The comment becomes historical handover data.

---

## 23. Handover Completion

A completed handover must contain:

* outgoing Session;
* incoming Session;
* outgoing cashier;
* incoming cashier;
* expected cash;
* actual cash;
* difference;
* acceptance actor;
* timestamps.

---

## 24. Handover and Open Orders

Open Orders must survive the handover.

The system must not:

* duplicate them;
* create replacement Orders;
* change their UUIDs;
* lose their table association.

The existing Orders remain authoritative.

---

## 25. Order Attribution After Handover

An Order keeps its original creation context.

Later operations may belong to the incoming cashier and new Cash Session.

Example:

```text id="p6m3x8"
Order UUID = O1

Created:
Cashier A
Session A

Paid:
Cashier B
Session B
```

Both histories must remain visible.

---

## 26. Payment During Handover

If a Payment is attempted while the handover transition is not yet complete, the system must not silently assign it to the wrong Session.

The Payment may:

* wait in a pending state;
* be rejected temporarily;
* be retried after the new Session becomes active.

The chosen implementation must preserve financial integrity.

---

## 27. Payment After Handover

Once the incoming Session is active:

new Payments performed by the incoming cashier are attributed to:

```text id="w2n7k5"
incoming_session_id
incoming_employee_id
```

The original Order UUID remains unchanged.

---

## 28. Inventory During Handover

Inventory operations continue normally.

A handover does not reset inventory state.

Inventory transactions retain their own:

* employee;
* device;
* branch;
* timestamp;
* transaction UUID.

---

## 29. Order Modification During Handover

An Order modification attempted during the transition must either:

* complete before the outgoing Session closes;
* be performed under the new Session after handover;
* or be safely rejected/retried.

It must never become unattributed.

---

## 30. Session Close and Handover Atomicity

The transition must avoid the invalid state:

```text id="n3q8v1"
Outgoing Session = CLOSED
Incoming Session = not OPEN
Register = unusable
```

or:

```text id="m8x4p2"
Outgoing Session = OPEN
Incoming Session = OPEN
```

The database/application transaction boundary must protect the Register state.

---

## 31. Handover Transaction Boundary

Conceptually:

```text id="q7m2k5"
Validate outgoing Session
Validate incoming Employee
Validate authorization
Record physical count
Calculate difference
Close outgoing Session
Create/open incoming Session
Create Handover record
Commit
```

If the transaction fails before commit, the transition must remain recoverable.

---

## 32. Handover and Session UUIDs

The outgoing and incoming Session UUIDs must remain different.

Example:

```text id="v4p8n2"
Session A = UUID-A
Session B = UUID-B
```

UUID-B must never replace UUID-A.

---

## 33. Handover Version

A handover may use optimistic concurrency:

```text id="r3m7x5"
version
```

The version changes when the handover state changes.

Stale updates must be rejected.

---

## 34. Concurrent Handover

Two devices must not successfully create two handovers from the same active Session.

Example:

```text id="k8q2m4"
Session A

Device 1 → Handover to B
Device 2 → Handover to C
```

Only one transition may succeed.

The second receives a safe rejection or conflict.

---

## 35. Concurrent Incoming Session

The Register must not accept two incoming Sessions.

The following state is invalid:

```text id="p2v7m9"
Register R
 ├── Session B OPEN
 └── Session C OPEN
```

---

## 36. Handover Idempotency

If the client submits the same Handover UUID multiple times:

* no duplicate Handover is created;
* no second incoming Session is created;
* no second cash transfer is recorded.

The original result is returned or the current authoritative state is returned.

---

## 37. Offline Handover

Trusted devices may perform Handover while offline if:

* offline authorization is valid;
* outgoing cashier is authorized;
* incoming cashier is authorized;
* Branch is valid;
* Register is valid;
* Session transition is allowed.

---

## 38. Offline Handover UUID

The Handover UUID may be generated locally.

The same UUID must be used during synchronization.

The server must not create a second Handover for the same UUID.

---

## 39. Offline Handover Conflict

Possible conflicts include:

* outgoing Session already closed;
* another Handover already completed;
* incoming Employee became inactive;
* device revoked;
* subscription expired;
* Register changed state;
* Branch became inactive;
* another Session became active.

Conflicts must be explicit.

---

## 40. Server Authority

After synchronization, the server is authoritative for:

* Session state;
* Handover state;
* employee status;
* permissions;
* Register state;
* subscription;
* final financial records.

Offline local state must not override server state.

---

## 41. Handover Conflict Resolution

A conflict may be resolved only through an authorized operation.

Resolution must preserve:

* original Handover event;
* conflict state;
* resolver;
* reason;
* timestamp;
* resulting state.

No silent overwrite is allowed.

---

## 42. Cash Correction After Handover

If the outgoing Session contains a discrepancy, later correction must reference the outgoing Session.

The incoming Session must not be modified merely to hide the original discrepancy.

---

## 43. Handover Correction

If the Handover itself contains incorrect metadata, correction must be represented separately.

Original Handover data remains available.

Suggested model:

```text id="j5m9q3"
Shift Handover
      ↓
Handover Correction
```

---

## 44. Handover Correction Fields

Suggested fields:

```text id="x3v8m2"
id
handover_id
actor_id
device_id
correction_type
previous_value
new_value
reason
authorization_id
created_at
```

---

## 45. Handover Audit

Important events must create Audit records:

* handover initiated;
* cash count submitted;
* incoming cashier accepted;
* handover completed;
* handover cancelled;
* handover conflict;
* conflict resolution;
* force intervention;
* correction.

---

## 46. Handover Notifications

Notifications may be generated for:

* shortage;
* overage;
* failed handover;
* conflict;
* unauthorized attempt;
* force close;
* correction authorization.

Notification failure must not roll back a successful Handover.

---

## 47. Cash Session Relationship

The Handover should reference both Sessions:

```text id="q8m4v2"
outgoing_session_id
incoming_session_id
```

This creates an explicit transition relationship.

---

## 48. Cash Register Relationship

The Handover references one Cash Register.

Both Sessions must reference that same Register.

This prevents accidental cross-register handovers.

---

## 49. Employee Relationship

The Handover references:

```text id="n5x2p7"
outgoing_employee_id
incoming_employee_id
initiated_by_employee_id
approved_by_employee_id
```

The incoming employee may be the same employee only if the business explicitly allows a self-handover process.

By default, normal handover assumes different cashiers.

---

## 50. Device Relationship

The Handover should preserve the Device that initiated or completed the operation.

If outgoing and incoming cashiers use different trusted devices, both device contexts may be stored through separate event/audit records.

---

## 51. Handover and Cash Transactions

The physical cash transfer itself should be represented by Cash Session opening/closing transactions rather than by modifying the original Payment records.

The Handover links the two Sessions.

This keeps Cash and Handover responsibilities separate.

---

## 52. Opening Balance Relationship

The incoming Session's opening cash may equal the accepted physical cash from the outgoing Session.

Conceptually:

```text id="v7m3q8"
Outgoing actual cash
        ↓
Handover accepted cash
        ↓
Incoming opening cash
```

The two values must remain separately stored.

---

## 53. Handover Amount Integrity

If the business rule requires the incoming opening cash to equal accepted handover cash:

```text id="r2n8p5"
incoming.opening_cash_amount
=
handover.actual_cash_amount
```

Any difference must require explicit correction and reason.

---

## 54. Handover and Shortage

A shortage does not reduce the physical cash amount actually handed over.

Example:

```text id="m6q3v9"
Expected = 500,000
Actual = 480,000

Handover cash = 480,000
Shortage = 20,000
```

The incoming Session receives 480,000 as physical opening cash.

The outgoing Session retains the 20,000 shortage.

---

## 55. Handover and Overage

Example:

```text id="x4v7m2"
Expected = 500,000
Actual = 520,000

Handover cash = 520,000
Overage = 20,000
```

The incoming Session receives the actual physical cash.

The 20,000 overage remains historically attributed to the outgoing Session.

---

## 56. Cash Acceptance

The incoming cashier's acceptance should record:

```text id="p8m2q5"
accepted_by_employee_id
accepted_at
accepted_amount
acceptance_comment
```

Acceptance does not rewrite the outgoing Session's actual count.

---

## 57. Acceptance Rejection

If the incoming cashier refuses to accept the cash:

* the handover does not complete;
* the outgoing Session remains responsible until resolution;
* the reason is recorded;
* an authorized intervention may be required.

The exact operational handling must prevent two active Sessions from existing simultaneously.

---

## 58. Failed Handover

If a Handover fails before completion:

* the outgoing Session remains authoritative;
* no duplicate incoming Session is created;
* no duplicate cash transaction is created;
* the failure may be retried using the same Handover UUID.

---

## 59. Recovery After Application Crash

If the application crashes during handover, the server must determine the committed state.

Possible outcomes:

```text id="y2m7v4"
Handover not committed
OR
Handover committed
```

The system must never invent a third ambiguous financial state.

---

## 60. Recovery After Network Loss

If network connection is lost after submission:

* the client retries using the same Handover UUID;
* server idempotency prevents duplication;
* current authoritative state is returned.

---

## 61. Subscription Expiry

If subscription expires during handover:

* already committed operations remain valid;
* new modifying operations may be blocked according to subscription rules;
* server time is authoritative.

A client must not bypass subscription restrictions using offline handover.

---

## 62. Employee Deactivation

If the incoming employee becomes inactive before handover completion:

```text id="q6v3m8"
Handover cannot complete
```

unless an authorized recovery process assigns another valid employee.

The inactive employee must not become the active cashier.

---

## 63. Device Revocation

If the operating Device is revoked:

* new handover operations from that device are rejected;
* already committed Handover history remains valid;
* offline events from the revoked device are validated during synchronization.

---

## 64. Business/Branch Deactivation

A Handover cannot begin for an inactive Branch.

A deleted Business cannot accept Handover events.

Stale offline events must not resurrect deleted Sessions.

---

## 65. Handover History

The system must preserve:

* outgoing cashier;
* incoming cashier;
* outgoing Session;
* incoming Session;
* Register;
* Branch;
* expected cash;
* actual cash;
* difference;
* comments;
* timestamps;
* device;
* authorization;
* correction history.

---

## 66. Handover Reporting

Reports should support:

* cashier handover history;
* outgoing/incoming cashier;
* Session transition;
* shortage/overage;
* accepted cash;
* rejected handovers;
* force interventions;
* corrections;
* conflicts.

---

## 67. Suggested Indexes

Recommended indexes:

```text id="z5m8q2"
shift_handovers(business_id, branch_id, initiated_at)
shift_handovers(cash_register_id, initiated_at)
shift_handovers(outgoing_session_id)
shift_handovers(incoming_session_id)
shift_handovers(outgoing_employee_id, initiated_at)
shift_handovers(incoming_employee_id, initiated_at)
shift_handovers(status, initiated_at)
shift_handover_corrections(handover_id, created_at)
```

Unique constraints should protect:

* Handover UUID;
* one successful outgoing Session transition;
* one incoming Session per Register transition.

---

## 68. Suggested `shift_handovers` Constraints

Conceptually:

```text id="n7p4x2"
UNIQUE(id)

outgoing_session_id != incoming_session_id

outgoing_employee_id
=
outgoing_session.cashier_employee_id

incoming_employee_id
=
incoming_session.cashier_employee_id

outgoing_session.cash_register_id
=
incoming_session.cash_register_id
```

Business and Branch consistency must also be enforced.

---

## 69. Data Types

Monetary fields must use exact monetary types.

Timestamps must use timezone-aware timestamps.

UUIDs must use the database UUID type where supported.

Boolean flags must not replace lifecycle states when historical state is required.

---

## 70. Historical Immutability

After Handover completion:

* original cash count cannot be silently changed;
* outgoing cashier cannot be replaced;
* incoming cashier cannot be replaced;
* original Sessions cannot be replaced;
* original difference cannot be removed.

Corrections must be additive.

---

## 71. Cache

Current handover status may be cached for UI responsiveness.

Cache is not authoritative.

The authoritative state remains in PostgreSQL.

---

## 72. Transaction Boundaries

### Initiate Handover

```text id="j3m8q5"
Validate Session
Validate Incoming Employee
Validate Permissions
Validate Device
Create Handover
Commit
```

### Complete Handover

```text id="p7v2n4"
Validate Handover
Validate Cash Count
Close Outgoing Session
Create/Activate Incoming Session
Persist Handover Completion
Commit
```

### Resolve Handover Conflict

```text id="x8m3q6"
Validate Authorization
Load Conflict
Apply Resolution
Create Audit Event
Commit
```

---

## 73. Performance

Handover is an operationally important but relatively infrequent transaction.

The implementation should:

* use indexed Session/Register lookup;
* keep transition transactions short;
* avoid large report queries inside the handover transaction;
* avoid synchronous notification processing;
* avoid unnecessary configuration queries;
* preserve normal POS responsiveness.

---

## 74. Security

Handover must enforce:

```text id="m4q8v2"
Authentication
+
Employee Status
+
Branch Scope
+
Cash Permission
+
Device Trust
+
Subscription Entitlement
```

A trusted Device alone cannot authorize handover.

An authenticated Employee without required permission cannot perform it.

---

## 75. Database Invariants

The following invariants are mandatory:

1. Every Handover has a permanent UUID.
2. Handover UUIDs are globally unique.
3. Handover UUIDs are never reused.
4. Every Handover belongs to one Business.
5. Every Handover belongs to one Branch.
6. Outgoing Session belongs to the same Business.
7. Incoming Session belongs to the same Business.
8. Outgoing Session belongs to the same Branch.
9. Incoming Session belongs to the same Branch.
10. Outgoing and incoming Sessions use the same Cash Register.
11. Outgoing and incoming Sessions cannot be the same Session.
12. Outgoing cashier matches outgoing Session cashier.
13. Incoming cashier matches incoming Session cashier.
14. Outgoing cashier must be active when handover starts.
15. Incoming cashier must be active before acceptance.
16. Incoming cashier must have valid Branch scope.
17. Incoming cashier must have required permission.
18. Handover requires valid authentication.
19. Handover requires valid device trust.
20. Handover requires valid subscription entitlement.
21. Cross-Branch handover is forbidden.
22. Cross-Register handover is forbidden.
23. Outgoing Session must precede incoming Session.
24. Outgoing Session must be closed before incoming Session becomes active.
25. Two active Sessions cannot exist for one Register.
26. Two successful handovers cannot transition the same Session simultaneously.
27. Handover actual cash cannot be negative.
28. Handover expected cash cannot be negative.
29. Handover difference equals actual minus expected.
30. Positive difference represents overage.
31. Negative difference represents shortage.
32. Zero difference represents balanced cash.
33. Shortage remains attributed to outgoing Session.
34. Overage remains attributed to outgoing Session.
35. Physical cash handed over equals the recorded actual cash unless explicitly corrected.
36. Incoming opening cash is recorded separately.
37. Incoming opening cash does not rewrite outgoing actual cash.
38. Handover does not change Order UUIDs.
39. Handover does not recreate Orders.
40. Open Orders survive a completed handover.
41. Later Order operations may belong to the incoming Session.
42. Later Payments may belong to the incoming Session.
43. Original Order creation attribution remains historical.
44. Payment during transition cannot be silently assigned to the wrong Session.
45. Inventory operations retain their own transaction attribution.
46. Handover UUID synchronization is idempotent.
47. Repeated Handover submission cannot create duplicate Sessions.
48. Repeated Handover submission cannot duplicate cash movement.
49. Offline Handover requires trusted authorization.
50. Offline Handover uses the same UUID after synchronization.
51. Server authority determines final Session state.
52. Offline conflicts are explicit.
53. Conflict resolution requires authorization.
54. Conflict resolution requires a reason.
55. Conflict resolution is audited.
56. Handover corrections do not overwrite original Handover data.
57. Handover corrections require authorization.
58. Handover corrections require a reason.
59. Original cash difference remains historically visible.
60. Original cashier identities remain historically visible.
61. Original Session UUIDs remain historically visible.
62. Handover completion records acceptance actor.
63. Handover completion records acceptance time.
64. Incoming cashier acceptance does not alter outgoing Session history.
65. Rejected acceptance does not silently complete Handover.
66. Failed Handover does not create a second active Session.
67. Failed Handover can be safely retried.
68. Lost network response can be retried using Handover UUID.
69. Application crash cannot create an ambiguous final financial state.
70. Subscription expiry cannot be bypassed by offline Handover.
71. Deactivated incoming Employee cannot become active cashier.
72. Revoked Device cannot start unauthorized new Handover operations.
73. Inactive Branch cannot start a new Handover.
74. Deleted Business cannot accept stale Handover events.
75. Historical Handover remains readable after subscription expiry.
76. Handover history remains reconstructable after configuration changes.
77. Handover reports use authoritative Session records.
78. Notification failure does not roll back Handover.
79. Report generation failure does not roll back Handover.
80. Handover state is concurrency-safe.
81. Stale optimistic-concurrency updates are rejected.
82. Cache is not authoritative.
83. Business isolation is mandatory.
84. Branch isolation is mandatory.
85. Register isolation is mandatory.
86. Device attribution remains available.
87. Initiator attribution remains available.
88. Approver attribution remains available.
89. Acceptance attribution remains available.
90. Handover timestamps remain available.
91. Handover comments remain available.
92. Handover correction history remains available.
93. Force intervention remains auditable.
94. Cash discrepancy cannot be silently transferred to the incoming cashier.
95. Original shortage cannot be erased by opening the next Session.
96. Original overage cannot be converted silently into sales revenue.
97. Incoming Session must have a distinct UUID.
98. Physical Register identity remains unchanged across normal handover.
99. Handover must not interrupt core POS financial integrity.
100. The complete cashier-to-cashier transition must always be reconstructable from authoritative records.

---

## 76. Related Documents

### Database

* `02_Database_Architecture.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`
* `22_Offline_and_Synchronization_Data_Model.md`
* `24_Data_Lifecycle_and_Deletion_Data_Model.md`

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

## 77. Final Rule

The Shift Handover model must make cashier responsibility and physical cash movement unambiguous.

The central rule is:

```text id="k5m8q2"
One physical Register.
One active Session.
One outgoing cashier.
One incoming cashier.
A new Session for every handover.
Original discrepancies remain with the outgoing Session.
Open Orders continue without changing their UUIDs.
Corrections never rewrite historical handover data.
```

The model must remain compatible with Cash, Payment, Order, Device Trust, Offline Operation, Synchronization, Audit, Reporting, Subscription, and Data Lifecycle domains.

