# Shift Handover

**Document ID:** FF-BA-010
**Status:** Accepted
**Version:** 1.0
**Scope:** Cashier handover, responsibility transfer, cash acceptance, open orders, confirmation, and handover history
**Parent Document:** `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`

---

## 1. Purpose

This document defines the business requirements for transferring responsibility for an active cash register from one cashier to another.

The handover process must provide:

* Clear responsibility transfer
* Physical cash verification
* Individual employee accountability
* Continuity of open orders
* Transparent discrepancy handling
* Reliable handover history
* Minimal disruption to restaurant operations

Shift handover is an operational process within a cash session.

It is not a separate replacement for the cash-session model.

---

## 2. Handover Model

A handover occurs when responsibility for an active cash register is transferred from one cashier to another without closing the cash session.

The basic process is:

**Current Cashier → Handover → New Cashier Accepts → Responsibility Transfers**

The existing cash session remains open.

A new cash session is not created solely because the cashier changes.

---

## 3. Current Cashier

The current cashier is the employee who is responsible for the active cash register before the handover.

The system must be able to identify:

* Current cashier
* Branch
* Cash register
* Cash session
* Device
* Handover state

The current cashier's identity must remain in historical records after responsibility is transferred.

---

## 4. New Cashier

The new cashier must use their own employee account.

The new cashier must not use the previous cashier's account to accept responsibility.

The system must verify the new cashier's authorization before allowing the handover to proceed.

The new cashier must have the permissions required to operate the relevant branch and cash register.

---

## 5. Authentication Requirement

The new cashier must authenticate through their own account before accepting the cash register.

The system must associate the acceptance action with:

* New cashier
* Business
* Branch
* Cash register
* Cash session
* Device
* Timestamp

A simple device login is not sufficient to transfer cash responsibility.

---

## 6. Handover Initiation

The handover begins while the cash session is still open.

The current cashier or another authorized employee may initiate the handover according to the applicable permissions.

The system records the beginning of the handover process.

The active cash session remains open during the process.

---

## 7. Order Processing During Handover

The system should control order processing during the critical cash-acceptance stage.

The new cashier must accept responsibility before becoming the responsible cashier for new operations.

Open orders must not be deleted, cancelled, or recreated merely because a handover is occurring.

---

## 8. Open Orders

All currently open orders remain part of the same cash session.

After successful handover, open orders automatically become available to the new cashier.

The new cashier may continue working with them according to their permissions.

The original order UUID remains unchanged.

---

## 9. Order History During Handover

The system must preserve the history of who originally created or modified an order.

Transferring cash responsibility must not rewrite historical order actions.

Where the new cashier subsequently modifies an existing order, the modification must be associated with the new cashier.

This allows the system to distinguish:

* Original order activity
* Activity performed before handover
* Activity performed after handover

---

## 10. Physical Cash Count

The new cashier must physically count the cash before accepting responsibility.

The new cashier enters the counted physical cash amount into the system.

The system must not require the new cashier to calculate the expected amount manually.

---

## 11. Expected Amount Protection

Before the new cashier enters the physical cash amount, the expected amount must remain hidden.

This ensures that the physical cash count is performed independently.

After the new cashier submits the actual amount, the system displays the reconciliation result.

The result includes:

* Expected cash
* Actual cash
* Difference
* Relevant payment information
* Order count
* Cash-session information

---

## 12. Cash Difference During Handover

The system calculates the difference between expected and actual cash.

The result may be:

* No difference
* Shortage
* Overage

The result must remain associated with the handover and cash-session history.

A discrepancy must not be silently ignored.

---

## 13. Handover Recount

If the new cashier identifies a discrepancy or believes the entered amount is incorrect, the relevant cash may be recounted.

The system must preserve the previous information rather than silently replacing it.

Where a recalculation occurs, the recalculation event must be traceable.

---

## 14. Previous Cashier Notification

After the new cashier enters the physical cash amount, the previous cashier receives a handover notification.

