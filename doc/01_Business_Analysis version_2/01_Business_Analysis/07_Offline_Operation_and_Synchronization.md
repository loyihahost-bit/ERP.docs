# Offline Operation and Synchronization

**Document ID:** FF-BA-007
**Status:** Accepted
**Version:** 2.0
**Scope:** Offline operation, local data, transaction processing, synchronization, conflict handling, and offline business continuity
**Parent Document:** `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`

---

## 1. Purpose

This document defines how FastFood ERP operates when a branch temporarily loses internet connectivity.

The system must allow a branch to continue essential restaurant operations during temporary network interruptions while preserving:

* Data integrity
* Employee accountability
* Business and branch isolation
* Permission enforcement
* Subscription restrictions
* Transaction uniqueness
* Inventory integrity
* Cash-session integrity
* Auditability
* Reliable synchronization
* Historical integrity

Offline operation is a business-continuity capability, not a separate version of the ERP.

The offline system must follow the same business rules as the online system as closely as possible using the latest valid locally authorized state.

---

## 2. Offline-First Principle

Temporary internet loss must not unnecessarily stop normal restaurant operations.

A previously registered and trusted device may continue supported branch operations using:

* Locally synchronized business data
* Locally synchronized branch data
* Valid employee authorization
* Valid offline authorization
* Local inventory state
* Current cash-session state
* Local configuration required for supported operations

When connectivity is restored, the device must synchronize automatically and return to normal online operation.

Users must not be required to recreate orders or manually enter the same transactions again merely because the network was temporarily unavailable.

Offline operation must never intentionally bypass:

* Permissions
* Branch scope
* Business scope
* Subscription restrictions
* Inventory rules
* Cash-session rules
* Order rules
* Audit requirements
* Security requirements

---

## 3. Conditions for Offline Operation

Offline operation is available only when the device has previously:

1. Connected to the server.
2. Been registered.
3. Been trusted.
4. Received valid offline authorization.
5. Obtained required business and branch data.
6. Obtained valid employee authorization for supported offline operations.

An unknown or newly introduced device must not begin ERP operation for the first time while offline.

A new device must first connect online, complete registration and verification, and become trusted.

Trusted-device status does not automatically grant business permissions.

---

## 4. Offline Authorization

Offline authorization must be:

* Cryptographically protected
* Time-bounded
* Associated with the trusted device
* Associated with the employee identity
* Associated with the Business
* Associated with the authorized Branch scope
* Associated with the applicable permission state
* Associated with the applicable subscription state
* Protected against replay
* Protected against unauthorized modification

Offline authorization must have an explicit validity boundary.

The exact authorization duration is an implementation decision and must be defined later in Security and Architecture documentation.

The device must detect relevant clock rollback or suspicious time manipulation.

A device must not gain additional authorization merely because it is offline.

---

## 5. Offline Scope

Offline mode is intended primarily to preserve essential branch operations.

Supported offline operations may include:

* Creating orders
* Saving Draft orders locally
* Accepting valid orders
* Modifying permitted Accepted orders
* Applying permitted discounts
* Recording supported payments
* Recording supported debt information
* Performing supported cash-session operations
* Performing permitted shift handover operations
* Recording permitted inventory operations
* Printing supported kitchen and customer documents
* Recording audit information
* Viewing required synchronized data
* Recording permitted cancellations
* Recording supported corrections
* Continuing supported POS workflows

Operations that fundamentally require current server information may remain unavailable until connectivity is restored.

The exact technical list of offline-capable functions is finalized in System Analysis, Architecture, Security, and implementation documentation.

---

## 6. Locally Available Data

Before going offline, the device must have the data required for supported operations.

Depending on device scope, this may include:

* Active menu items
* Product information
* Product categories
* Approved recipe information
* Set definitions
* Effective pricing
* Branch price overrides
* Applicable discount rules
* Relevant branch inventory state
* Employee authorization information
* Branch permissions
* Cash-register information
* Current cash-session information
* Table and hall information
* Required business configuration
* Device authorization
* Subscription authorization state
* Relevant reference data

The system must not assume that all historical or business-wide data must be stored locally.

Only data required for the device's authorized offline scope should be synchronized.

---

## 7. Local Data Protection

Offline business data must be protected against unauthorized access.

