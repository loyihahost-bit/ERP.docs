# Offline Operation and Synchronization

**Document ID:** FF-BA-007
**Status:** Accepted
**Version:** 1.0
**Scope:** Offline operation, local data, transaction processing, synchronization, and conflict handling
**Parent Document:** `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`

---

## 1. Purpose

This document defines how the FastFood ERP operates when a branch temporarily loses internet connectivity.

The system must allow a restaurant branch to continue essential operations during temporary network interruptions while preserving:

* Data integrity
* Employee accountability
* Business and branch isolation
* Permission enforcement
* Transaction uniqueness
* Auditability
* Reliable synchronization

Offline operation is a business-continuity capability, not a separate version of the ERP.

---

## 2. Offline-First Principle

The system must be designed so that temporary internet loss does not unnecessarily stop normal restaurant operations.

A branch may continue supported operations using previously synchronized and authorized local data.

The system must automatically return to normal online operation when connectivity is restored.

The user should not need to manually recreate orders or enter the same transactions again merely because the internet connection was temporarily unavailable.

---

## 3. Conditions for Offline Operation

Offline operation is available only when the device has previously:

1. Connected to the server.
2. Been registered and trusted.
3. Received valid offline authorization.
4. Obtained the necessary business and branch data.
5. Obtained valid employee authorization for supported offline operations.

An unknown or newly introduced device must not begin ERP operation for the first time while offline.

---

## 4. Offline Scope

Offline mode is intended primarily to preserve essential branch operations.

Supported offline functionality may include:

* Creating orders
* Modifying permitted orders
* Applying permitted discounts
* Recording supported payments
* Printing supported receipts
* Deducting inventory according to available local inventory state
* Cash-session operations allowed by the current authorization
* Recording audit information
* Viewing required locally synchronized data

Functions that fundamentally require current server information may remain unavailable until connectivity is restored.

The exact technical list of offline-capable functions must be finalized during system architecture and implementation planning.

---

## 5. Offline Data Availability

Before going offline, the device must have the data required for supported operations.

This may include:

* Active menu items
* Product information
* Recipe information required for permitted operations
* Prices
* Relevant branch inventory state
* Employee authorization information
* Cash-session information
* Required business configuration
* Device authorization
* Relevant reference data

The system must not assume that all historical or business-wide data must be stored locally.

Only data necessary for supported offline operation should be synchronized to the device.

---

## 6. Local Data Protection

Offline data must be protected against unauthorized access.

Local business data must not be stored as openly readable files.

Sensitive locally stored information must use appropriate encryption and secure credential handling.

If a device is lost or stolen, local data must not become easily accessible simply by accessing the device storage directly.

The exact encryption technology belongs to the Security and Architecture documents.

---

## 7. Transaction Identity

Every transaction created offline must use the existing transaction UUID model.

The system must not introduce a separate Client Transaction ID.

A transaction UUID must remain stable throughout the transaction lifecycle.

The same UUID must be used when the transaction is later synchronized with the server.

This allows the server to recognize whether a transaction has already been processed.

---

## 8. Offline Order Creation

When a cashier creates an order while offline:

1. The employee is authenticated locally.
2. The device authorization is checked.
3. The employee's offline permissions are checked.
4. The order receives its UUID.
5. The order is associated with the correct business and branch.
6. The order records the responsible employee and device.
7. Applicable business rules are evaluated locally.
8. The order is stored securely.
9. The order becomes available for supported restaurant operations.
10. The order is queued for synchronization.

The cashier should not need to repeat the order after the connection returns.

---

## 9. Required Transaction Context

Offline transactions must preserve sufficient identity information to prevent cross-business or cross-branch mixing.

Important transaction records should retain, where applicable:

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

The exact database structure is defined later in the Database and Architecture documents.

---

## 10. Offline Order Number

The customer-facing order number remains separate from the transaction UUID.

The existing three-digit order number behavior remains governed by the Cash Register and Order Management rules.

The order number may reset according to the relevant cash-session lifecycle.

The UUID remains the permanent transaction identity even if the customer-facing order number is reused in a later cash session.

---

## 11. Offline Inventory

Offline inventory must use the latest valid inventory state available on the device.

The system must continue enforcing the no-negative-stock rule as far as the available synchronized inventory state allows.

If the local inventory state indicates insufficient stock, the system must block the relevant operation according to normal inventory rules.

The device must not intentionally permit negative inventory merely because it is offline.

---

## 12. Inventory Synchronization

Inventory changes created offline must be synchronized with the server after reconnection.

The server must process offline inventory changes according to the authoritative inventory rules.

If multiple devices or branches have made changes affecting the same inventory, the server must identify and handle the resulting conflict rather than silently overwriting one transaction with another.

Inventory synchronization must preserve the history of relevant changes.

---

## 13. Offline Cash Operations

Offline cash operations must follow the currently authorized cash-session state.

The system must not allow offline mode to bypass cash-session rules.

For example:

* A cashier cannot become responsible for a session without the required acceptance process.
* A closed session does not become open simply because the device is offline.
* Permission restrictions remain active.
* Cash-session identity remains associated with the transaction.

