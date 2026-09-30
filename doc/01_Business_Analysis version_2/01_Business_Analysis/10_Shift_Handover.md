# Shift Handover

**Document ID:** FF-BA-010
**Status:** Accepted
**Version:** 2.0
**Scope:** Cashier handover, cash-session transition, responsibility transfer, physical cash acceptance, open orders, confirmation, and handover history
**Parent Document:** `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`

---

## 1. Purpose

This document defines the business requirements for transferring operational responsibility from one cashier to another.

The handover process must provide:

* Clear responsibility boundaries
* Physical cash verification
* Individual employee accountability
* Continuity of open orders
* Transparent discrepancy handling
* Reliable handover history
* Controlled cash-session transitions
* Minimal disruption to restaurant operations
* Support for authorized offline operation

The handover process is directly connected to the cash-session lifecycle.

A cashier handover creates a clear boundary between the previous cashier's closed session and the new cashier's newly opened session.

---

## 2. Handover Model

Under the current business model, cashier handover is implemented through a cash-session transition.

The process is:

**Previous Cashier → Close Previous Cash Session → New Cashier Authenticates → Count/Accept Cash → Open New Cash Session**

The previous cashier's session becomes permanently closed.

The new cashier does not take ownership of the previous cash session.

Instead, the new cashier becomes responsible through a new cash session.

Therefore:

**Previous Session UUID ≠ New Session UUID**

The cash register itself remains the same.

---

## 3. Responsibility Boundary

The responsibility boundary is defined by the cash-session transition.

Before handover completion:

* The previous cashier remains responsible for the open session.
* The previous session remains open until successfully closed.
* The new cashier does not become responsible for the previous session.

After the previous session is closed and the new cashier opens a new session:

* The previous cashier remains historically responsible for the previous session.
* The new cashier becomes responsible for the new session.
* New cash-affecting operations belong to the new session.

This prevents responsibility from being transferred ambiguously inside one cash session.

---

## 4. Previous Cashier

The previous cashier is the employee responsible for the current open cash session.

The system must identify:

* Previous cashier
* Business
* Branch
* Cash register
* Previous cash session
* Device
* Session state

The previous cashier remains historically associated with the closed session after handover.

Closing the session does not remove the previous cashier's responsibility from historical records.

---

## 5. New Cashier

The new cashier must use their own employee account.

The new cashier must not use:

* The previous cashier's account
* The previous cashier's credentials
* The previous cashier's session identity

The system must verify the new cashier's authorization before allowing them to operate the new cash session.

The new cashier must have the required permissions and branch scope.

---

## 6. Authentication Requirement

The new cashier must authenticate through their own employee account.

The new cashier's authentication must be associated with:

* Employee
* Business
* Branch
* Cash register
* New cash session
* Device
* Timestamp

A device login alone is not sufficient to establish cashier responsibility.

Trusted-device status also does not replace employee authentication.

---

## 7. Handover Initiation

The handover begins while the previous cash session is still open.

The previous cashier must initiate or participate in the closing process according to the applicable permissions.

The system records that a cashier transition is in progress where required.

The previous session remains the active session until its closing process is completed.

The new cashier must not create a second active session on the same register while the previous session remains open.

---

## 8. Previous Cash Session Closing

The previous cashier must close the current cash session before the new cashier becomes responsible for the register.

The closing process follows the requirements in:

`01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`

The previous session records:

* Opening information
* Closing information
* Expected cash
* Actual cash
* Difference
* Payment totals
* Closing comments
* Responsible employee
* Closing timestamp
* Relevant device
* Corrections where applicable

Once closed, the previous session cannot be reopened as an active session.

---

## 9. Physical Cash Count

The physical cash count is performed by the cashier responsible for the relevant stage of the handover.

The new cashier physically counts the cash that will become the opening cash of the new session.

The new cashier enters the counted physical amount using their own authenticated account.

The system must not require the new cashier to manually calculate expected cash.

---

## 10. Expected Amount Protection

Before the physical cash amount is entered, the relevant expected amount must remain hidden where the business process requires an independent count.

The purpose is to prevent the expected amount from influencing the physical cash count.

After the actual cash amount is submitted, the system may display the reconciliation information.

This includes, where applicable:

* Expected cash
* Actual cash
* Difference
* Order count
* Payment totals
* Previous cashier information
* New cashier information
* Previous session information

---

## 11. Cash-Only Physical Entry

During cash handover/reconciliation, the cashier physically counts and enters **cash only**.