Locally stored business data must not be kept as openly readable files.

Sensitive local data must use appropriate encryption and secure credential handling.

The system must protect against:

* Direct local database manipulation
* Unauthorized copying
* Unauthorized modification of queued transactions
* Unauthorized access after device compromise
* Unauthorized reuse of offline authorization

If a device is lost or stolen, locally stored business data must not become easily accessible merely by accessing device storage.

The exact encryption technology belongs to Security and Architecture documentation.

---

## 8. Transaction Identity

Every transaction created offline must use the existing transaction UUID model.

The system must **not** introduce a separate Client Transaction ID.

The transaction UUID:

* Is generated before synchronization
* Remains stable throughout the transaction lifecycle
* Is used during synchronization
* Is used for duplicate detection
* Remains the permanent transaction identity

The same UUID must be used when the transaction is submitted to the server.

The server must use this identity to determine whether the transaction has already been processed.

---

## 9. Transaction Context

Offline transactions must retain sufficient context to prevent cross-business, cross-branch, employee, device, or cash-session mixing.

Important records must retain, where applicable:

* Transaction UUID
* Business UUID
* Branch UUID
* Employee UUID
* Device UUID
* Cash Register UUID
* Cash Session UUID
* Creation timestamp
* Relevant transaction state
* Synchronization state
* Original local creation context
* Relevant parent transaction UUID
* Audit context

The exact database structure belongs to Database and Architecture documentation.

---

## 10. Offline Order Creation

When a cashier creates an order while offline:

1. The employee is authenticated locally.
2. The device authorization is checked.
3. The employee's offline permissions are checked.
4. The correct Business and Branch context is established.
5. The order receives its UUID.
6. The order receives its customer-facing order number according to cash-session rules.
7. The responsible employee and device are recorded.
8. Applicable local business rules are evaluated.
9. The order is stored securely.
10. The order becomes available for supported local restaurant operations.
11. The transaction is placed into the synchronization queue.

The cashier must not need to recreate the order after connectivity returns.

---

## 11. Offline Order Lifecycle

The business order lifecycle remains:

**Draft → Accepted → Preparing → Ready → Served**

There is no `Completed` state.

### Draft

A Draft order:

* May be created offline.
* Is autosaved locally.
* Does not notify the kitchen.
* Does not deduct inventory.
* Does not occupy the table.
* May remain Draft until validly saved/accepted.

### Accepted

When a Draft is saved/accepted:

1. Inventory availability is checked.
2. Required inventory deduction is performed atomically.
3. The order becomes Accepted.
4. The table becomes occupied where applicable.
5. Kitchen notification/printing is initiated.
6. The transaction enters the synchronization queue.

If inventory is insufficient, the save/accept operation must fail as one transaction.

The system must not partially accept the order.

---

## 12. Offline Inventory Validation

Offline inventory must use the latest valid inventory state available on the device.

The no-negative-stock rule remains active offline.

If local inventory indicates insufficient stock, the relevant operation must be blocked.

The device must not intentionally allow negative inventory simply because it is offline.

However, multiple offline devices may have different local inventory states.

Therefore, local acceptance is not a replacement for server-side validation.

When synchronization occurs, the server must validate the resulting inventory transaction against authoritative inventory state.

---

## 13. Atomic Order Acceptance and Inventory Deduction

Order acceptance and inventory deduction must be treated as one business transaction.

For an Accepted order:

* Order acceptance must succeed together with the required inventory deduction.
* Inventory deduction must not be duplicated during synchronization.
* A failed synchronization retry must not deduct inventory again.
* A rejected synchronization must not silently create a second order or second inventory event.

The server must use the transaction UUID and related business transaction identity to guarantee idempotent processing.

---

## 14. Offline Order Modification

Permitted Accepted orders may be modified while offline.

Modification must follow the same business rules as online operation.

Inventory is reconciled using the difference between the previous and new state.

Examples:

* `30g → 0g` returns 30g to inventory.
* `30g → 50g` deducts an additional 20g.
* `30g → 20g` returns 10g.

If the additional inventory required by a modification is insufficient:

* The entire modification is rejected locally.
* The previous order remains unchanged.
* No partial modification is saved.

The system must synchronize the modification using stable transaction/event identity.