Cash-session correction rules continue to apply after synchronization.

---

## 14. Offline Permissions

Offline mode must use the employee authorization state that was valid when the device received its offline authorization.

A trusted device does not automatically give every employee unrestricted permissions.

The employee must still operate according to:

* Their role
* Their permission set
* Their branch scope
* Their business scope

Permission changes made on the server while a device is offline may not be immediately visible to the device.

After reconnection, the server becomes authoritative.

---

## 15. Offline Subscription Restrictions

Offline mode must not bypass subscription restrictions.

If the business subscription becomes restricted or expires while a device is offline, the device may temporarily continue according to its already valid offline authorization until the applicable authorization boundary is reached.

After synchronization or authorization renewal, current subscription restrictions must be enforced.

The exact offline grace behavior must be defined consistently with the subscription lifecycle and security architecture.

---

## 16. Offline Audit Information

Offline actions must be recorded locally with enough information to reconstruct what happened.

At minimum, important actions must retain:

* Employee identity
* Device identity
* Business identity
* Branch identity
* Transaction identity
* Timestamp
* Action type
* Relevant previous/new values where applicable
* Synchronization state

Offline audit information must not disappear simply because synchronization fails temporarily.

---

## 17. Synchronization Queue

Transactions created while offline must enter a local synchronization queue.

Each queued item must have a clear synchronization state.

Conceptually, states may include:

* Pending
* Sending
* Accepted
* Rejected
* Requires Review

The exact state model is an implementation decision, but the system must always be able to determine whether an offline transaction has been successfully synchronized.

---

## 18. Automatic Synchronization

When connectivity returns, synchronization should begin automatically.

The user should not normally need to manually resend every transaction.

Synchronization should:

1. Establish a secure server connection.
2. Authenticate the device.
3. Validate the device authorization.
4. Submit pending transactions.
5. Validate transaction UUIDs.
6. Process accepted transactions.
7. Return validation results.
8. Update local synchronization state.
9. Refresh required server data.
10. Record synchronization events.

---

## 19. Idempotent Synchronization

Synchronization must be idempotent.

If the same transaction is submitted more than once because of:

* Network interruption
* Retry
* Application restart
* Server response timeout
* Duplicate synchronization attempt

the server must recognize the existing transaction UUID and must not create a second business transaction.

The system must distinguish between:

**Retrying the same transaction**

and

**Creating a genuinely new transaction.**

---

## 20. Interrupted Synchronization

Synchronization may itself be interrupted.

For example:

1. Device begins synchronization.
2. Some transactions are accepted.
3. Network connection is lost.
4. Remaining transactions stay pending.

The system must not require already accepted transactions to be recreated.

The next synchronization attempt must continue safely using transaction UUIDs and synchronization state.

---

## 21. Synchronization Order

Where transaction dependencies exist, synchronization must respect the required business sequence.

For example, a dependent inventory or payment operation must not be processed as an unrelated standalone action if its parent transaction has not yet been accepted.

The exact dependency mechanism is a technical design decision.

The business requirement is that synchronization must preserve valid business relationships.

---

## 22. Conflict Handling

A conflict occurs when offline data cannot be accepted directly because the server state has changed in a way that affects the transaction.

Examples may include:

* Inventory no longer sufficient
* Product became unavailable
* Price changed
* Permission changed
* Cash session state changed
* Another synchronized transaction affected the same resource
* Business or branch configuration changed

Conflicts must not be silently resolved by overwriting data.

The system must preserve the original offline transaction and record the reason for the conflict.

---

## 23. Conflict Resolution Principles

Conflict resolution must follow these principles:

1. Preserve the original transaction.
2. Do not silently discard user actions.
3. Do not create duplicate transactions.
4. Do not bypass business rules.
5. Record the conflict reason.
6. Apply an explicit resolution where required.
7. Preserve an audit trail.

The exact resolution workflow depends on the affected business domain.

---

## 24. Rejected Transactions

If the server rejects an offline transaction, the system must retain the rejected transaction and its original information.

The rejection must include a meaningful reason.

The system must not simply delete the rejected transaction from local history.

Where manual resolution is possible, the user must be shown what requires attention.

---

## 25. Duplicate Transactions

The server must prevent duplicate creation when the same offline transaction is synchronized multiple times.

The transaction UUID is the primary mechanism for identifying the same transaction.

A duplicate synchronization attempt must not result in:

* Duplicate order
* Duplicate payment
* Duplicate inventory deduction
* Duplicate audit event representing a new business action

Technical retry events may still be logged separately from the original business transaction.

---

## 26. Multiple Offline Devices

Multiple trusted devices may operate offline within the same branch.

Each device must maintain its own local transaction state.

When devices reconnect, the server becomes the central source of truth.

The system must not assume that two offline devices have identical local inventory or configuration states.

Synchronization must reconcile their transactions through server-side validation.

---

## 27. Branch Isolation During Offline Operation

Offline data must retain the correct branch identity.

A device operating for Branch A must not accidentally create transactions for Branch B merely because the same business has multiple branches.