The system may display recorded payment totals for:

* Cash
* Card
* Debt
* Mixed payments

However, the cashier does not manually enter the card amount.

The card amount is derived from recorded transactions.

The same principle applies to other non-cash payment methods.

---

## 12. Handover Cash Result

After the actual physical cash amount is entered, the system displays the applicable reconciliation result.

At minimum, the result may include:

* Expected cash
* Actual cash
* Difference
* Relevant order count
* Cash payment total
* Card payment total
* Other payment totals where applicable
* Previous cashier
* New cashier
* Previous cash session
* New cash session

The result must remain historically traceable.

---

## 13. Handover Difference

The system calculates the difference between expected and actual cash.

The result may be:

* No difference
* Shortage
* Overage

The discrepancy must remain associated with the appropriate session and handover history.

A shortage from the previous session must remain associated with the previous session.

It must not automatically become a shortage belonging to the new cashier's session.

---

## 14. Handover Recount

If a discrepancy is identified, the applicable cashier may perform a recount according to the cash-session rules.

The recount must not silently erase the original entered amount.

The system must preserve the relevant values and state transitions.

Where a recount or recalculation occurs, the event must be auditable.

---

## 15. Confirmation Process

The handover process must have a clear confirmation state.

The previous cashier may receive a handover-related notification when the new cashier has entered the physical cash amount.

The notification provides the applicable confirmation actions defined by the business process.

The standard actions are:

**Confirm**

or

**Recalculate**

A separate `Reject` action is not part of the current business model.

---

## 16. Confirm Action

If the previous cashier selects **Confirm**, the applicable handover process is confirmed.

The system records:

* Previous cashier
* New cashier
* Previous cash session
* New cash session
* Cash register
* Physical cash result
* Confirmation timestamp
* Relevant devices
* Confirmation actor

Confirmation does not reopen or modify the previous cash session.

The previous session remains closed.

---

## 17. Recalculate Action

If the previous cashier selects **Recalculate**, the system performs the applicable reconciliation recalculation.

The recalculation must not erase the previous handover information.

The system must retain:

* Previous result
* Recalculation request
* Updated result
* Requesting employee
* Timestamp
* Related sessions
* Relevant values

After recalculation, the confirmation process continues according to the current workflow.

---

## 18. Responsibility Transfer

Responsibility transfers only after the previous session has been successfully closed and the new cashier has opened the new cash session.

Before completion:

* The previous cashier remains responsible for the previous session.
* The new cashier is not responsible for the previous session.
* No second active session may exist on the same register.

After completion:

* The previous cashier remains responsible historically for the previous session.
* The new cashier becomes responsible for the new session.
* New cash operations belong to the new session.

---

## 19. New Cash Session Opening

After the previous session is closed, the new cashier authenticates and opens a new cash session.

The new session records:

* Business
* Branch
* Cash register
* New cashier
* Device
* Opening timestamp
* Opening cash amount
* New session UUID

The opening cash amount is the physical amount entered by the new cashier.

The new session receives its own permanent identity.

---

## 20. Handover Completion

A completed cashier transition must allow the system to identify:

* Previous cashier
* Previous cash session
* Previous closing result
* New cashier
* New cash session
* New opening cash
* Cash register
* Branch
* Previous and new devices where relevant
* Handover time
* Relevant reconciliation result

The system must not merge the two sessions into one historical session.

---

## 21. Handover Rejection

The current business model does not use a separate `Reject` action.

The required confirmation actions are:

* Confirm
* Recalculate

If required confirmation is not completed, the transition remains incomplete according to the recorded process state.

The system must not incorrectly mark the new cashier as responsible before the required session transition has been completed.

---

## 22. Discrepancy After Handover

If the previous session closes with a remaining discrepancy:

* The discrepancy remains attached to the previous session.
* The previous cashier remains historically responsible for that discrepancy.
* The new cashier's new session is not automatically charged with the previous discrepancy.
* The applicable Owner notification must be generated.

The discrepancy follows the cash-session correction and reporting rules.

---

## 23. Discrepancy Responsibility

The system must distinguish:

**Previous Session Responsibility**

from:

**New Session Responsibility**

A new cashier physically counting cash does not automatically become responsible for a discrepancy originating from the previous session.

The history must clearly show:

* Who operated the previous session
* Who closed it
* Who counted the cash
* What amount was expected
* What amount was entered
* What difference existed
* Who opened the new session
* What opening amount was recorded

---