---

## 15. Offline Unit-Level Customization

Offline POS must support the same unit-level customization rules as online POS where the required data is available.

Each product unit may have its own:

* Removed ingredients
* Increased ingredients
* Added extras
* Other supported customization

Example:

A quantity of two may contain:

* Unit 1: normal
* Unit 2: customized

A quantity of three may contain three different customization states.

The system does not require an `Apply to all` action.

Inventory, cost, price, and kitchen instructions must be calculated according to each unit's actual state.

The base recipe itself must not be modified by a one-time order customization.

---

## 16. Offline Modification After Kitchen Ticket

If an Accepted order is modified after a kitchen ticket has already been generated:

* The old kitchen ticket is marked `CANCELLED` or `UPDATED`.
* A new kitchen ticket is created.
* The same order UUID and customer-facing order number remain associated with the order.
* Inventory is reconciled by delta.
* Audit history records the change.

The new kitchen ticket represents the current order state.

It does not need to display the full difference from the previous ticket.

The complete historical change remains available through audit/change history.

---

## 17. Offline Kitchen Printer Failure

Printer failure must not roll back a valid ERP transaction.

For example:

1. Order is accepted.
2. Inventory is deducted.
3. Kitchen print job is created.
4. Printer is unavailable.
5. ERP transaction remains valid.
6. Print job enters a retryable state.

Supported conceptual printer states include:

* Pending
* Failed
* Retrying
* Printed

The system must retain:

* Print job identity
* Related order/event identity
* Printer identity
* Attempt history
* Failure information
* Retry information

A retry must not create a duplicate ERP order or duplicate inventory deduction.

Persistent printer failures must become visible to authorized users according to notification rules.

---

## 18. Offline Cancellation

Cancellation is separate from refund.

Where cancellation permission exists, a user may initiate cancellation while offline if the required authorization and data are locally available.

Cancellation must:

* Preserve the original order
* Create a separate cancellation event
* Require a reason
* Require a comment where required by the business rule
* Notify/update kitchen state where applicable
* Preserve audit history

Inventory return is determined per item.

The cancellation interface uses a per-item `Return Inventory` decision.

The default behavior for eligible non-Served items is return enabled.

A Served item can never return inventory.

Offline cancellation must not silently modify historical order records.

---

## 19. Offline Refund

Refund and cancellation remain separate business operations.

Refund may be performed only by authorized users.

Current supported refund methods are:

* Cash
* Card

Refund requires:

* Permission
* Reason
* Comment
* Original payment/order context

Refund does not return inventory.

The current refund process is manual.

Offline refund availability depends on the locally authorized capabilities and required locally available transaction data.

---

## 20. Offline Payment and Debt

Supported payment methods are:

* Cash
* Card
* Debt
* Mixed

Mixed payment may combine supported payment methods.

Card payment is currently recorded manually.

Future external payment-provider integrations must not be assumed to work offline.

Debt orders require:

* Customer name
* Customer phone

Address and comment may be stored where applicable.

Multiple debt orders may belong to the same customer.

Partial debt repayment must preserve historical debt records.

Offline payment events must retain:

* Order UUID
* Payment UUID
* Employee
* Branch
* Cash session where applicable
* Device
* Amount
* Payment method
* Timestamp

Duplicate synchronization must never create duplicate payments.

---

## 21. Offline Cash Sessions

Offline operation must follow the currently authorized cash-session state.

The device must not bypass cash-session rules.

Current business rules include:

* One cash register per branch.
* One primary POS/cashier computer is the normal configuration.
* Cash sessions are opened manually.
* Cash sessions are closed manually.
* A session may remain open overnight.
* A cashier change requires the old cashier to close the current session and the new cashier to open a new session.
* A closed session never becomes open again.
* Corrections are performed through the correction workflow.

Offline mode must not:

* Reopen a closed session
* Change session ownership without the required process
* Bypass cashier authentication
* Bypass handover requirements
* Bypass correction limits

Cash-session identity must remain associated with relevant transactions.

---

## 22. Offline Shift Handover

Where supported by the current cash-session state, shift handover may continue offline.

The required process remains:

1. Current cashier closes the session.
2. Cash is counted and entered.
3. Required discrepancy information is recorded.
4. The new cashier authenticates with their own employee account.
5. The new cashier opens a new cash session.

