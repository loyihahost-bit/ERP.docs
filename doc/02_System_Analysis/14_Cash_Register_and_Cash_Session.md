# Cash Register and Cash Session

**Document ID:** SA-14
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for Cash Registers and Cash Sessions.

It specifies:

* Cash Register identity;
* Cash Session lifecycle;
* session opening and closing;
* opening cash;
* physical cash counting;
* expected and actual cash;
* shortage and overage;
* cash-session corrections;
* session concurrency;
* offline operation;
* reporting;
* relationship with payments and shift handover.

The objective is to preserve accurate cash history while keeping normal cashier operations fast and simple.

---

## 2. Cash Register Model

The current business model assumes one primary Cash Register per Branch.

The architecture must not prevent future support for multiple registers.

The relationship is:

```text id="r8c4m2"
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Sessions
```

---

## 3. Cash Register Identity

Every Cash Register has a permanent Cash Register UUID.

The Cash Register identity represents the physical/operational register.

It is different from:

* Cash Session UUID;
* Device UUID;
* Employee UUID;
* Order UUID;
* Payment UUID.

A Cash Register remains the same while Cash Sessions change.

---

## 4. Cash Register and Device

A Cash Register is not permanently identical to one physical computer.

Trusted devices may operate the same Cash Register according to authorization.

The same Cash Session may be used by the same cashier from multiple trusted devices when the business rule permits it.

Every action still records its Device UUID.

---

## 5. Cash Register Branch Ownership

A Cash Register belongs to exactly one Branch.

The system must validate:

* Business UUID;
* Branch UUID;
* Cash Register UUID.

A Cash Register cannot normally be used by another Branch.

Cross-Branch cash operation is not allowed through ordinary POS workflows.

---

## 6. Cash Session

A Cash Session represents one operational cash period for a cashier.

Each session has its own UUID.

A Cash Session belongs to:

* one Business;
* one Branch;
* one Cash Register;
* one primary cashier/session owner;
* one opening context.

---

## 7. Cash Session Lifecycle

The normal lifecycle is:

```text id="p7n3v5"
Not Open
   ↓
Open
   ↓
Closed
```

A Closed Cash Session cannot become Open again.

Corrections are performed through separate controlled operations.

---

## 8. Opening a Cash Session

A cashier may open a new Cash Session when:

* the employee is active;
* the employee has required permission;
* the Business is active for modification;
* the Branch is valid;
* the Cash Register is valid;
* no conflicting active session exists under the applicable concurrency rule;
* device authorization is valid.

---

## 9. Opening Cash

Opening a Cash Session requires an opening cash amount.

The opening amount represents physical cash available at the beginning of the session.

The system records:

* opening amount;
* cashier;
* Branch;
* Cash Register;
* Device;
* timestamp;
* Cash Session UUID.

The opening amount becomes part of the expected cash calculation.

---

## 10. Expected Cash Visibility

The expected cash amount is not shown before the cashier enters the physical cash count during session closing.

This prevents the cashier from simply copying the system-calculated amount without performing an actual count.

The cashier must first enter the actual physical cash.

---

## 11. Cash Session Operations

During an Open Cash Session, authorized operations may include:

* Cash payments;
* Cash debt repayments;
* Cash refunds where permitted;
* approved cash corrections;
* other explicitly supported cash movements.

Every relevant operation must be linked to the Cash Session.

---

## 12. Card Payments

Card payments are recorded in the Cash Session context where relevant for reporting, but they do not increase physical cash.

The system must distinguish:

```text id="m4q8s1"
Cash Session Financial Activity
├── Physical Cash
└── Card Activity
```

Only physical cash contributes to actual cash count.

---

## 13. Debt Payments

Cash debt repayments contribute to physical cash.

The system must identify them separately from ordinary sales payments.

Debt repayment records retain their own financial identity.

---

## 14. Mixed Payments

For Mixed payments:

* Cash portion contributes to physical cash;
* Card portion does not;
* the logical payment remains associated with the Order.

The Cash Session records the applicable cash effect.

---

## 15. Cash Session Expected Amount

The system calculates expected cash using authoritative cash movements.

Conceptually:

```text id="q5v9c3"
Expected Cash
=
Opening Cash
+ Cash Inflows
− Cash Outflows
± Approved Cash Adjustments
```

The exact set of cash movements is determined by the applicable business rules.

---

## 16. Physical Cash Count

When closing a Cash Session, the cashier physically counts the cash.

The cashier enters the actual cash amount into the system.

The system then displays:

* expected cash;
* actual cash;
* difference;
* relevant Order count;
* payment totals;
* other required session information.

---

## 17. Cash Difference

The difference is calculated as:

```text id="x7m2p8"
Difference
=
Actual Cash
−
Expected Cash
```

Possible results:

* positive → overage;
* zero → balanced;
* negative → shortage.

The original calculated difference is preserved.

---

## 18. Shortage

A shortage occurs when:

```text
Actual Cash < Expected Cash
```

The system records:

* shortage amount;
* Cash Session;
* cashier;
* Branch;
* timestamp;
* relevant context.

The shortage must not be silently removed.

---

## 19. Overage

An overage occurs when:

```text
Actual Cash > Expected Cash
```

The system records the overage as part of the session result.

The original overage remains historically preserved.

---

## 20. Closing Comment

The cashier may be required to provide a closing comment according to the configured rules.

A comment may explain:

* shortage;
* overage;
* operational issue;
* other relevant circumstances.

Where configured, a discrepancy or significant closing comment may trigger an Owner notification.

---

## 21. Session Closing

Closing a Cash Session requires:

1. Valid cashier identity.
2. Valid session state.
3. Required permissions.
4. Physical cash entry.
5. Difference calculation.
6. Required comment/reason where applicable.
7. Final validation.
8. Atomic session close.

After successful closing, the session becomes permanently historical.

---

## 22. Closed Session

A Closed Cash Session:

* cannot accept ordinary new payments;
* cannot be reopened as an active session;
* remains available for reporting;
* retains all historical transactions;
* may be subject to separate correction operations.

---

## 23. Session Correction

Corrections are separate from reopening.

A correction may adjust a historical result according to the permission model.

The system must preserve:

* original value;
* corrected value;
* actor;
* timestamp;
* reason;
* authorization;
* correction UUID;
* parent session/reference.

The original session remains closed.

---

## 24. Correction Limit

A Cash Session supports a maximum of three ordinary corrections.

Each correction is independently recorded.

After the third correction, the normal correction limit is exhausted.

---

## 25. Additional Correction Authorization

After the normal correction limit is exhausted, exactly one additional correction may be authorized.

Authorization may be performed by:

* Owner;
* authorized Manager.

The authorization is consumed by the additional correction.

After that authorization is used, the session cannot receive another ordinary correction through the same mechanism.

Administrative intervention is required for further action.

---

## 26. Reopen Meaning

The system must not interpret correction authorization as physically reopening the Cash Session.

The term `reopen`, where used in the business workflow, means:

> authorize one additional correction opportunity.

The Cash Session remains historically Closed.

---

## 27. Correction Immutability

A correction cannot overwrite the original shortage or overage.

For example:

```text id="k3p7m9"
Original Difference:
-50,000

Correction:
+20,000

Historical Original:
-50,000

Effective Adjusted Result:
-30,000
```

The original difference remains visible.

---

## 28. Cash Session Concurrency

Only one active Cash Session may exist for the applicable Branch/Register according to the current business model.

If two requests attempt to open a conflicting session:

```text id="v8n2c5"
Request A → Open Session
Request B → Open Session

First valid request → Success
Second request → Rejected
```

The server must enforce this atomically.

---

## 29. Session Opening Concurrency

Client-side checks are insufficient.

