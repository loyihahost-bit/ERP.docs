# Cash Register and Cash Sessions

**Document ID:** FF-BA-009
**Status:** Accepted
**Version:** 2.0
**Scope:** Cash registers, cash sessions, opening, closing, reconciliation, cashier handover, discrepancies, corrections, and offline operation
**Parent Document:** `01_Business_Analysis/08_POS_and_Order_Management.md`

---

## 1. Purpose

This document defines the business requirements for branch cash registers and cash sessions.

The cash-session model must provide:

* Clear responsibility for physical cash
* Accurate cash reconciliation
* Controlled cashier handover
* Reliable session history
* Discrepancy tracking
* Controlled corrections
* Strong auditability
* Offline continuity where authorized
* Fast and simple everyday operation

The model must remain simple enough for normal restaurant operations while preserving financial and historical integrity.

---

## 2. Cash Register Model

The current business model assumes:

**One cash register per branch.**

A branch normally operates one cash register and one primary POS/cashier computer.

The architecture must not prevent future support for multiple registers per branch.

Each cash register has a permanent system identity.

The cash register identity remains stable across all historical and future cash sessions.

---

## 3. Cash Register and Cash Session Relationship

The business relationship is:

**Business → Branch → Cash Register → Cash Sessions**

A cash register represents the physical or logical cash point used by a branch.

A cash session represents one operating period belonging to that register.

A cash register may therefore have many historical sessions.

Each cash session has its own permanent identity.

The cash session is also associated with the business, branch, responsible employee, device, orders, payments, and relevant audit events.

---

## 4. Cash Session Lifecycle

A cash session follows this general lifecycle:

**Not Open → Open → Closing/Reconciliation → Closed**

A closed session is final from a lifecycle perspective.

A closed session must never be reopened as an active cash session.

Corrections after closing are separate controlled operations and do not change the lifecycle state back to `Open`.

---

## 5. Manual Opening

A cash session is opened manually.

The system must not automatically create a new cash session merely because:

* a new calendar day starts;
* the previous session crossed midnight;
* a cashier logs into the POS;
* the branch becomes active.

The responsible cashier must explicitly open the new session.

Opening must be associated with:

* Business
* Branch
* Cash register
* Employee
* Device
* Opening timestamp
* Opening cash amount
* Cash session identity

The opening event must be auditable.

---

## 6. Opening Cash Amount

The opening process records the physical cash amount with which the new session begins.

The opening amount becomes part of the session's cash calculation.

The original entered value must remain historically available.

If an authorized correction is later required, the correction must not erase the original opening value.

---

## 7. Open Session Duration

A cash session may remain open overnight.

The system must not automatically close a session at midnight.

A session may therefore cross one or more calendar boundaries when operationally necessary.

The session period is determined by:

**Opening Timestamp → Closing Timestamp**

rather than by a calendar date.

---

## 8. One Active Session

Under the current one-register-per-branch model, a register may have only one active cash session at a time.

The system must prevent creation of another active session while the current session remains open.

A new cashier cannot simply open another session while the previous session is still active.

Cashier change must follow the controlled handover process defined in this document.

---

## 9. Cashier Responsibility

Every open cash session must have an explicitly identified responsible employee.

Responsibility is not determined merely by the employee currently logged into the POS.

A different employee logging into the system does not automatically become responsible for an already-open session.

When responsibility changes, the existing session must be closed and the new cashier must open a new session using their own identity.

Historical responsibility must remain attached to the original session.

---

## 10. Cash Session Context

Every cash session must retain sufficient context to identify its operational ownership.

At minimum, the session is associated with:

* Business
* Branch
* Cash register
* Responsible employee
* Opening device
* Closing device where applicable
* Opening timestamp
* Closing timestamp
* Opening cash
* Expected cash
* Actual cash
* Difference
* Payment totals
* Relevant orders
* Handover information where applicable
* Comments
* Corrections
* Audit history

---

## 11. Operations During an Open Session

During an open session, permitted employees may perform authorized POS operations.

Relevant operations may include:

* Order creation
* Order modification
* Order cancellation
* Payment recording
* Refund operations where authorized
* Cash-related operations
* Other authorized POS operations

Relevant cash-affecting activity must remain associated with the active cash session.

Permission rules are defined by the Users, Roles, and Permissions documentation.

---

## 12. Payment Types

The system must support at least:

* Cash
* Card
* Debt
* Mixed

The architecture must allow additional payment methods in the future.

The cash session must distinguish cash from non-cash payment values.