The system must preserve both:

* Previous cashier/session responsibility
* New cashier/session responsibility

Offline synchronization must not merge two distinct cash sessions into one.

---

## 23. Offline Cash Corrections

Cash-session correction rules remain valid offline only where the authorized correction operation is supported by the current offline authorization.

A closed session remains closed.

Corrections must:

* Preserve original values
* Store the new value
* Store the difference
* Require a reason
* Preserve employee identity
* Preserve timestamp and device identity
* Create audit history

The existing correction limit remains applicable.

If the correction limit is exceeded, the additional authorization required by the business rule must be obtained.

Offline mode must not bypass that authorization.

---

## 24. Offline Permissions

Offline operation uses the employee authorization state contained in the valid offline authorization.

A trusted device does not automatically grant unrestricted permissions.

The employee must still operate according to:

* Role permissions
* Employee overrides
* Branch scope
* Business scope
* Subscription entitlement
* Action-level permissions

Permission changes made on the server while the device is offline may not immediately reach the device.

After reconnection, server state becomes authoritative.

---

## 25. Employee Deactivation During Offline Period

If an employee is deactivated while a device is offline, the device may not immediately know about the change.

The offline authorization remains bounded by its validity and security rules.

When the device reconnects:

1. Employee authorization is revalidated.
2. Current employee status is obtained from the server.
3. Any deactivation becomes authoritative.
4. Future operations using the deactivated employee are blocked.
5. Previously created valid transactions remain historically attributable to that employee.

Historical identity must not be rewritten.

---

## 26. Offline Subscription Restrictions

Offline mode must not permanently bypass subscription restrictions.

If the subscription expires or becomes restricted while the device is offline, the locally issued offline authorization may remain valid only until its defined authorization boundary.

After the authorization boundary or reconnection, current subscription state must be enforced.

Subscription expiry rules remain:

* Modifying functions become blocked.
* Existing data remains viewable.
* Historical information remains accessible where permitted.
* Excel export remains available where permitted.
* Permanent deletion occurs only after the defined retention period.

The exact offline subscription grace behavior belongs to Security and Architecture documentation, but it must not create an indefinite offline bypass.

---

## 27. Offline Recipe and Menu Configuration

Offline POS must use the latest synchronized configuration available to the device.

This may include:

* Product activation state
* Product category
* Approved recipe version
* Set composition
* Selling price
* Branch price override
* Discount rules
* Equipment-related availability
* Customization rules

A product becoming inactive on the server while a device is offline may not immediately be reflected locally.

After synchronization, the current server configuration becomes authoritative.

Historical orders must not be recalculated because of later configuration changes.

---

## 28. Recipe and Set Effective Sessions

Recipe and Set configuration changes follow cash-session effectiveness rules.

A newly approved recipe becomes effective from the applicable next cash session.

A changed Set configuration becomes effective from the applicable next cash session.

If a device was offline during the configuration change:

* It may temporarily operate using the last valid synchronized configuration.
* The new configuration must be synchronized before it becomes authoritative on that device.
* Historical orders must continue using their original configuration snapshot.
* The server must prevent invalid historical recalculation.

---

## 29. Offline Audit Information

Every important offline action must be recorded locally with enough information to reconstruct what happened.

Important audit information includes:

* Employee identity
* Device identity
* Business identity
* Branch identity
* Transaction identity
* Cash Register identity where applicable
* Cash Session identity where applicable
* Timestamp
* Action type
* Previous values where applicable
* New values where applicable
* Reason/comment where applicable
* Synchronization state

Audit information must not disappear merely because synchronization temporarily fails.

Synchronization attempts and technical retry events may be recorded separately from business events.

---

## 30. Synchronization Queue

Transactions created or changed while offline must enter a local synchronization queue.

Each queued item must have a clear synchronization state.

Conceptual states include:

* Pending
* Sending
* Accepted
* Rejected
* Requires Review

Technical implementation may use a different state model, but the system must always be able to determine:

* Whether the transaction was submitted
* Whether the server accepted it
* Whether it was rejected
* Whether it requires attention
* Whether it is safe to retry

---

## 31. Automatic Synchronization

When connectivity returns, synchronization should begin automatically.

