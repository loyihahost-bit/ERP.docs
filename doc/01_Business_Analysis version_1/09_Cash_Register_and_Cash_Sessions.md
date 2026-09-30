# Cash Register and Cash Sessions

**Document ID:** FF-BA-009
**Status:** Accepted
**Version:** 1.0
**Scope:** Cash registers, cash sessions, opening, closing, reconciliation, discrepancies, and session corrections
**Parent Document:** `01_Business_Analysis/08_POS_and_Order_Management.md`

---

## 1. Purpose

This document defines the business requirements for cash registers and cash sessions.

The cash-session model must provide:

* Clear responsibility for physical cash
* Accurate payment reconciliation
* Controlled cashier handover
* Reliable session history
* Discrepancy tracking
* Auditable corrections
* Support for offline operation

The model must remain simple enough for everyday restaurant operations.

---

## 2. Cash Register Model

The current business model assumes:

**One cash register per branch.**

A branch normally operates one active cash register.

The architecture should not prevent future support for multiple registers if the business model is expanded.

Each cash register must have a permanent system identity.

The cash register identity must remain stable across multiple cash sessions.

---

## 3. Cash Register and Cash Session

A cash register represents the physical or logical register used by the branch.

A cash session represents one continuous operating period between:

**Cash Register Opening → Cash Register Closing**

Each cash session has its own permanent identity.

The cash register may therefore have many historical cash sessions.

---

## 4. Manual Opening

The cash register is opened manually.

The system must not automatically open a new cash session simply because a new calendar day has started.

The responsible cashier must perform the opening process.

Opening must be associated with:

* Cash register
* Branch
* Business
* Employee
* Device
* Opening time
* Opening cash amount
* Cash session identity

---

## 5. Open Session Duration

A cash session may remain open overnight.

The system must not automatically close a session at midnight.

The session remains open until an authorized employee completes the closing process.

Therefore, a cash-session reporting period is determined by:

**Opening Time → Closing Time**

rather than strictly by calendar date.

---

## 6. One Active Session

A branch cash register must not have multiple simultaneously active sessions under the current business model.

A new cashier cannot simply create another cash session while the previous session remains open.

The previous session must be handled according to the cash handover or closing process.

---

## 7. Cashier Responsibility

The employee responsible for an open cash session must be identifiable.

The system must retain the responsible employee identity throughout the session lifecycle.

Responsibility must not be inferred only from the latest login.

A different employee logging into the system does not automatically make that employee responsible for the open cash session.

---

## 8. Cash Register Opening Amount

The opening process must record the physical cash amount with which the session begins.

The amount becomes part of the session's financial calculation.

The system must preserve the original entered amount.

If an authorized correction is later required, the original value must remain available in history.

---

## 9. Cash Session Operations

During an open session, permitted employees may process restaurant operations according to their permissions.

Relevant operations may include:

* Orders
* Payments
* Refunds where permitted
* Cash-related operations
* Cashier handover
* Other authorized POS operations

Every relevant transaction must remain associated with the active cash session.

---

## 10. Payment Types

The cash session must track payment totals by payment type.

The system must distinguish at least:

* Cash
* Card

The architecture must allow additional payment types in the future.

The cashier does not manually enter the card total during closing.

The card amount is derived from recorded transactions.

---

## 11. Expected Cash

At closing, the system calculates the expected physical cash based on the session's recorded activity.

The calculation considers relevant cash-affecting transactions, including:

* Opening cash
* Cash sales
* Cash refunds
* Other configured cash movements

The exact accounting calculation is defined in the Finance and Payments documentation.

---

## 12. Actual Cash Entry

When closing the cash session, the cashier enters the amount of physical cash actually counted.

The cashier is responsible for entering the counted physical cash amount.

The system must not ask the cashier to manually calculate the expected cash.

---

## 13. Expected Amount Visibility

Before the cashier enters the actual physical cash amount, the expected cash amount must remain hidden from the cashier.

This prevents the expected amount from influencing the physical counting process.

After the cashier submits the actual cash amount, the system reveals the reconciliation information.

The displayed information must include:

* Expected cash
* Actual cash
* Difference
* Relevant order count
* Payment totals
* Session information

---

## 14. Cash Difference

The system calculates the difference between expected and actual cash.

The result may be:

* No difference
* Shortage
* Overage

The original calculated result must be preserved.

A discrepancy must not be silently removed from history.

---

## 15. Cashier Recount

If a discrepancy exists, the system should recommend recounting the physical cash.

The cashier may recount the cash before finalizing the session result.

The system must preserve the relevant entered values and resulting state.

The recount must not erase the original information.

---

## 16. Discrepancy Explanation

If a shortage or other discrepancy remains after the required process, the responsible cashier must provide an explanation/comment.

The explanation must be associated with the cash session.

The Owner must be informed about the discrepancy according to the notification rules.

The responsible employee remains identifiable.

---

## 17. Owner Notification

The Owner must be notified when a relevant cash discrepancy remains.

The notification should allow the Owner to understand:

* Which branch
* Which cash session
* Which cashier
* Expected amount
* Actual amount
* Difference
* Relevant time
* Cashier explanation where available

The Owner does not need to participate in every normal cash-closing operation.

---

## 18. Closing Confirmation

Closing a cash session finalizes the current session state.

The system records:

* Closing employee
* Closing time
* Actual cash
* Expected cash
* Difference
* Payment totals
* Relevant order information
* Closing comments where required

The closed session becomes part of historical reporting.

---

## 19. Closed Sessions Remain Closed

A closed cash session must remain closed.

It must not simply be reopened to change historical values.

If an error is discovered, the system must use the authorized correction process.

This protects the integrity of historical cash records.

---

## 20. Cash Session Corrections

Authorized employees may correct information in a closed cash session.

The correction process must:

* Preserve the original value
* Record the new value
* Require a reason/comment
* Identify the employee performing the correction
* Record the correction time
* Update the relevant calculated result
* Preserve the correction history

The correction must not silently overwrite the original session information.

---

## 21. Correction Permission

Closed cash-session correction requires a dedicated permission.

The Owner has authority to perform or authorize corrections according to the permission model.

Other employees may receive the relevant permission where explicitly authorized.

Possessing general cashier access does not automatically grant cash-session correction permission.

---

## 22. Initial Correction Limit

A closed cash session may initially be corrected up to:

**3 corrections**

The correction count is associated with the individual cash session.

Every correction counts toward the limit.

The system must retain the complete correction history.

---

## 23. Additional Correction Authorization

After the initial three corrections are used, another correction requires explicit authorization.

The Owner or an appropriately authorized Manager may grant permission for:

**Exactly one additional correction.**

Each additional authorization permits only one correction.

The authorization must include:

* Cash session
* Requesting cashier or employee
* Reason
* Authorizing employee
* Authorization time
* Number of permitted additional corrections

One authorization must not automatically allow unlimited future corrections.

---

## 24. Additional Correction History

Every additional correction authorization must remain in history.

The system must preserve:

* Original correction limit
* Number of corrections already used
* Additional correction requests
* Approval/rejection
* Authorization reason
* Authorized employee
* Resulting correction
* Date and time

The history must remain available in reports and audit records.

---

## 25. Correction Request

When an additional correction requires authorization, the requesting employee must submit a correction request.

The request must show relevant context, including:

* Cash session
* Responsible cashier
* Current correction count
* Previous correction results
* Latest discrepancy
* Requesting employee's reason
* Correction history

The approving employee must have sufficient authority to process the request.

---

## 26. Correction Request Approval

An authorized Owner or Manager may approve the request.

Approval creates authorization for exactly one additional correction.

The approval must be recorded in the audit history.

After the authorized correction is completed, the additional authorization is consumed.

It must not remain available for another correction.

---

## 27. Correction Request Rejection

A correction request may be rejected.

A rejection must require an explanation.

The rejected request remains in history.

The requesting employee must not automatically be able to submit another request for the same case after rejection.

The Owner or authorized Manager who rejected the request may later reopen the opportunity if appropriate.

The previous rejection and explanation must remain visible.

---

## 28. Reopening Correction Ability

"Reopening" a correction opportunity does not reopen the cash session itself.

It only grants the ability to perform one additional correction on the closed session.

The session remains historically closed.

The reopening authorization must be separately audited.

---

## 29. Original Data Preservation

Every correction must preserve the original information.

A corrected field must therefore have a traceable history:

**Original Value → Corrected Value**

The system must retain:

* Original value
* Corrected value
* Reason
* Employee
* Timestamp
* Correction sequence

Historical values must not be physically erased.

---

## 30. Correction Impact on Reports

If a closed cash session is corrected, the relevant report data must reflect the corrected state.

Previous generated reports remain immutable.

A new report version may be generated according to the report-versioning rules.

The system must retain the relationship between:

* Cash session
* Correction
* Report version
* Change history

---

## 31. Cashier Handover

Cashier handover is not a separate shift-change entity.

The process is:

**Previous Cashier → Close/Handover Process → New Cashier Accepts → New Cashier Becomes Responsible**

The previous cashier does not remain responsible after the handover has been successfully completed.

---

## 32. Handover Requires Employee Authentication

The new cashier must authenticate using their own employee account.

The new cashier must confirm that they have accepted responsibility for the cash register.

The system must not allow the new cashier to take responsibility simply by using the previous cashier's session.

---

## 33. Handover Cash Count

During handover, the new cashier physically counts the available cash.

The system does not initially reveal the expected cash amount.

The new cashier enters the counted physical amount.

After entry, the system displays the relevant reconciliation information.

This preserves the independence of the physical cash count.

---

## 34. Handover Result

After the new cashier submits the physical cash amount, the system displays:

* Expected cash
* Actual counted cash
* Difference
* Previous cashier information
* New cashier information
* Relevant order count
* Payment information

The result becomes part of the cash-session history.

---

## 35. Handover Confirmation

The previous cashier receives a handover notification.

The notification must provide exactly two required actions:

**Confirm**

or

**Recalculate**

One of these actions must be selected.

---

## 36. Handover Recalculation

If the previous cashier selects **Recalculate**, the system recalculates the relevant cash-session values.

The recalculation must not erase the previous handover information.

The system must preserve the relevant history of the process.

After recalculation, the required confirmation process continues.

---

## 37. Handover Confirmation

If the previous cashier selects **Confirm**, the handover is confirmed.

The system records:

* Previous cashier
* New cashier
* Confirmation
* Time
* Relevant cash result
* Handover history

The new cashier becomes responsible for the cash register.

---

## 38. Open Orders During Handover

Open orders must not disappear during cashier handover.

They automatically transfer to the new cashier's operational context.

The new cashier may continue working with those orders according to their permissions.

The order UUID and historical activity remain unchanged.

---

## 39. Handover and Order History

The system must preserve which cashier was responsible for an order before and after handover where applicable.

Changing cashier responsibility must not rewrite the historical order creation information.

The order must remain traceable to:

* Original employee
* New responsible employee where applicable
* Cash session
* Branch
* Device
* Order UUID

---

## 40. Cashier Comments

The cashier may be required to provide a comment after closing or when a discrepancy occurs according to the relevant business process.

Comments are part of the historical session record.

They must not replace structured financial values.

---

## 41. Offline Cash Sessions

Cash-session operations may continue offline only where the device has valid offline authorization and the operation is supported offline.

Offline mode must not bypass:

* Employee identity
* Cash-session responsibility
* Permission restrictions
* Closed-session rules
* Correction limits
* Audit requirements

Offline transactions must synchronize according to the Offline Operation and Synchronization document.

---

## 42. Reporting Period

A cash-session report is based on the actual session period:

**Opening Timestamp → Closing Timestamp**

A session that crosses midnight remains one cash session.

It must not automatically be divided into two sessions merely because the calendar date changed.

---

## 43. Monthly Reporting

Monthly reports must include relevant cash-session information.

The monthly report should contain, where applicable:

* Cash session
* Branch
* Cashier
* Opening information
* Closing information
* Expected cash
* Actual cash
* Difference
* Handover information
* Corrections
* Correction requests
* Approvals
* Rejections
* Reopening authorizations
* Audit history

---

## 44. Cash Session Audit

Important cash-session events must be auditable.

These include:

* Opening
* Closing
* Handover
* Cash acceptance
* Recalculation
* Discrepancy
* Comment
* Correction
* Correction request
* Approval
* Rejection
* Additional correction authorization

Audit records must preserve actor, time, affected session, and relevant values.

---

## 45. Security Principles

The cash-session model must prevent silent manipulation of cash history.

Important principles are:

1. A session has a clear responsible employee.
2. Closed sessions do not reopen normally.
3. Corrections are controlled.
4. Original values remain available.
5. Every correction has a reason.
6. Additional corrections require explicit authorization.
7. Handover uses the new employee's own identity.
8. Expected cash is hidden before physical cash entry.
9. Payment totals are derived from recorded transactions.
10. Offline mode cannot bypass cash controls.

---

## 46. Performance Requirements

Cashier operations must remain fast.

The system should not introduce unnecessary confirmation steps into ordinary POS work.

Security and audit processing should operate efficiently without requiring powerful hardware.

The cash-closing and handover workflow should remain understandable to ordinary restaurant employees.

---

## 47. Cash Session Business Rules Summary

| Area                | Rule                                        |
| ------------------- | ------------------------------------------- |
| Registers           | Normally one per branch                     |
| Opening             | Manual                                      |
| Closing             | Manual                                      |
| Overnight           | Session may remain open                     |
| Auto-close          | Not allowed                                 |
| Active sessions     | One per branch/register under current model |
| Responsible cashier | Explicitly identified                       |
| Payment types       | Cash and card at minimum                    |
| Actual cash         | Entered by cashier                          |
| Expected cash       | Hidden until actual cash is entered         |
| Difference          | Calculated automatically                    |
| Discrepancy         | Recount recommended                         |
| Explanation         | Required when relevant discrepancy remains  |
| Owner notification  | Required for relevant discrepancies         |
| Closed session      | Remains closed                              |
| Correction          | Authorized correction process only          |
| Initial corrections | Maximum 3                                   |
| Extra correction    | Exactly one per authorization               |
| Extra authorization | Owner/authorized Manager                    |
| Correction request  | Auditable                                   |
| Rejection           | Requires explanation                        |
| Handover            | New cashier authenticates and accepts       |
| Handover actions    | Confirm or Recalculate                      |
| Open orders         | Transfer automatically                      |
| Historical data     | Original values preserved                   |
| Offline             | Supported where authorized                  |
| Reporting period    | Opening to closing                          |
| Audit               | Required for important session events       |

---

## 48. Business Analysis Boundary

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

These decisions must be defined later in the Architecture, Database, Backend, Frontend, Security, and Operations documentation.

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
* `05_Database`
* `06_Backend`
* `07_Frontend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`