Card amounts are derived from recorded payment transactions.

The cashier does not manually enter the card total during normal session closing.

Debt is recorded as a payment method but does not represent physical cash received during closing.

Mixed payments must be decomposed into their actual payment components for reconciliation.

---

## 13. Cash-Affecting Transactions

The expected physical cash calculation must consider relevant cash-affecting activity during the session.

Depending on the applicable payment and cash rules, this may include:

* Opening cash
* Cash sales
* Cash portions of mixed payments
* Cash refunds
* Authorized cash movements
* Other configured cash-affecting transactions

The exact financial calculation is defined in the Payments, Finance, and Database documentation.

---

## 14. Expected Cash

At reconciliation time, the system calculates the expected physical cash.

The expected amount is system-derived.

The cashier must not be required to calculate it manually.

The expected amount must remain hidden before the cashier submits the actual physical cash count.

This rule applies to both normal closing and the physical cash-count stage of cashier handover.

---

## 15. Actual Cash Entry

The responsible cashier physically counts the available cash.

The cashier then enters the actual counted cash amount.

The cashier is responsible for the accuracy of the entered physical cash amount.

The system must not reveal the expected amount before this entry is submitted.

The cashier must physically count the cash independently of the system's expected value.

---

## 16. Expected Amount Visibility

Before actual cash is entered:

* Expected cash remains hidden.
* The cashier performs the physical count independently.

After actual cash is submitted:

The system reveals the reconciliation information, including where applicable:

* Expected cash
* Actual cash
* Difference
* Relevant order count
* Payment totals
* Cash session information
* Responsible cashier information

This behavior is intended to reduce bias during physical cash counting.

---

## 17. Cash Difference

The system calculates:

**Difference = Actual Cash − Expected Cash**

The result may represent:

* No difference
* Shortage
* Overage

The original calculated result must remain historically traceable.

A discrepancy must never be silently removed or replaced.

---

## 18. Cash Recount

If a discrepancy exists, the system must require or strongly guide the responsible cashier through the applicable recount/confirmation process.

The cashier may recount the physical cash.

The recount must not erase the original entered value or previous reconciliation state.

The system must retain the relevant reconciliation history.

If the final discrepancy remains, the applicable discrepancy explanation process must be completed.

---

## 19. Discrepancy Explanation

When a relevant shortage or other discrepancy remains, the responsible cashier must provide a comment or explanation.

The explanation must be associated with the relevant cash session or handover event.

The comment must not replace the structured financial values.

The system must retain:

* Expected cash
* Actual cash
* Difference
* Explanation
* Responsible employee
* Timestamp

---

## 20. Owner Notification

The Owner must be notified when a relevant cash discrepancy remains after the required reconciliation process.

The notification should provide enough context to understand:

* Business
* Branch
* Cash register
* Cash session
* Responsible cashier
* Expected amount
* Actual amount
* Difference
* Relevant time
* Cashier explanation

The Owner does not need to participate in ordinary cash counting or routine closing.

---

## 21. Cashier Closing

The responsible cashier manually closes the current cash session.

Closing records at minimum:

* Closing employee
* Closing timestamp
* Actual cash
* Expected cash
* Difference
* Payment totals
* Relevant order information
* Closing comment where required
* Closing device where applicable

The close event becomes part of permanent session history.

---

## 22. Cashier Comment on Closing

Where the closing process requires or allows a cashier comment, the comment becomes part of the session history.

A closing comment that requires Owner attention must generate the applicable Owner notification.

The comment must also appear in the relevant reporting context.

---

## 23. Closed Sessions Remain Closed

A closed cash session must remain closed.

The system must never reopen the session as an active cash session merely to change historical information.

After closing:

* The session remains `Closed`.
* New transactions cannot be attached as normal active-session transactions.
* Historical values cannot be silently overwritten.
* Authorized corrections must use the correction workflow.

Any business process described as "reopening" a correction opportunity must not be interpreted as reopening the cash session itself.

---

## 24. Cashier Handover Model

Cashier handover is implemented through a session boundary.

The final process is:

**Previous Cashier → Close Current Cash Session → New Cashier Authenticates → New Cashier Opens New Cash Session**

The previous cashier's session becomes closed.

The new cashier becomes responsible through a new cash session.

This preserves a clear responsibility boundary between employees.

---

## 25. Handover Requires Closing the Previous Session

A cashier must not simply transfer responsibility for an already-open session to another employee.

The previous cashier must complete the closing/reconciliation process.

After successful closing:

* The previous session remains closed.
* The previous cashier remains historically responsible for that session.
* The new cashier authenticates using their own employee account.
* The new cashier opens a new cash session.

---

## 26. New Cashier Authentication

The new cashier must authenticate using their own employee identity.

The system must not allow the new cashier to assume responsibility using:

* The previous cashier's account
* The previous cashier's credentials
* The previous cashier's session identity

The new cash session must record the new cashier as its responsible employee.

---

## 27. Handover Physical Cash Count

During the handover process, the previous session is closed and its cash is reconciled.

The physical cash available for the next session is counted by the new cashier as part of opening the new session.

The new cashier enters the physical opening cash amount using their own authenticated session.

Expected values from the previous session must not be exposed before the relevant physical cash entry where the business process requires an independent count.

---

## 28. Handover Reconciliation

The handover process must preserve both sides of the responsibility boundary.

The system must retain:

### Previous session

* Previous cashier
* Previous cash session
* Expected closing cash
* Actual closing cash
* Difference
* Closing comments
* Corrections

### New session

* New cashier
* New cash session
* Opening cash
* Opening timestamp
* Opening device
* Relevant branch and register

The new session must not overwrite the previous session's closing history.

---

## 29. Handover Discrepancy

If the previous session closes with a shortage or overage, the discrepancy remains attached to the previous cashier/session.

The new cashier does not automatically inherit responsibility for the previous session's historical discrepancy.

The new cashier's opening amount belongs to the new session.

This creates a clear financial responsibility boundary.

---

## 30. Handover and Open Orders

Open orders must not disappear when cashier responsibility changes.

Orders that remain operationally active may continue to be processed by the new cashier according to their permissions.

The order's permanent UUID and historical events remain unchanged.

Changing the active cashier or operational context must not rewrite the original order creation event.

---

## 31. Handover and Order History

Where cashier responsibility changes during the lifecycle of an order, the system must preserve relevant employee/session context.

The order remains traceable to:

* Original employee
* Current responsible employee where applicable
* Relevant cash session(s)
* Branch
* Device(s)
* Order UUID

Historical events must not be rewritten merely because responsibility changed.

---

## 32. Payment Totals at Closing

The system must derive payment totals from recorded payment transactions.

The closing view may show:

* Cash total
* Card total
* Debt total
* Mixed-payment breakdown
* Other configured payment totals

The cashier does not manually enter card, debt, or other non-cash totals during physical cash reconciliation.

Only the actual physical cash amount is manually entered for cash reconciliation.

---

## 33. Cash Register Physical Scope

The current model assumes one physical cash register per branch.

The system may later support multiple registers.

If multiple registers are introduced in the future, each register must maintain separate:

* Register identity
* Active session
* Responsible cashier
* Cash calculations
* Closing history
* Corrections
* Audit history

The current business requirements must not make such expansion structurally impossible.

---

## 34. Cash Session Corrections

Authorized employees may perform corrections against a closed cash session.

A correction must:

* Preserve the original value
* Record the corrected value
* Require a reason/comment
* Identify the employee performing the correction
* Record the correction timestamp
* Record the correction sequence
* Recalculate the affected result where applicable
* Preserve the complete correction history

A correction must never silently overwrite the original historical value.

---

## 35. Correction Permission

Closed cash-session correction requires a dedicated permission.

The Owner has authority to perform or authorize corrections according to the permission model.

A Manager or other employee may perform corrections only if explicitly granted the required permission.

Normal cashier permission does not automatically grant closed-session correction permission.

Permission scope must follow the standard:

**Role Permission + Employee Override + Branch Scope + Subscription Entitlement**

---

## 36. Initial Correction Limit

A closed cash session may initially receive a maximum of:

**3 corrections**

The limit belongs to the individual cash session.

Every completed correction counts toward the session's correction count.

Rejected correction requests do not themselves change the correction count.

The system must retain the complete history of all correction activity.

---

## 37. Correction After Three Corrections

After the initial three corrections have been consumed, another correction requires explicit authorization.

The authorization grants:

**Exactly one additional correction.**

One authorization must not create unlimited correction capability.

After the authorized correction is completed, that authorization is consumed.

The session remains closed throughout this process.

---

## 38. Additional Correction Authorization

An additional correction may be authorized by:

* Owner; or
* An appropriately authorized Manager.

The authorization must include:

* Cash session
* Requesting employee
* Current correction count
* Reason
* Authorizing employee
* Authorization timestamp
* Number of additional corrections authorized

The number of corrections granted by one authorization must be explicitly recorded.