The user should not normally need to manually resend every transaction.

The preferred process is:

1. Detect connectivity.
2. Establish secure server connection.
3. Authenticate the device.
4. Validate device trust.
5. Validate offline authorization context.
6. Submit pending transactions.
7. Validate transaction UUIDs.
8. Validate Business and Branch identity.
9. Validate employee and permissions.
10. Validate subscription state.
11. Validate business rules.
12. Process accepted transactions.
13. Return validation results.
14. Update local synchronization state.
15. Refresh required server data.
16. Record synchronization events.

---

## 32. Synchronization Idempotency

Synchronization must be idempotent.

If the same transaction is submitted multiple times because of:

* Network interruption
* Retry
* Application restart
* Device restart
* Server response timeout
* Duplicate synchronization attempt

the server must recognize the existing transaction UUID and must not create a second business transaction.

Retrying the same transaction must remain different from creating a genuinely new transaction.

---

## 33. Duplicate Prevention

Duplicate synchronization must never create:

* Duplicate order
* Duplicate payment
* Duplicate inventory deduction
* Duplicate cancellation
* Duplicate refund
* Duplicate correction
* Duplicate production transaction
* Duplicate business audit event representing a new action

Technical retry attempts may still be logged as synchronization/technical events.

---

## 34. Interrupted Synchronization

Synchronization itself may be interrupted.

Example:

1. Device begins synchronization.
2. Some transactions are accepted.
3. Network connection is lost.
4. Remaining transactions remain pending.
5. Device later reconnects.
6. Synchronization resumes.

Already accepted transactions must not be recreated.

The next synchronization attempt must use:

* Transaction UUID
* Synchronization state
* Server acceptance state

to continue safely.

---

## 35. Transaction Dependencies

Where transactions depend on one another, synchronization must preserve their required business order.

For example:

* An order modification must not be processed without its parent order.
* A payment must not be accepted as an unrelated transaction without its order.
* An inventory adjustment related to a transaction must preserve its relationship.
* A correction must reference the relevant original record.
* A cancellation must reference the original order/item state.
* A refund must reference the relevant payment/order context.

The exact dependency mechanism is a technical design decision.

The business requirement is that synchronization must preserve valid business relationships.

---

## 36. Inventory Synchronization Conflicts

Inventory is authoritative on the server after synchronization.

If multiple devices have performed offline operations against the same stock, the server must validate all transactions.

Example:

* Device A locally believes 5 units are available.
* Device B locally believes 5 units are available.
* Both sell 4 units while offline.
* Both transactions cannot necessarily be accepted against the authoritative stock.

The server must identify the conflict.

It must not silently overwrite one transaction with another.

The original offline transaction must remain traceable even if the server rejects it.

---

## 37. Conflict Types

Possible synchronization conflicts include:

* Inventory no longer sufficient
* Product became inactive
* Product became unavailable
* Price/configuration changed
* Recipe version changed
* Set configuration changed
* Permission changed
* Employee became inactive
* Cash session state changed
* Device trust was revoked
* Subscription expired
* Business configuration changed
* Branch scope changed
* Another transaction affected the same resource
* Parent transaction was rejected
* Transaction dependency became invalid

The exact conflict-resolution mechanism belongs to the affected domain and later technical documentation.

---

## 38. Conflict Resolution Principles

Conflict resolution must follow these principles:

1. Preserve the original offline transaction.
2. Do not silently discard user actions.
3. Do not create duplicates.
4. Do not bypass business rules.
5. Record the conflict reason.
6. Preserve the original transaction context.
7. Apply explicit resolution where required.
8. Preserve audit history.
9. Keep historical data immutable.
10. Do not rewrite the original employee/device responsibility.

---

## 39. Rejected Transactions

If the server rejects an offline transaction:

* The original transaction remains retained.
* The rejection reason is recorded.
* The synchronization state becomes `Rejected` or equivalent.
* The transaction remains traceable.
* The user is informed where manual attention is required.
* The system must not silently delete the local record.

A rejected transaction must not be recreated automatically as a new transaction unless an authorized business workflow explicitly creates a new transaction.

---

## 40. Multiple Offline Devices

Multiple trusted devices may operate offline within the same branch.

Each device maintains its own local state.