The server must enforce active-session uniqueness using appropriate:

* database constraints;
* transaction isolation;
* locking;
* version checks;
* or equivalent mechanisms.

---

## 30. Cashier Logout

Logging out does not automatically close a Cash Session.

If a cashier logs out while the session remains Open:

* the session remains Open;
* no automatic close occurs;
* another authorized cashier may perform the handover process;
* Owner or authorized employee may force-close when required.

Force close is audited.

---

## 31. Cashier Handover

Cashier handover is a separate operational process.

The normal sequence is:

```text id="h4m8q2"
Previous Cashier
      ↓
Close Previous Cash Session
      ↓
New Cashier Authenticates
      ↓
Count / Accept Cash
      ↓
Open New Cash Session
```

The physical Cash Register remains the same.

A new Cash Session UUID is created.

---

## 32. Previous Session Ownership

The previous Cash Session remains permanently associated with the previous cashier.

Its transactions, payments, shortage, overage, corrections and audit history remain tied to that session.

The new cashier does not inherit the previous session identity.

---

## 33. Opening Amount After Handover

The new Cash Session records its own opening cash amount.

The amount is entered as the physical cash available when the new session begins.

The new session does not overwrite the previous session's closing amount.

---

## 34. Open Orders During Handover

Open/unpaid Orders continue to exist during cashier handover.

The Order UUID remains unchanged.

The Table Visit/Session remains unchanged.

The new cashier may continue authorized operations after the new Cash Session is opened.

---

## 35. Order and Cash Session Relationship

An Order is not owned by one Cash Session for its entire lifetime.

Financial actions against the Order are associated with the Cash Session in which they occur.

Example:

```text id="c6r9p4"
Order #125

Accepted
   ↓
Cash Session A

Later Payment
   ↓
Cash Session B
```

The Order identity remains unchanged.

---

## 36. Payment During Session Transition

If a payment operation occurs during session transition:

* payment before transition belongs to the previous session;
* payment after transition belongs to the new session;
* an operation caught during the transition remains pending until the session context is resolved.

The system must not silently assign the payment to the wrong session.

---

## 37. Cash Session and Inventory

Cash Session state does not directly control inventory.

Inventory is controlled by Order and Inventory transaction rules.

Closing a Cash Session must not:

* reset stock;
* duplicate deductions;
* reverse inventory.

---

## 38. Cash Session and Kitchen

Closing or opening a Cash Session does not directly change kitchen status.

Kitchen processing remains associated with Orders.

Open Orders may continue through kitchen lifecycle during cashier handover.

---

## 39. Cash Session and Tables

Cash Session state does not directly determine table occupancy.

Tables remain governed by:

* Table Visit/Session;
* active Orders;
* payment state;
* table occupancy rules.

Cashier handover does not reset tables.

---

## 40. Offline Cash Session

A trusted device with valid offline authorization may open and operate a Cash Session offline when permitted.

The offline authorization must include sufficient information to validate:

* Business;
* Branch;
* Employee;
* Device;
* subscription entitlement;
* offline validity period;
* relevant permissions.

---

## 41. Offline Cash Session Identity

An offline Cash Session receives its own Cash Session UUID.

The UUID remains unchanged during synchronization.

The server must not replace it with a new session UUID merely because the session was created offline.

---

## 42. Offline Cash Operations

Offline operations may include permitted:

* Cash payments;
* Cash debt repayments;
* cash session operations;
* other authorized cash movements.

All offline transactions retain their original local UUIDs and context.

---

## 43. Offline Session Synchronization

When the device reconnects:

1. Cash Session events are queued.
2. Dependency order is respected.
3. Server validates Business/Branch/Employee/Device context.
4. Server validates session state.
5. Duplicate UUIDs are handled idempotently.
6. Valid events are synchronized.
7. Conflicts remain explicit.

The POS must continue working while synchronization runs in the background.

---

## 44. Offline Session Conflict