The notification must provide exactly two required actions:

**Confirm**

or

**Recalculate**

The previous cashier must select one of these actions.

---

## 15. Confirm Action

If the previous cashier selects **Confirm**, the handover is confirmed.

The system records:

* Previous cashier
* New cashier
* Cash session
* Cash register
* Confirmed cash result
* Confirmation time
* Relevant device information

Responsibility then transfers to the new cashier.

---

## 16. Recalculate Action

If the previous cashier selects **Recalculate**, the system recalculates the relevant cash-session values.

The recalculation must not erase the previous handover information.

The system must retain the relevant history of:

* Previous calculation
* Recalculation request
* Updated calculation
* Actors
* Times

After recalculation, the confirmation process must continue.

---

## 17. Responsibility Transfer

Responsibility transfers only after the required handover process has been successfully completed.

Before successful acceptance:

* The new cashier must not be treated as the responsible cashier.
* The previous cashier remains identifiable as the responsible cashier.
* The cash session remains open.

After successful acceptance:

* The new cashier becomes responsible.
* The previous cashier is no longer responsible for new cash-register activity.
* The handover becomes part of the session history.

---

## 18. Handover Completion

A completed handover must record at minimum:

* Cash session
* Cash register
* Previous cashier
* New cashier
* Previous device where relevant
* New device where relevant
* Actual counted cash
* Expected cash
* Difference
* Confirmation result
* Confirmation time

The handover record must remain associated with the cash session.

---

## 19. Handover Rejection

The current business model does not use a separate "Reject" button in the previous cashier's handover notification.

The required actions are limited to:

* Confirm
* Recalculate

If the previous cashier does not confirm, the handover must not be considered successfully completed.

The system may keep the process pending until the required action is completed according to operational rules.

---

## 20. Discrepancy After Handover

If the handover produces a remaining discrepancy, the responsible process follows the cash-session discrepancy rules.

The relevant cashier may be required to provide an explanation.

The Owner must be informed according to the notification rules.

The discrepancy remains part of the cash-session and handover history.

---

## 21. Responsibility for Discrepancy

The system must preserve which cashier was responsible before the handover and which cashier became responsible afterward.

A discrepancy must not automatically be attributed to the new cashier merely because the new cashier counted the cash.

The historical responsibility and handover result must be available to authorized users.

---

## 22. Handover and Cash Session Continuity

A successful handover does not close the cash session.

The same cash session continues.

Therefore:

**Cash Session UUID remains unchanged**

while:

**Responsible Cashier changes**

This allows the entire operating period to remain one coherent financial session.

---

## 23. Handover and Orders

Orders created before handover remain part of the same cash session.

Orders created after handover are associated with the new responsible cashier.

Existing open orders may be completed by the new cashier.

The order history must retain the employee responsible for each individual action.

---

## 24. Handover and Payments

Payment transactions before and after handover remain part of the same cash session.

The payment records must preserve the employee responsible for the relevant payment operation.

The handover itself must not alter previously recorded payment amounts.

---

## 25. Handover and Inventory

If the new cashier continues processing an existing order after handover, inventory effects must follow the same order and recipe rules.

The handover does not reset or recreate inventory consumption.

Any new inventory-affecting action must be associated with the employee performing that action.

---

## 26. Offline Handover

Handover may be performed offline only where the device and employees have valid offline authorization and the handover operation is supported offline.

Offline handover must continue to respect:

* Employee identity
* Permissions
* Cash-session state
* Device authorization
* Audit requirements

The handover must synchronize with the server after connectivity is restored.

---

## 27. Handover Synchronization

When an offline handover synchronizes:

1. The device identifies the cash session.
2. The handover event is submitted.
3. The server validates the business and branch.
4. Employee authorization is validated.
5. Transaction identity is checked.
6. The handover is accepted or rejected.
7. Synchronization status is updated.
8. Relevant current server state is returned to the device.