Devices may therefore have different temporary:

* Inventory state
* Configuration state
* Permission state
* Menu state
* Synchronization state

The system must not assume that local states are identical.

After reconnection, the server becomes the central source of truth.

Server-side validation reconciles the transactions from different devices.

---

## 41. Branch Isolation

Offline data must retain the correct Branch identity.

A device operating for Branch A must not accidentally create transactions for Branch B merely because both branches belong to the same Business.

Branch switching remains subject to:

* Employee permissions
* Branch assignment
* Device authorization
* Current branch context

Offline mode must never weaken branch-level access restrictions.

---

## 42. Business Isolation

Every synchronized transaction must be validated against its Business identity.

A transaction created for one Business must never be accepted into another Business.

This remains true even if:

* The device is reused
* Employee accounts change
* The device was previously trusted for another Business
* Synchronization occurs after a long offline period
* Local data is stale

Business isolation applies to:

* Orders
* Payments
* Inventory
* Cash
* Employees
* Audit events
* Reports
* Configuration
* Synchronization queues

---

## 43. Data Refresh After Synchronization

After successful synchronization, the device must refresh data that may have changed while it was offline.

This may include:

* Menu
* Product active state
* Prices
* Branch price overrides
* Recipe versions
* Set configurations
* Inventory
* Employee permissions
* Employee status
* Branch configuration
* Cash-session state
* Subscription state
* Device authorization
* Relevant notifications

Only data within the device's authorized scope should be synchronized.

---

## 44. Server as the Source of Truth

During offline operation, the device temporarily operates using its locally authorized state.

After reconnection, the server becomes authoritative.

The server determines:

* Current employee status
* Current permissions
* Current subscription state
* Current branch authorization
* Accepted transactions
* Current inventory
* Current configuration
* Current cash-session state
* Current device trust status

Local state must not permanently override server state.

---

## 45. Offline Data Retention

Offline transactions must remain locally available until their synchronization state is safely established.

Successfully synchronized data may later be removed from local working storage according to security and data-retention rules.

Required historical records must remain available through the central system according to the Data Lifecycle rules.

Rejected or unresolved transactions must remain locally traceable until the relevant workflow has safely completed.

---

## 46. Failure Recovery

The offline system must tolerate:

* Temporary network loss
* Application restart
* Device restart
* Server temporary unavailability
* Interrupted synchronization
* Partial synchronization
* Duplicate synchronization attempts
* Background synchronization failure
* Printer failure
* Temporary local service failure

A temporary technical failure must not cause already recorded business transactions to disappear.

Synchronization should retry automatically when appropriate.

Repeated failures must be visible to authorized users.

---

## 47. Offline User Experience

The application must clearly indicate that the device is offline.

Users should be able to understand:

* That the device is offline
* Whether transactions are pending
* Whether synchronization is running
* Whether synchronization succeeded
* Whether transactions were rejected
* Whether attention is required
* Whether printer jobs are pending or failed

Offline indicators must not unnecessarily interrupt normal POS work.

The POS should remain fast and usable while synchronization runs in the background.

---

## 48. Offline-to-Online Transition

The preferred transition is:

**Offline → Connection Detected → Secure Reconnection → Authorization Validation → Synchronization → Server Validation → Data Refresh → Online**

The user should not need to manually recreate branch state or re-enter previously recorded transactions.

The transition must preserve:

* Transaction UUIDs
* Employee identity
* Device identity
* Branch identity
* Cash-session identity
* Audit history
* Synchronization state

---

## 49. Clock and Time Integrity

Offline authorization and transaction processing depend on reliable time information.

The system must protect against:

* Clock rollback
* Suspicious time jumps
* Expired offline authorization
* Replay of previously valid authorization
* Manipulation of local timestamps

A suspicious clock state may cause offline operations to be restricted until the device can reconnect and revalidate its authorization.

The exact detection and enforcement mechanism belongs to Security and Architecture documentation.

---

## 50. Security Requirements

Offline operation and synchronization must protect against:

* Unauthorized devices
* Unauthorized employees
* Cross-business access
* Cross-branch access
* Transaction replay
* Duplicate transaction creation
* Local data tampering
* Unauthorized modification of queued transactions
* Expired authorization
* Revoked device trust
* Employee deactivation
* Permission escalation
* Subscription bypass
* Clock manipulation
* Unauthorized historical modification