Branch switching must remain subject to employee authorization.

Offline mode must not weaken branch-level access restrictions.

---

## 28. Business Isolation During Synchronization

The server must validate the business identity associated with every synchronized transaction.

A transaction created for one business must never be accepted into another business.

This rule applies even if:

* The device is reused
* Employee accounts change
* A device was previously trusted for another business
* Synchronization occurs after a long offline period

---

## 29. Data Refresh After Synchronization

After successful synchronization, the device should refresh data that may have changed while it was offline.

This may include:

* Menu
* Prices
* Recipes
* Inventory
* Employee permissions
* Branch configuration
* Subscription state
* Device authorization

Only data relevant to the device's authorized scope should be synchronized.

---

## 30. Server as the Source of Truth

During offline operation, the device temporarily operates using its locally authorized state.

After reconnection, the server becomes authoritative.

The server determines:

* Current permissions
* Current subscription state
* Current branch authorization
* Accepted transactions
* Current inventory state
* Current configuration
* Device trust status

Local data must not permanently override server state.

---

## 31. Offline Data Retention

Offline transactions must remain locally available until their synchronization state is safely established.

Successfully synchronized data may later be removed from local working storage according to the system's data-retention and security policies.

Required historical records must remain available through the central system according to the relevant data lifecycle rules.

---

## 32. Failure Recovery

The system must tolerate:

* Temporary network loss
* Application restart
* Device restart
* Interrupted synchronization
* Server temporary unavailability
* Duplicate synchronization attempts
* Partial synchronization

A temporary failure must not cause already recorded transactions to disappear.

The system should retry synchronization automatically when appropriate.

Repeated synchronization failures must be visible to authorized users.

---

## 33. User Experience During Offline Mode

The application must clearly indicate that the device is offline.

Users should be able to understand:

* That they are operating offline
* Whether transactions are pending synchronization
* Whether synchronization is in progress
* Whether synchronization succeeded
* Whether any transactions require attention

The offline indicator must not unnecessarily interrupt normal POS work.

---

## 34. Offline-to-Online Transition

When connectivity returns, the application should transition automatically toward online operation.

The preferred flow is:

**Offline → Connection Detected → Secure Reconnection → Synchronization → Server Validation → Data Refresh → Online**

The user should not need to manually recreate the branch state.

---

## 35. Security Requirements

Offline synchronization must provide protection against:

* Unauthorized devices
* Unauthorized employees
* Cross-business access
* Cross-branch access
* Transaction replay
* Duplicate transaction creation
* Local data tampering
* Unauthorized modification of queued transactions
* Expired authorization
* Clock manipulation

The detailed cryptographic and technical implementation belongs to the Security and Architecture documents.

---

## 36. Performance Requirements

Offline operation must remain lightweight.

The system should not require powerful hardware merely to support offline functionality.

Synchronization should run efficiently and should avoid unnecessarily blocking POS operations.

Where possible, synchronization should operate in the background while employees continue normal restaurant operations.

---

## 37. Business Rules Summary

| Area                  | Rule                                                |
| --------------------- | --------------------------------------------------- |
| Offline availability  | Only previously authorized/trusted devices          |
| First device use      | Must initially be online                            |
| Employee identity     | Individual employee account remains required        |
| Transaction identity  | Existing UUID model                                 |
| Client Transaction ID | Not introduced                                      |
| Local data            | Securely protected                                  |
| Inventory             | No intentional negative stock                       |
| Cash session          | Offline mode cannot bypass cash rules               |
| Permissions           | Offline authorization remains limited               |
| Subscription          | Offline mode cannot permanently bypass subscription |
| Synchronization       | Automatic when connection returns                   |
| Duplicate handling    | Transaction UUID prevents duplicate processing      |
| Interrupted sync      | Already accepted transactions remain accepted       |
| Rejected transaction  | Original data retained with reason                  |
| Conflicts             | Must not silently overwrite data                    |
| Multiple devices      | Server reconciles transactions                      |
| Business isolation    | Mandatory                                           |
| Branch isolation      | Mandatory                                           |
| Server authority      | Server becomes authoritative after reconnection     |
| Audit                 | Offline actions remain traceable                    |
| Performance           | Offline/sync must not noticeably slow POS           |

---

## 38. Business Analysis Boundary

This document defines the required business behavior of offline operation and synchronization.

The following remain implementation decisions:

* Local database technology
* Synchronization protocol
* Queue implementation
* Encryption implementation
* Conflict-resolution algorithms
* Network retry strategy
* Cryptographic signatures
* Local cache structure
* Synchronization batch size
* Background worker implementation
* Exact offline authorization duration

These decisions must be documented later in the Architecture, Database, Backend, Security, and Deployment documentation.

---

## Related Documents

* `01_Business_Analysis/01_Product_Overview.md`
* `01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/08_POS_and_Order_Management.md`
* `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `01_Business_Analysis/18_Audit_and_Change_History.md`
* `01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `01_Business_Analysis/20_Business_Rules.md`
* `04_Architecture`
* `05_D_