A conflict may occur when:

```text id="n5c8v2"
Offline Device:
Open Cash Session A

Server:
Another active session already exists
```

The server must not silently create two conflicting active sessions.

The event becomes a synchronization conflict or is rejected according to the authoritative state.

---

## 45. Offline Cash Count

If session closing is permitted offline:

* cashier enters the physical cash count locally;
* expected amount is calculated from locally known valid data;
* actual amount is stored;
* difference is calculated;
* the close event is synchronized later.

The server revalidates the session and cash movement history.

---

## 46. Offline Correction

Offline correction is allowed only if the valid offline authorization explicitly permits it.

The system must enforce:

* correction count;
* employee permission;
* session state;
* Branch scope;
* subscription entitlement.

The server validates the correction during synchronization.

---

## 47. Cash Session Audit

Important Cash Session operations are audited.

Examples:

* session creation;
* opening cash entry;
* session close;
* actual cash entry;
* shortage/overage;
* correction;
* additional correction authorization;
* force close;
* handover;
* offline session creation;
* synchronization conflict.

Audit context includes:

* Event UUID;
* Cash Session UUID;
* Cash Register UUID;
* Business UUID;
* Branch UUID;
* Employee UUID/System;
* Device UUID;
* timestamp;
* old state;
* new state;
* reason;
* source;
* result.

---

## 48. Cash Session Reporting

Reports must be able to show:

* session UUID;
* cashier;
* Cash Register;
* Branch;
* opening cash;
* expected cash;
* actual cash;
* shortage/overage;
* Cash payments;
* Card payments;
* Debt repayments;
* Cash refunds;
* corrections;
* Order count;
* opening time;
* closing time;
* comments;
* force-close status where applicable.

---

## 49. Monthly Cash Reports

Monthly automatic reports are generated according to the reporting rules.

The report waits for an Open Cash Session to close when the reporting period requires finalized cash-session data.

The report must not silently treat an open session as finalized.

---

## 50. Manual Cash Reports

Manual Cash Session reports may be generated for a maximum period of one calendar month.

Invalid date ranges are rejected.

Large report generation should run in the background.

---

## 51. Report Versioning

Cash Session reports use immutable report versions.

If a correction changes a relevant report metric:

* a new report version is created;
* previous versions remain immutable;
* the correction is linked to the relevant report version.

If the correction does not affect relevant report metrics, a new report version is not required.

---

## 52. Subscription and Entitlement

Cash Session modification is subject to Business subscription entitlement.

When subscription modification rights expire:

* new modifying cash operations are blocked;
* historical Cash Sessions remain viewable;
* permitted reports remain accessible;
* Excel export remains available according to permissions;
* offline authorization cannot bypass the restriction.

---

## 53. Cash Session Security

The system must distinguish:

* employee authentication;
* employee permission;
* Branch scope;
* Cash Register scope;
* Cash Session scope;
* trusted device;
* offline authorization.

A trusted device alone does not authorize Cash Session operations.

---

## 54. Cash Session Idempotency

Cash Session operations must use UUID-based idempotency where retries are possible.

Repeated requests must not create:

* duplicate sessions;
* duplicate opening cash entries;
* duplicate closing effects;
* duplicate corrections.

---

## 55. Cash Session Error Handling

Errors are classified as:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

The cashier receives a business-safe message.

Technical details remain in structured logs.

Retryable operations use idempotency and bounded retry policies.

---

## 56. Core Transaction Boundaries

The following are core Cash Session operations:

* opening a session;
* recording opening cash;
* recording Cash payment;
* recording Cash repayment;
* recording Cash refund;
* closing a session;
* recording the closing difference;
* applying an authorized correction.

Each core operation must be atomic.

---

## 57. Secondary Operations

Secondary processing may include:

* notifications;
* report generation;
* synchronization;
* background calculations;
* non-critical processing.

Secondary failure must not roll back a successfully committed Cash Session transaction.