The detailed cryptographic and technical implementation belongs to Security and Architecture documentation.

---

## 51. Performance Requirements

Offline operation must remain lightweight.

The system must not require powerful hardware merely to support offline functionality.

Synchronization should:

* Run efficiently
* Prefer background execution
* Avoid unnecessarily blocking POS
* Avoid duplicate processing
* Avoid excessive local resource consumption
* Avoid unnecessary network traffic

Security, encryption, audit, and synchronization must be designed so that ordinary POS/office hardware can continue normal operation without noticeable performance degradation.

---

## 52. Business Rules Summary

| Area                            | Rule                                                         |
| ------------------------------- | ------------------------------------------------------------ |
| Offline availability            | Only previously registered and trusted devices               |
| First device use                | Must initially be online                                     |
| Offline authorization           | Cryptographically protected and time-bounded                 |
| Employee identity               | Individual employee account remains required                 |
| Transaction identity            | Existing UUID model                                          |
| Client Transaction ID           | Not introduced                                               |
| Local data                      | Encrypted/protected                                          |
| Draft order                     | No inventory deduction and no kitchen notification           |
| Accepted order                  | Inventory deduction and kitchen workflow initiated           |
| Inventory                       | Negative stock is not intentionally permitted                |
| Inventory acceptance            | Local validation followed by server validation               |
| Order modification              | Inventory reconciled by delta                                |
| Insufficient modification stock | Entire modification rejected; previous state preserved       |
| Cancellation                    | Separate event from original order                           |
| Served item                     | Never returns inventory                                      |
| Refund                          | Separate from cancellation and never returns inventory       |
| Cash session                    | Offline mode cannot bypass session rules                     |
| Shift handover                  | Old session closes; new cashier opens a new session          |
| Corrections                     | Preserve original values and audit history                   |
| Permissions                     | Offline authorization remains limited                        |
| Trusted device                  | Does not grant permissions                                   |
| Subscription                    | Offline mode cannot permanently bypass subscription          |
| Synchronization                 | Automatic when connection returns                            |
| Duplicate handling              | Transaction UUID prevents duplicate processing               |
| Interrupted sync                | Already accepted transactions remain accepted                |
| Rejected transaction            | Original data retained with reason                           |
| Conflicts                       | Must not silently overwrite data                             |
| Multiple devices                | Server validates and reconciles transactions                 |
| Business isolation              | Mandatory                                                    |
| Branch isolation                | Mandatory                                                    |
| Server authority                | Server becomes authoritative after reconnection              |
| Audit                           | Offline actions remain traceable                             |
| Printer failure                 | ERP transaction remains intact; print job retries separately |
| Performance                     | Offline/sync must not noticeably slow POS                    |

---

## 53. Business Analysis Boundary

This document defines the required business behavior of offline operation and synchronization.

The following remain implementation decisions:

* Local database technology
* Synchronization protocol
* Queue implementation
* Encryption implementation
* Cryptographic algorithms
* Conflict-resolution algorithms
* Network retry strategy
* Batch size
* Background worker implementation
* Cache structure
* Exact offline authorization duration
* Exact clock-tamper detection mechanism
* Exact synchronization ordering mechanism
* Local storage technology
* Printer retry implementation

These decisions must be documented later in:

* `04_Architecture`
* `05_Database`
* `06_Backend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`

---

## Related Documents

* `01_Business_Analysis/01_Product_Overview.md`
* `01_Business_Analysis/02_Business_Model.md`
* `01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/08_POS_and_Order_Management.md`
* `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `01_Business_Analysis/10_Shift_Handover.md`
* `01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `01_Business_Analysis/12_Products_and_Recipes.md`
* `01_Business_Analysis/13_Menu_and_Pricing.md`
* `01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `01_Business_Analysis/16_Reports_and_Dashboards.md`
* `01_Business_Analysis/17_Notifications_and_Alerts.md`
* `01_Business_Analysis/18_Audit_and_Change_History.md`
* `01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `01_Business_Analysis/20_Business_Rules.md`
* `04_Architecture`
* `05_Database`
* `06_Backend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`
* `adr/ADR-001-Documentation-First.md`