## 24. Open Orders

Open orders must not disappear when cashier responsibility changes.

Orders created before the handover remain operationally available.

The new cashier may continue processing those orders according to their permissions.

The order UUID remains unchanged.

The handover must not:

* Delete the order
* Recreate the order
* Reset the order lifecycle
* Remove order history
* Recalculate historical actions merely because the cashier changed

---

## 25. Open Orders and Cash Sessions

An order may have operational activity spanning a cashier transition.

The system must preserve the distinction between:

* Original order session/context
* Previous cashier actions
* New cashier actions
* New payment actions
* New modifications

Where applicable, later payment or order actions are associated with the new active cash session.

The original order creation event remains unchanged.

---

## 26. Order History During Handover

If the new cashier modifies an existing order after handover, the modification must be associated with:

* New cashier
* New device
* New active cash session
* Timestamp
* Order UUID

The original order creation and earlier modifications remain associated with their original employees and sessions.

This allows the system to reconstruct activity across the cashier transition.

---

## 27. Payment History During Handover

Payments recorded before the transition remain associated with the previous cash session.

Payments recorded after the transition belong to the new active cash session.

The system must preserve the employee responsible for each payment.

The handover must not modify previously recorded payment amounts.

---

## 28. Inventory During Handover

If the new cashier continues working with an existing order, inventory behavior follows the normal order and inventory rules.

The handover itself does not:

* Reset inventory consumption
* Recreate an order
* Duplicate inventory deductions
* Reverse inventory automatically

Any new inventory-affecting action is attributed to the employee performing that action.

---

## 29. Multiple Cashier Transitions

A branch may have multiple cashier transitions over time.

For example:

**Cashier A / Session A → Cashier B / Session B → Cashier C / Session C**

Each transition must preserve:

* Previous cashier
* Previous session
* New cashier
* New session
* Cash result
* Opening/closing information
* Relevant order/payment activity

The system must not collapse the history into only the final cashier.

---

## 30. Cash Register Continuity

Although each cashier transition creates a new cash session, the physical cash register remains the same under the current one-register-per-branch model.

Therefore:

**Cash Register Identity remains stable**

while:

**Cash Session Identity changes**

and:

**Responsible Cashier changes**

This preserves both physical register continuity and financial responsibility boundaries.

---

## 31. Offline Handover

Cashier transition may be performed offline only when:

* The device is trusted.
* The employee has valid offline authorization.
* The required permissions are available offline.
* The operation is supported by the offline workflow.

Offline operation must not bypass:

* Employee identity
* Branch scope
* Session lifecycle
* Cashier responsibility
* Permission restrictions
* Closed-session rules
* Audit requirements
* Subscription restrictions

A new active session must not be created offline if doing so would violate the server-side session rules.

---

## 32. Offline Handover Synchronization

When offline handover/session-transition events synchronize:

1. The device identifies the relevant previous session.
2. The closing event is submitted where applicable.
3. The new session/opening event is submitted.
4. The server validates the business.
5. The server validates the branch.
6. The server validates the cash register.
7. Employee authorization is validated.
8. Session state is validated.
9. UUID/idempotency checks are performed.
10. Events are accepted or rejected.
11. Synchronization status is recorded.
12. Current authoritative server state is returned to the device.

Retrying the same event must not create duplicate sessions, duplicate closing events, or duplicate handover records.

---

## 33. Multiple Devices

The new cashier may use another trusted device if permitted by the business configuration.

Device identity must remain part of the session and handover history.

A trusted device does not replace employee authentication.

The system must preserve which device was used for:

* Previous session closing
* Physical cash entry
* New session opening
* Subsequent POS operations

---

## 34. Handover Audit

Important handover events must be auditable.

These include:

* Handover initiation
* Previous session closing
* Physical cash entry
* Expected amount reveal
* Difference calculation
* Recount
* Recalculation
* Confirmation
* New session opening
* New cashier authentication
* Handover completion
* Synchronization events where applicable

Audit records must retain, where applicable:

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

Audit history must not be silently overwritten.

---

## 35. Handover Notifications

Relevant notifications may include:

* Handover started
* Previous session closing required
* Physical cash entry completed
* Reconciliation result available
* Confirmation required
* Recalculation requested
* Previous-session discrepancy detected
* New session opened
* Handover completed
* Synchronization failure

Notifications must reflect the actual current state.

---

## 36. Handover Failure and Interruption

The system must safely handle interruptions such as:

* Application restart
* Network loss
* Device restart
* Synchronization failure
* Offline queue interruption

A partially completed transition must not result in an ambiguous permanent responsibility state.

The system must retain the last valid state.

After restart or reconnection, the system must determine whether:

* The previous session is still open.
* The previous session is closed.
* The new session has been successfully opened.
* A synchronization event is pending.
* A synchronization event was already accepted.

The same transition must not be executed twice.

---

## 37. Session Closing After Handover

The new cashier may later close the new cash session according to the normal cash-session closing process.

The closing process must identify:

* New session
* New cashier
* Opening cash
* Expected cash
* Actual cash
* Difference
* Relevant payments
* Closing timestamp
* Comments
* Corrections where applicable

The previous cashier remains associated with the previous closed session.

---

## 38. Handover History

Every cashier transition must remain separately identifiable.

For example:

**Cashier A → Session A → Cashier B → Session B → Cashier C → Session C**

must preserve every session and transition.

The system must not replace the previous cashier with the latest cashier in historical records.

---

## 39. Reporting

Handover information must be available in relevant reports.

Authorized users should be able to understand:

* Session started by whom
* Previous cashier
* Previous session
* Previous closing result
* Physical cash counted
* Difference
* New cashier
* New session
* New opening amount
* Transition time
* Recalculation events
* Confirmation events
* Relevant discrepancies
* Subsequent closing result

Handover information must also remain available through audit history.

---

## 40. Historical Integrity

A cashier transition must never rewrite historical information.

The system must preserve the distinction between:

* Previous session
* Previous session closing
* Handover/reconciliation process
* New session opening
* New cashier operations

Historical order, payment, inventory, and cash events must retain their original identities and timestamps.

---

## 41. Performance Requirements

The handover process must remain fast enough for normal restaurant operations.

The system should avoid unnecessary steps that do not contribute to cash accountability.

The workflow should be understandable to ordinary cashiers.

Security, audit, and synchronization mechanisms should not noticeably reduce normal POS performance.

The current one-register/one-primary-POS configuration must remain practical on ordinary POS hardware.

---

## 42. Handover Business Rules Summary

| Area                       | Rule                                                  |
| -------------------------- | ----------------------------------------------------- |
| Handover model             | Cash-session transition                               |
| Previous session           | Must be closed                                        |
| New session                | Created for the new cashier                           |
| Session UUID               | Changes after handover                                |
| Cash register UUID         | Remains the same                                      |
| Previous cashier           | Remains historically responsible for previous session |
| New cashier                | Becomes responsible for new session                   |
| Authentication             | New cashier must use own account                      |
| Physical cash count        | Required                                              |
| Cash entry                 | Cashier enters physical cash only                     |
| Expected cash              | Hidden before actual cash entry                       |
| Reconciliation             | Revealed after actual cash entry                      |
| Payment totals             | Derived from recorded transactions                    |
| Card entry                 | Not manually entered during cash count                |
| Difference                 | Calculated automatically                              |
| Recount                    | Supported when discrepancy requires it                |
| Confirm                    | Supported                                             |
| Recalculate                | Supported                                             |
| Reject                     | Not part of current model                             |
| Open orders                | Must remain available                                 |
| Order UUID                 | Unchanged                                             |
| Previous payment history   | Preserved                                             |
| New payment activity       | Associated with new session                           |
| Inventory                  | Not reset or duplicated                               |
| Multiple handovers         | Supported                                             |
| Offline                    | Supported where authorized                            |
| Audit                      | Required                                              |
| New cashier responsibility | Starts with new session                               |
| Previous session           | Never reopened as active                              |
| Historical data            | Original values preserved                             |

---

## 43. Business Analysis Boundary

This document defines the business requirements for cashier handover and cash-session transition.

The following remain implementation decisions:

* Handover UI
* Cash-count UI
* Notification delivery mechanism
* Local handover storage
* Offline transition storage
* Synchronization protocol
* Cash hardware integration
* Session locking implementation
* Real-time communication mechanism
* Database schema
* Exact audit-log implementation
* API contracts
* Concurrency implementation
* Device coordination

These decisions must be defined later in the Architecture, Database, Backend, Frontend, Security, API, Testing, and Operations documentation.

---

## Related Documents

* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `01_Business_Analysis/08_POS_and_Order_Management.md`
* `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `01_Business_Analysis/16_Reports_and_Dashboards.md`
* `01_Business_Analysis/17_Notifications_and_Alerts.md`
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