The system must not create a second handover event if the same event is retried.

---

## 28. Multiple Devices

A cashier may operate from an authorized device.

The new cashier may use another authorized device if permitted by the business configuration.

The device identity must remain part of the handover history.

A trusted device does not replace employee authentication.

---

## 29. Handover Audit

Every important handover action must be auditable.

The system must retain:

* Initiation
* Previous cashier
* New cashier
* Cash amount entered
* Expected amount revealed
* Recalculation
* Confirmation
* Completion
* Timestamp
* Device
* Cash session
* Branch

Audit records must not be silently overwritten.

---

## 30. Handover Notifications

Relevant employees should receive notifications for important handover events.

These may include:

* Handover started
* New cashier entered physical cash
* Confirmation required
* Recalculation requested
* Handover completed
* Discrepancy detected

Notifications must reflect the actual state of the handover.

---

## 31. Handover Failure

The system must handle interruptions such as:

* Application restart
* Network loss
* Device restart
* Synchronization failure

A partially completed handover must not result in an ambiguous permanent responsibility state.

The system must retain the last valid state and allow the handover process to continue or be safely resolved according to the recorded state.

---

## 32. Handover and Session Closing

A handover does not automatically close the cash session.

The new cashier may later close the cash session according to normal closing rules.

At final closing, the system must be able to identify:

* Who opened the session
* Previous cashiers
* Handover events
* Current/final responsible cashier
* Closing cashier
* All relevant cash results

---

## 33. Handover History

A cash session may contain multiple handovers.

Each handover must remain separately identifiable.

For example:

**Cashier A → Cashier B → Cashier C**

must preserve all three responsibility states and both transfer events.

The system must not collapse them into only the final cashier.

---

## 34. Reporting

Handover information must be available in relevant reports.

Reports should allow authorized users to understand:

* Which cashier started the session
* Which handovers occurred
* Who accepted responsibility
* When each handover occurred
* Cash counted at handover
* Differences
* Confirmation/recalculation events
* Final cashier
* Closing result

Handover information must also remain available in audit history.

---

## 35. Performance Requirements

The handover process should be fast enough for normal restaurant operations.

The system must avoid unnecessary steps that do not contribute to cash accountability.

The physical counting and confirmation process should remain understandable to ordinary cashiers.

Security and audit processing should not noticeably reduce POS performance.

---

## 36. Handover Business Rules Summary

| Area                     | Rule                                                 |
| ------------------------ | ---------------------------------------------------- |
| Handover type            | Transfer responsibility within the same cash session |
| New cash session         | Not created by handover                              |
| New cashier              | Must use own account                                 |
| Authentication           | Required                                             |
| Physical cash count      | Required                                             |
| Expected cash            | Hidden before actual entry                           |
| Difference               | Calculated after actual entry                        |
| Previous cashier actions | Confirm or Recalculate                               |
| Reject action            | Not part of the current model                        |
| Responsibility transfer  | Only after successful completion                     |
| Open orders              | Transfer automatically                               |
| Order UUID               | Remains unchanged                                    |
| Cash session UUID        | Remains unchanged                                    |
| Previous history         | Preserved                                            |
| New actions              | Attributed to new cashier                            |
| Discrepancy              | Follows cash-session discrepancy rules               |
| Multiple handovers       | Supported                                            |
| Offline                  | Supported where authorized                           |
| Audit                    | Required                                             |
| Session closing          | Separate from handover                               |

---

## 37. Business Analysis Boundary

This document defines the business behavior of cashier handover.

The following remain implementation decisions:

* Handover UI
* Notification delivery mechanism
* Local handover storage
* Synchronization protocol
* Cash hardware integration
* Session locking implementation
* Real-time communication mechanism
* Database schema
* Exact audit-log implementation

These decisions must be defined later in the Architecture, Database, Backend, Frontend, Security, and Operations documentation.

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
* `05_Database`
* `06_Backend`
* `07_Frontend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`