Under the standard workflow, one authorization grants exactly one correction.

---

## 39. Correction Request

When an additional correction requires authorization, the requesting employee submits a correction request.

The request must provide relevant context, including:

* Cash session
* Responsible cashier
* Current correction count
* Previous correction results
* Current discrepancy
* Reason for requesting another correction
* Existing correction history

The requesting employee must have sufficient permission to submit the request.

---

## 40. Correction Request Approval

An authorized Owner or Manager may approve the request.

Approval creates authorization for exactly one additional correction.

The approval must be recorded in audit history.

After the authorized correction is completed, the authorization is consumed.

A consumed authorization cannot be reused.

---

## 41. Correction Request Rejection

A correction request may be rejected.

A rejection requires an explanation.

The rejected request remains in history.

The requesting employee does not automatically receive additional correction authority after rejection.

If the business later determines that another correction opportunity is appropriate, a separately authorized action must be recorded.

The previous rejection and its explanation remain visible.

---

## 42. Correction Opportunity Reopening

A correction opportunity may be reopened through an authorized workflow.

This does **not** reopen the cash session.

It only permits a new controlled correction against the already-closed session.

The reopening/authorization event must record:

* Cash session
* Previous correction count
* Reason
* Authorizing employee
* Timestamp
* Number of newly authorized corrections
* Resulting correction

The session lifecycle remains `Closed`.

---

## 43. Original Data Preservation

Every correction must maintain a traceable history:

**Original Value → Corrected Value**

The system must retain at minimum:

* Original value
* Corrected value
* Reason
* Employee
* Timestamp
* Correction sequence
* Authorization context where applicable

Historical values must never be physically erased.

---

## 44. Correction Impact on Reports

When a closed cash session is corrected, affected reporting data must reflect the corrected state according to report-versioning rules.

Previously generated report versions remain immutable.

If the correction changes a report result, a new report version must be created according to the reporting requirements.

The system must retain the relationship between:

* Cash session
* Correction
* Report version
* Change history
* Audit event

---

## 45. Offline Cash Sessions

Cash-session operations may continue offline only on trusted devices with valid offline authorization.

Offline operation must not bypass:

* Employee identity
* Branch scope
* Cash-session responsibility
* Permission restrictions
* Session lifecycle
* Closed-session rules
* Correction limits
* Audit requirements
* Subscription restrictions

Offline transactions must use the existing UUID-based idempotency model.

After reconnection, synchronization must be validated by the server.

The server remains authoritative.

Offline operation must not allow a second active session to be created where the server-side business rules prohibit it.

---

## 46. Offline Cash Reconciliation

Offline cash reconciliation must preserve the same business sequence as online operation.

The device may temporarily store:

* Opening information
* Cash transactions
* Closing information
* Physical cash entry
* Difference
* Comments
* Handover-related information
* Correction events where explicitly supported

Synchronization must preserve event order and idempotency.

A synchronization failure must not silently discard a cash event.

Conflicts or rejected operations must remain traceable.

---

## 47. Reporting Period

A cash-session report is based on:

**Opening Timestamp → Closing Timestamp**

A session that crosses midnight remains one session.

The system must not automatically divide the session because the calendar date changed.

Reports must use the actual session boundaries.

---

## 48. Open Sessions in Reports

Reports that require finalized cash reconciliation must not treat an open session as a completed closed session.

Where a report includes current open-session information, the open status must be explicit.

Monthly finalized cash reports must use the applicable closed-session state.

---

## 49. Monthly Cash Reporting

Monthly reporting must include relevant cash-session information.

Where applicable, reports include:

* Business
* Branch
* Cash register
* Cash session
* Responsible cashier
* Opening information
* Closing information
* Opening cash
* Expected cash
* Actual cash
* Difference
* Payment totals
* Handover/session-boundary information
* Corrections
* Correction requests
* Approvals
* Rejections
* Additional correction authorizations
* Audit history

Monthly reports follow the general report-generation and versioning rules.

---

## 50. Cash Session Audit

Important cash-session events must be auditable.

These include:

* Session opening
* Session closing
* Cash entry
* Cash reconciliation
* Recount
* Discrepancy
* Cashier comment
* Owner notification
* Correction
* Correction request
* Correction approval
* Correction rejection
* Additional correction authorization
* Correction opportunity reopening
* Handover/session transition
* Relevant synchronization events

Audit records must preserve, where applicable:

* Actor
* Business
* Branch
* Cash register
* Cash session
* Device
* Timestamp
* Action
* Original value
* New value
* Reason
* Related entity