---

## 58. Performance

Cash Session operations are part of the POS workflow.

The system must not block normal cashier operations because of:

* report generation;
* notification delivery;
* synchronization;
* printer communication;
* unrelated background processing.

Background synchronization must not freeze the POS.

---

## 59. Historical Integrity

The system must preserve:

* original opening cash;
* cash movements;
* expected amount;
* actual amount;
* original shortage/overage;
* corrections;
* authorization;
* force-close events;
* handover history;
* session status changes.

Closed sessions remain immutable as historical sessions.

---

## 60. System Invariants

The following invariants apply to Cash Register and Cash Session:

1. A Cash Register belongs to exactly one Branch.
2. A Cash Register has a permanent UUID.
3. A Cash Session has a unique UUID.
4. Cash Register UUID and Cash Session UUID are different identities.
5. The current business model uses one primary Cash Register per Branch.
6. The architecture must not prevent future multiple registers.
7. A Cash Session belongs to one Business, Branch and Cash Register.
8. A Cash Session belongs to its cashier/session owner.
9. The normal lifecycle is Not Open → Open → Closed.
10. A Closed Cash Session cannot be reopened as an active session.
11. Corrections do not physically reopen a closed session.
12. Opening cash is recorded when a session is opened.
13. Expected cash is not shown before actual physical cash is entered during closing.
14. Actual cash is entered by physical count.
15. Difference equals actual cash minus expected cash.
16. Shortage and overage are preserved historically.
17. Cash payments affect physical cash.
18. Card payments do not affect physical cash.
19. Cash debt repayments affect physical cash.
20. Cash refunds affect physical cash.
21. Mixed payment Cash portions affect physical cash.
22. Closed sessions cannot receive ordinary new Cash transactions.
23. Logout does not automatically close a Cash Session.
24. Force close is separately controlled and audited.
25. Only one conflicting active Cash Session is allowed for the applicable Register/Branch context.
26. Active-session concurrency is enforced server-side.
27. Cashier handover creates a new Cash Session.
28. The physical Cash Register remains the same during normal handover.
29. Previous session history remains tied to the previous cashier.
30. New session has its own UUID and opening cash.
31. Open Orders remain open during cashier handover.
32. Order UUID does not change during handover.
33. Later payments belong to the Cash Session in which they occur.
34. Cash Session state does not directly control inventory.
35. Cash Session state does not directly control kitchen status.
36. Cash Session state does not directly control table occupancy.
37. Offline Cash Sessions require trusted-device authorization.
38. Offline Cash Sessions retain their own UUID.
39. Server does not replace offline Cash Session UUIDs.
40. Offline session events are synchronized idempotently.
41. Offline session conflicts are explicit.
42. Offline operations cannot bypass subscription entitlement.
43. Offline operations cannot bypass employee permissions.
44. Cash Session corrections are separate operations.
45. A maximum of three ordinary corrections is allowed.
46. One additional correction may be authorized after the limit.
47. Additional correction authorization is consumed once used.
48. Further intervention after the additional authorization requires administrative handling.
49. Original shortage/overage remains immutable.
50. Corrections preserve original and adjusted values.
51. Important Cash Session operations are audited.
52. Monthly finalized cash reports wait for required sessions to close.
53. Manual Cash Session reports are limited to one calendar month.
54. Report versions are immutable.
55. Report version changes occur only when relevant metrics change.
56. Duplicate Cash Session operations are prevented by idempotency.
57. Core Cash Session transactions are atomic.
58. Secondary processing failures do not roll back committed Cash Session transactions.
59. Heavy background work must not block POS.
60. Business and Branch isolation applies to all Cash Session operations.
61. Trusted Device status alone does not grant Cash Session permission.
62. Historical Cash Session relationships remain traceable after corrections and handover.

---

## 61. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 62. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `14_Cash_Register_and_Cash_Session.md`

**Next Document:** `15_Shift_Handover.md`