---

## 51. Security Principles

The cash-session model must prevent silent manipulation of cash history.

The following principles are mandatory:

1. Every open session has a clearly identified responsible employee.
2. A branch/register cannot have multiple active sessions under the current model.
3. Closed sessions never reopen as active sessions.
4. Cashier handover closes the previous session and creates a new session for the new cashier.
5. The new cashier uses their own employee identity.
6. Physical cash is entered by the responsible cashier.
7. Expected cash remains hidden until actual cash is entered.
8. Payment totals are derived from recorded transactions.
9. Corrections preserve original values.
10. Corrections require appropriate permissions.
11. Three initial corrections are allowed per session.
12. Additional corrections require explicit one-correction authorization.
13. Every correction requires a reason.
14. Offline mode cannot bypass cash controls.
15. Audit history cannot be silently modified.
16. Trusted-device status does not grant permissions by itself.

---

## 52. Historical Integrity

Cash sessions are financial operational history.

The system must preserve the distinction between:

* Original transaction
* Session closing state
* Correction
* Recalculated state
* Report version

The latest corrected state may be used for current reporting, but historical versions must remain reconstructable.

A correction must never make it impossible to determine what the original session contained.

---

## 53. Performance Requirements

Cashier operations must remain fast.

The system should avoid unnecessary confirmation steps during ordinary POS operations.

Security and audit mechanisms should operate efficiently without requiring powerful hardware.

Cash opening, payment, order processing, closing, and handover must remain understandable to ordinary restaurant employees.

Offline functionality must not introduce unnecessary delays to normal POS operations.

---

## 54. Business Rules Summary

| Area                     | Rule                                                 |
| ------------------------ | ---------------------------------------------------- |
| Registers                | Normally one per branch                              |
| Primary POS              | Normally one primary cashier/POS computer per branch |
| Future registers         | Architecture must not prevent multiple registers     |
| Opening                  | Manual                                               |
| Closing                  | Manual                                               |
| Overnight                | Session may remain open overnight                    |
| Auto-close               | Not allowed                                          |
| Active sessions          | One active session per register                      |
| Responsible cashier      | Explicitly identified                                |
| Cashier change           | Close previous session, then open new session        |
| New cashier              | Must authenticate with own account                   |
| Payment types            | Cash, Card, Debt, Mixed at minimum                   |
| Physical cash entry      | Cashier enters actual counted cash                   |
| Expected cash            | Hidden until actual cash is entered                  |
| Difference               | Calculated automatically                             |
| Recount                  | Required/guided when discrepancy remains             |
| Discrepancy explanation  | Required when relevant                               |
| Owner notification       | Required for relevant unresolved discrepancy         |
| Closed session           | Remains closed                                       |
| Correction               | Controlled correction workflow                       |
| Initial corrections      | Maximum 3                                            |
| Additional correction    | Exactly one per authorization                        |
| Additional authorization | Owner or authorized Manager                          |
| Correction request       | Auditable                                            |
| Rejection                | Requires explanation                                 |
| Correction reopening     | Reopens correction opportunity, not the session      |
| Original values          | Always preserved                                     |
| Open orders              | Continue operationally after cashier change          |
| Historical orders        | Original activity remains unchanged                  |
| Offline                  | Supported where authorized                           |
| Offline bypass           | Not allowed                                          |
| Reporting period         | Opening timestamp to closing timestamp               |
| Open sessions            | Not treated as finalized closed sessions             |
| Audit                    | Required for important session events                |

---

## 55. Business Analysis Boundary

This document defines the business requirements for cash registers and cash sessions.

The following remain implementation decisions:

* Cash-session database structure
* Financial calculation implementation
* POS cash UI
* Cash drawer integration
* Hardware integration
* Payment gateway integration
* Printer integration
* Offline cash synchronization implementation
* Report generation implementation
* Permission enforcement implementation
* Exact API contracts
* Database transaction strategy
* Concurrency implementation
* Encryption implementation

These decisions must be defined later in the Architecture, Database, Backend, Frontend, Security, API, Testing, and Operations documentation.

---

## Related Documents

* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `01_Business_Analysis/08_POS_and_Order_Management.md`
* `01_Business_Analysis/10_Shift_Handover.md`
* `01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `01_Business_Analysis/16_Reports_and_Dashboards.md`
* `01_Business_Analysis/18_Audit_and_Change_History.md`
* `01_Business_Analysis/20_Business_Rules.md`
* `04_Architecture`
* `05_Database`
* `06_Backend`
* `07_Frontend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`

