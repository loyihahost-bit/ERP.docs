# POS and Order Management

**Document ID:** FF-BA-008
**Status:** Accepted
**Version:** 2.0
**Scope:** Point of Sale (POS), order lifecycle, order types, tables, waiters, order items, customization, Sets, modifications, cancellation, kitchen printing, offline operation, and order-related business rules
**Parent Document:** `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`

---

## 1. Purpose

This document defines the business requirements for the Point of Sale (POS) and order management system.

The POS must allow restaurant employees to create and process orders quickly while maintaining:

* Accurate order information
* Employee accountability
* Inventory consistency
* Payment consistency
* Cash-session relationships
* Table and waiter relationships
* Kitchen communication
* Offline operation
* Auditability
* Historical integrity

The POS must remain lightweight and practical for everyday restaurant operations.

---

## 2. POS Operating Model

The initial POS model is based on physical order entry by restaurant employees.

The primary order-entry user is the cashier.

Waiters may participate in order creation and serving workflows where their permissions allow it.

The current order types are:

1. Hall / Dine-in
2. Takeaway

Phone Delivery and online customer ordering are not part of the current operational scope.

Future integrations such as:

* Customer mobile applications
* Online ordering
* Telegram ordering
* External delivery platforms
* Full CRM
* Advanced delivery management

must be able to build on the core order model without requiring the order identity model to be redesigned.

---

## 3. Order Identity

Every order has a permanent unique technical identity.

The order uses the existing UUID model.

The UUID:

* Is generated when the order is created.
* Remains unchanged throughout the order lifecycle.
* Is used for synchronization.
* Is used for duplicate protection.
* Is used for auditability.
* Remains the permanent identity of the order.

The system does not introduce a separate Client Transaction ID.

Therefore:

**Order UUID ≠ Customer-Facing Order Number**

The UUID is not required to be displayed to customers.

---

## 4. Customer-Facing Order Number

The POS uses a short customer-facing order number for practical restaurant operations.

The current requirement is a three-digit order number.

The three-digit number:

* Is easy to communicate to customers.
* Is displayed on relevant restaurant screens and receipts.
* Resets when a new cash session begins.
* Is not the permanent identity of the order.

The same three-digit number may therefore appear again in a later cash session.

Historical records remain distinguishable through:

* Order UUID
* Cash Session UUID
* Branch
* Business
* Relevant timestamps

---

## 5. Current Order Types

### 5.1 Hall / Dine-in

The customer consumes the order inside the restaurant.

The order may be associated with:

* Hall
* Table
* Waiter

where the branch uses table service.

A table may have multiple separate orders at the same time.

Each order remains an independent business transaction with its own:

* Order UUID
* Lifecycle
* Items
* Payment
* Inventory effects
* Audit history

---

### 5.2 Takeaway

The customer receives the order for consumption outside the restaurant.

A permanent customer profile is not required.

The order remains associated with its normal business context, including:

* Business
* Branch
* Employee
* Device
* Cash session
* Order UUID

---

## 6. Customer Information

The current system does not require a full customer database.

Normal Hall/Dine-in and Takeaway orders do not require customer information.

Debt transactions require:

* Customer name
* Customer phone number

Address and comment may also be stored when operationally required.

Customer information is stored as part of the relevant business transaction unless a future CRM system introduces a separate customer domain.

Duplicate phone numbers are allowed.

---

## 7. Order Context

When an order is created, it must be associated with the correct operating context.

Important context includes:

* Order UUID
* Business UUID
* Branch UUID
* Employee UUID
* Device UUID
* Cash Register UUID where applicable
* Cash Session UUID where applicable
* Order type
* Table UUID where applicable
* Main Waiter UUID where applicable
* Creation timestamp
* Current order state

The system must not allow an order to be silently created under the wrong Business or Branch.

---

## 8. Order Lifecycle

The business order lifecycle is:

**Draft → Accepted → Preparing → Ready → Served**

There is no `Completed` order state.

`Served` represents that the ordered item has been delivered to the customer.

Payment is a separate financial process and does not create a `Completed` order state.

The order state and payment state must therefore remain conceptually separate.

---

## 9. Draft State

A Draft order is an incomplete order being prepared by an employee.

Draft behavior:

* The order is autosaved.
* The order does not notify the kitchen.
* The order does not deduct inventory.
* The table remains `FREE`.
* The order may be edited according to permissions.
* The order can remain Draft until it is validly saved/accepted.

A Draft may contain insufficient-stock items during preparation.

The inventory check occurs when the order is saved/accepted into the operational lifecycle.

---

## 10. Accepting a Draft

When a Draft is saved/accepted:

1. The system validates the order.
2. Required inventory availability is checked.
3. Inventory deduction is performed atomically.
4. The order becomes `Accepted`.
5. The table becomes `OCCUPIED` where applicable.
6. The kitchen workflow is initiated.
7. Relevant printer jobs are created.
8. The order becomes part of the synchronization/audit flow.

If required inventory is insufficient:

* The acceptance operation is rejected.
* The order remains Draft.
* Inventory is not partially deducted.
* The kitchen is not notified.
* The table does not become occupied.

The order must not enter `Accepted` state with an invalid inventory result.

---

## 11. Product Selection

The cashier or authorized employee selects products from the active menu available to the current branch.

Only products that are currently:

* Active
* Available to the branch
* Allowed by subscription
* Allowed by employee permission
* Not unavailable due to applicable operational rules

should normally be selectable.

Inactive products are not shown or sold through the POS.

Historical orders containing previously active products remain unchanged.

---

## 12. Product Categories

Each product belongs to exactly one menu category.

The POS uses the product's current valid category for menu presentation.

Changing a product's category later must not rewrite the category information historically associated with completed business records where a historical snapshot is required.

---

## 13. Order Items

An order may contain multiple products.

Each order item must preserve enough information to understand what was actually sold.

Relevant information includes:

* Product identity
* Product snapshot/configuration
* Quantity
* Applied selling price
* Customization
* Extras
* Discount where applicable
* Comments
* Final item amount
* Relevant inventory effect

Historical orders must not depend exclusively on the current product or recipe configuration.

Later product price or recipe changes must not recalculate historical orders.

---

## 14. Quantity

The POS supports changing the quantity of an order item where permitted.

However, when different units of the same product require different customization, the system must be able to represent the individual units separately.

Example:

Quantity: `2`

* Unit 1: Normal
* Unit 2: No mayonnaise

The system must therefore not assume that every unit of a quantity always has identical customization.

---

## 15. Unit-Level Customization

Customization is performed at the individual unit level.

Each unit may have its own:

* Removed ingredients
* Increased ingredients
* Added extras
* Other supported customization

Example:

Quantity `3` may contain three different customization states.

Inventory, cost, price, and kitchen instructions must be calculated according to each unit's actual configuration.

The POS does not require an `Apply to all` operation.

The base recipe itself is never modified by a one-time order customization.

---

## 16. Ingredient Removal

A customer may remove a recipe ingredient when the business rules permit removal.

If an ingredient is removed completely:

* The unit's effective ingredient quantity becomes `0`.
* The removed quantity is not deducted from inventory.
* The base recipe remains unchanged.
* The kitchen receives the customization.
* The price effect follows the configured business pricing rule.

The current business model supports configurable pricing behavior for customization, including:

* No price change
* Subtract ingredient cost
* Subtract ingredient selling value

The exact pricing configuration is defined in `13_Menu_and_Pricing.md`.

---

## 17. Increased Ingredients

A customer may request more of an existing ingredient where the product/business configuration permits it.

Example:

Base quantity:

`30g`

Customer quantity:

`50g`

The system records:

`+20g`

The additional `20g` must:

* Be deducted from inventory.
* Affect cost where applicable.
* Affect selling price according to the configured markup/pricing rule.
* Appear as a separate customization instruction for the kitchen.

---

## 18. Extras

Approved extras/additional ingredients may be added to an order unit.

When an extra is added:

* The extra is recorded explicitly.
* Required inventory is deducted.
* Additional cost is calculated.
* Additional selling price is calculated according to business configuration.
* Kitchen output includes the extra.

Employees must not create arbitrary inventory-consuming extras outside configured business rules.

---

## 19. Component Swapping

Component swapping is not supported in the current business model.

For example:

**Remove Component A + Add Component B**

must not automatically be treated as an exchange.

Supported mechanisms are:

* Ingredient removal
* Ingredient increase
* Approved extra

Advanced component substitution may be introduced later as a separate business capability.

---

## 20. Non-Recipe Changes

Not every customer request needs to change recipe inventory.

Permitted non-recipe preparation instructions may be stored as comments.

Comments:

* Must be understandable to restaurant staff.
* Must not silently change inventory.
* Must not bypass structured business rules.
* Must not replace required structured cancellation, refund, correction, or permission data.

---

## 21. Multiple Customized Units

The POS must support independent customization for each unit.

Example:

| Unit | Configuration |
| ---- | ------------- |
| 1    | Normal        |
| 2    | No mayonnaise |
| 3    | Extra cheese  |

Each unit may therefore produce different:

* Inventory consumption
* Cost
* Selling price
* Kitchen instruction

The system must preserve this distinction in the order record.

---

## 22. Order Modification Before Served

An order may be modified after acceptance and before the relevant item reaches `Served`, provided the employee has the required permission.

Supported changes include:

* Product quantity
* Product selection where allowed
* Ingredient removal
* Ingredient increase
* Extras
* Discounts where permitted
* Comments
* Other configured order modifications

Inventory must be reconciled by delta.

Examples:

* `30g → 0g` → return `30g`
* `30g → 50g` → deduct additional `20g`
* `30g → 20g` → return `10g`

If additional inventory required by the modification is insufficient:

* The entire modification is rejected.
* The existing order remains unchanged.
* No partial modification is saved.

---

## 23. Modification After Kitchen Ticket

If an Accepted order has already generated a kitchen ticket and is then modified:

1. The previous kitchen ticket is marked `CANCELLED` or `UPDATED`.
2. A new kitchen ticket is generated.
3. The same Order UUID remains.
4. The same customer-facing order number remains.
5. Inventory is reconciled by delta.
6. Audit history records the modification.
7. The new ticket represents the current order state.

The new kitchen ticket does not need to show the complete difference from the old ticket.

The complete change history remains available through audit/history records.

---

## 24. Table Model

Where a branch uses tables, a table may contain multiple separate orders.

A table is considered occupied when at least one relevant open order exists.

A table may be shown using operational states such as:

* `FREE`
* `OCCUPIED`
* `WAITING_FOR_ORDER`

The exact UI representation is a Frontend concern.

The business state must remain consistent with the existence of open orders.

A table becomes free only when all relevant open orders are resolved according to the applicable business process.

---

## 25. Waiter Assignment

A table/order may have a permanent waiter assignment or a temporary waiter assignment.

If no permanent waiter is assigned:

* The first authorized employee who saves/accepts the order becomes the main waiter where the waiter workflow applies.

Only one main waiter is assigned to an order/table workflow at a time.

Other employees may assist without automatically becoming the main waiter.

Historical waiter responsibility must remain traceable.

---

## 26. Waiter Helpers

Additional employees may help serve an order.

A helper:

* May perform permitted serving actions.
* Does not automatically become the main waiter.
* Does not automatically receive payment authority.
* Does not automatically receive order modification authority.

The helper's action may still be recorded in audit/history where applicable.

---

## 27. Help Workflow

The `Help` workflow is intended for operational assistance.

A helper may:

* Deliver a Ready item to the customer.
* Mark the relevant item as Served where authorized.

Help does not automatically:

* Create a new order
* Free the table
* Change the main waiter
* Take payment
* Reassign the entire order

Those actions require their own permissions/workflows.

---

## 28. Served State

`Served` means the relevant item has been delivered to the customer.

A Served item is not considered available for inventory return.

A Served item can never be returned to inventory through cancellation.

The order may continue to contain other non-Served items.

Therefore, item-level state is important even when an order contains multiple products.

---

## 29. Walkout

Walkout is a controlled operational workflow for cases where a customer leaves without normal completion/payment handling.

Walkout may be performed by:

* Cashier
* Other explicitly authorized employee

Only items that have reached `Served` state and satisfy the main-waiter rule are included in the relevant Walkout responsibility calculation.

The system records the Walkout event.

Relevant information includes:

* Business
* Branch
* Table
* Related orders
* Cash session
* Cashier
* Main waiter
* Timestamps
* Item states
* Amounts
* Reason
* Comment

Walkout must remain auditable.

---

## 30. Order Cancellation

Cancellation is separate from refund.

Cancellation:

* Requires appropriate permission.
* Requires a reason.
* Requires a comment where applicable.
* Preserves the original order.
* Creates a separate cancellation event.
* Updates the relevant order/item state.
* Notifies the kitchen where required.

The order must not simply be deleted.

---

## 31. Cancellation by Item

Cancellation may affect individual items or quantities within an order.

The cancellation workflow includes a per-item `Return Inventory` decision.

For eligible items:

* `Return Inventory = Yes` → inventory is returned.
* `Return Inventory = No` → inventory is not returned.

The default for eligible non-Served items is return enabled.

A Served item can never return inventory.

---

## 32. Inventory Return Eligibility

The current rule is:

* All non-Served items are eligible for inventory return.
* Served items are never eligible for inventory return.
* The final decision is recorded per item during cancellation.

The system does not attempt to model informal external kitchen conversations.

Authorized staff determine the applicable inventory-return action through the cancellation workflow.

The decision is auditable.

---

## 33. Refund Relationship

Cancellation and refund are separate operations.

A paid order may require:

1. Order cancellation.
2. Separate refund.

Refund rules are defined in:

`14_Payments_Discounts_and_Refunds.md`

A refund:

* Requires authorization.
* Requires a reason.
* Requires a comment.
* May be full or partial.
* May target specific items or quantities.
* Currently supports Cash and Card.
* Does not return inventory.

The cancellation event and refund event must remain separately auditable.

---

## 34. Discounts

The POS supports discounts.

The Owner defines applicable discount rules.

Discount usage is permission-controlled.

Supported discount types include:

* Percentage
* Fixed amount

The order must retain sufficient information to determine:

* Original amount
* Discount
* Final amount
* Employee who applied the discount
* Applicable discount rule
* Required reason/configuration

Discounts must be traceable historically.

---

## 35. Sets

A Set is a predefined bundle of component products.

A Set is stored as a separate product/business item.

A Set has:

* Its own selling price
* A defined component composition
* Inventory effects based on its components
* Its own configuration/history

The customer cannot swap one predefined component for another through normal Set ordering.

Future Set functionality may be expanded without changing the basic Set model.

---

## 36. Set Inventory

When a Set is sold:

* Inventory is deducted according to the Set's component products.
* Component availability is validated.
* Mandatory unavailable components prevent the Set from being sold.

A Set is unavailable in POS when a mandatory component is unavailable because of:

* Insufficient stock
* `Equipment Broken` status
* Other explicitly configured unavailability rules

The system must not create negative inventory.

---

## 37. Set Pricing

A Set has a separately configurable selling price.

The Owner defines the Set selling price.

Set cost is derived from its component products.

Changes in component product selling prices do not automatically change the Set selling price.

The Set selling price remains the explicitly configured business value until the Set configuration is changed.

Component cost changes may affect the calculated Set cost.

---

## 38. Set Composition Stability

Changes to an underlying product recipe do not automatically change the composition of an existing Set.

To change a Set composition, an authorized user must explicitly edit the Set.

The system must preserve:

* Previous Set composition
* New Set composition
* Configuration version/history
* Effective time

Historical orders must not be recalculated because of later Set changes.

---

## 39. Set Configuration Effective Time

A changed Set configuration becomes effective from the next applicable cash session.

Therefore:

* The current cash session continues using the current Set configuration.
* The new configuration remains pending.
* The new configuration becomes active at the next cash session.
* Previous configuration history is preserved.
* Existing orders are not recalculated.

This rule prevents configuration changes from silently changing transactions already in progress.

---

## 40. Product Activation

Each product has an active/inactive state.

If a product is inactive:

* It is not shown in the active POS menu.
* It cannot normally be sold.
* Its historical records remain intact.
* Its historical orders are not deleted or recalculated.

Reactivation may make the product available again according to business and branch rules.

---

## 41. Menu and Pricing Snapshot

At the time an order is accepted, the system must preserve the relevant commercial information needed to understand the transaction.

This may include:

* Product
* Price
* Applied discount
* Customization
* Set configuration
* Relevant recipe/configuration version
* Quantity
* Final amount

Later changes to the menu, price, recipe, or Set must not rewrite historical transactions.

---

## 42. Kitchen Printer Routing

Kitchen printer routing is configurable by branch.

Products or categories may be routed to different printers.

Example:

* Pizza → Pizza printer
* Lavash → Lavash printer

A single order may therefore generate multiple kitchen print jobs.

Each print job contains only the information relevant to its configured preparation area.

---

## 43. Kitchen Ticket Content

A kitchen ticket may include:

* Customer-facing order number
* Relevant products
* Quantities
* Unit-level customizations
* Removed ingredients
* Increased ingredients
* Extras
* Preparation comments
* Relevant order/table information

Customer payment details are not required in kitchen output unless separately configured.

---

## 44. Printer Failure

Printer failure must not roll back a valid ERP transaction.

For example:

1. Order is accepted.
2. Inventory is deducted.
3. Kitchen print job is created.
4. Printer is unavailable.
5. ERP transaction remains valid.
6. Print job enters `Pending` or `Failed`.
7. The system retries after printer recovery.

Conceptual print states include:

* `Pending`
* `Failed`
* `Retrying`
* `Printed`

The system must retain:

* Print job identity
* Related order/event identity
* Printer identity
* Attempt history
* Failure information
* Retry information

A retry must not create:

* Duplicate order
* Duplicate inventory deduction
* Duplicate payment
* Duplicate business transaction

Persistent printer failures must generate appropriate notifications.

---

## 45. Payment Relationship

Payment is a separate financial process.

The order must retain its payment relationship after payment.

Supported payment methods are:

* Cash
* Card
* Debt
* Mixed

Mixed payment may combine the supported payment methods.

Payment details are defined in:

`14_Payments_Discounts_and_Refunds.md`

The POS must not mark an order as paid without recording the corresponding payment state.

Payment does not create a separate `Completed` order state.

---

## 46. Debt Orders

Debt may be selected as an order payment method where permitted.

A debt order requires:

* Customer name
* Customer phone

Multiple debt orders may belong to the same customer.

Partial repayment is supported.

The same phone number may exist on multiple customer debt records.

Historical debt orders retain the customer information recorded at the time.

Debt editing and deletion are permission-controlled.

A debt customer record may only be deleted after all associated debts have been paid, while historical orders retain the original information.

---

## 47. Inventory Deduction

For accepted recipe-based products:

**Accepted Order → Effective Recipe/Customization → Inventory Consumption**

Inventory deduction occurs when the order is accepted/saved into the operational lifecycle, not while it remains Draft.

The deduction must reflect:

* Product quantity
* Recipe components
* Unit-level customization
* Ingredient removal
* Ingredient increase
* Extras
* Set components where applicable

The system must not rely only on the current recipe if the order was created under a previous approved configuration.

---

## 48. Inventory Atomicity

Order acceptance and required inventory deduction must behave as one atomic business operation.

The system must not create a state where:

* Order is Accepted but required inventory deduction did not occur.
* Inventory was deducted but the order was not accepted.
* Only part of an order was accepted.
* A synchronization retry deducted inventory twice.

The exact database transaction implementation belongs to technical documentation.

The business requirement is atomic business consistency.

---

## 49. Insufficient Inventory

Negative inventory is not allowed.

If required inventory is insufficient:

* The acceptance operation is blocked.
* The order remains Draft where applicable.
* Inventory is not partially deducted.
* Kitchen notification is not created.
* The cashier may remove or modify the affected item.
* The system recalculates the order.

For an Accepted order modification, if additional stock is insufficient:

* The entire modification is rejected.
* The original Accepted order remains unchanged.

---

## 50. Historical Inventory Context

Historical orders must preserve enough information to understand the inventory effect at the time of sale.

Later changes to:

* Recipes
* Product prices
* Set composition
* Product activation
* Menu configuration

must not silently recalculate historical orders.

Historical inventory events remain traceable to their original transaction.

---

## 51. Offline POS

The POS supports approved offline operations on trusted devices.

Offline order behavior is defined in:

`07_Offline_Operation_and_Synchronization.md`

Offline POS must preserve:

* Order UUID
* Business
* Branch
* Employee
* Device
* Cash session
* Inventory context
* Audit context

Offline operation must not bypass:

* Permissions
* Branch scope
* Business scope
* Subscription rules
* Inventory rules
* Cash-session rules

When connectivity returns, synchronization uses the existing UUID and idempotency model.

---

## 52. Synchronization and Duplicate Protection

Offline transactions must be safely synchronized after connectivity returns.

If the same transaction is submitted more than once because of:

* Network failure
* Retry
* Application restart
* Server timeout

the server must recognize the existing transaction UUID.

The retry must not create:

* Duplicate order
* Duplicate payment
* Duplicate inventory deduction
* Duplicate cancellation
* Duplicate refund
* Duplicate correction

The detailed synchronization behavior is defined in `07_Offline_Operation_and_Synchronization.md`.

---

## 53. POS Authentication

The POS must always operate under an authenticated employee session.

The system must know which employee is performing the operation.

Trusted-device status does not replace employee authentication.

Authentication, device trust, and offline authorization are defined in:

`06_Authentication_and_Trusted_Devices.md`

---

## 54. Cash Register Relationship

Each relevant POS order must be associated with the appropriate cash register and cash session.

The current business model uses:

* One cash register per branch
* One primary POS/cashier computer as the normal configuration

The architecture must not prevent future support for multiple registers.

The POS must not allow an employee to process a transaction under an invalid or unauthorized cash-session context.

---

## 55. Cashier Handover

Cashier handover follows the cash-session lifecycle.

The old cashier:

1. Closes the current cash session.
2. Completes the required handover process.

The new cashier:

1. Authenticates with their own account.
2. Opens a new cash session.
3. Continues operations under the new session.

Open orders retain their original Order UUID.

They do not need to be recreated merely because the cashier changed.

The detailed handover process is defined in:

`10_Shift_Handover.md`

---

## 56. Table Release

A table becomes available only when all relevant open orders have been resolved according to the applicable business workflow.

After paid orders are resolved, the authorized waiter/employee may clean and release the table when no other open order remains.

A helper action must not automatically release a table unless the relevant permission/workflow explicitly allows it.

---

## 57. Order Search and Identification

The POS should allow employees to identify an order using operational information such as:

* Customer-facing order number
* Order state
* Table
* Cash session
* Relevant employee/waiter
* Debt customer information where applicable

The permanent UUID remains the technical identity.

---

## 58. Order History and Historical Integrity

Historical orders must remain available according to Data Lifecycle rules.

Historical information must preserve what was actually ordered and processed.

Later changes to:

* Menu
* Price
* Recipe
* Set composition
* Product activation
* Employee permissions
* Branch configuration

must not rewrite historical transaction facts.

Important corrections must preserve original values and create traceable correction/history records.

---

## 59. Order Cancellation vs Deletion

Historical orders must not be permanently deleted through normal POS operation.

When an order is incorrect, the system uses an appropriate:

* Modification
* Cancellation
* Refund
* Correction

workflow.

Cancellation does not erase the original order.

Deletion is not used as a substitute for auditability.

---

## 60. Performance Requirements

The POS must prioritize fast daily operation.

Common actions such as:

* Opening POS
* Selecting a product
* Changing quantity
* Customizing a unit
* Adding an extra
* Applying a permitted discount
* Accepting an order
* Sending kitchen output
* Recording payment

should not be unnecessarily delayed by background processing.

Security, audit, inventory validation, printing, and synchronization must be designed so normal cashier workflows remain responsive.

---

## 61. POS Business Rules Summary

| Area                       | Rule                                              |
| -------------------------- | ------------------------------------------------- |
| Current order entry        | Physical POS                                      |
| Primary POS user           | Cashier                                           |
| Current order types        | Hall/Dine-in, Takeaway                            |
| Phone Delivery             | Future scope                                      |
| Customer database          | Not required currently                            |
| Debt customer data         | Name + phone required                             |
| Order identity             | Permanent UUID                                    |
| Client Transaction ID      | Not introduced                                    |
| Customer-facing number     | Three digits                                      |
| Number reset               | New cash session                                  |
| Lifecycle                  | Draft → Accepted → Preparing → Ready → Served     |
| Completed state            | Not used                                          |
| Draft inventory            | No deduction                                      |
| Draft kitchen              | No notification                                   |
| Accepted inventory         | Atomic deduction                                  |
| Insufficient stock         | Acceptance blocked                                |
| Negative stock             | Not allowed                                       |
| Table orders               | Multiple independent orders allowed               |
| Main waiter                | One main waiter                                   |
| First saver                | May become main waiter if no permanent assignment |
| Helper                     | Does not automatically become main waiter         |
| Help                       | Serving assistance only                           |
| Served item                | Cannot return inventory                           |
| Walkout                    | Authorized cashier/employee workflow              |
| Customization              | Unit-level                                        |
| Apply to all               | Not required                                      |
| Ingredient removal         | Quantity may become zero                          |
| Ingredient increase        | Delta inventory deduction                         |
| Extras                     | Supported                                         |
| Component swapping         | Not supported                                     |
| Accepted modification      | Inventory reconciled by delta                     |
| Modification shortage      | Entire modification rejected                      |
| Post-ticket modification   | Old ticket cancelled/updated; new ticket          |
| Cancellation               | Separate auditable event                          |
| Cancellation inventory     | Per-item Return Inventory                         |
| Served cancellation return | Never                                             |
| Refund                     | Separate from cancellation                        |
| Refund inventory           | No inventory return                               |
| Set                        | Separate bundled product                          |
| Set swapping               | Not supported                                     |
| Set price                  | Owner-defined                                     |
| Set cost                   | Derived from components                           |
| Set unavailable            | Mandatory component unavailable                   |
| Set composition            | Stable until explicitly changed                   |
| Set changes                | Effective next cash session                       |
| Inactive product           | Not shown/sold                                    |
| Product category           | Exactly one category                              |
| Kitchen routing            | Configurable by branch                            |
| Printer failure            | ERP transaction remains valid                     |
| Printer retry              | Required                                          |
| Duplicate print retry      | Must not duplicate ERP transaction                |
| Payment                    | Separate financial process                        |
| Debt                       | Supported                                         |
| Mixed payment              | Supported                                         |
| Offline POS                | Supported on trusted devices                      |
| Authentication             | Employee-specific                                 |
| Cash register              | One per branch currently                          |
| Cashier handover           | Close old session, open new session               |
| Historical deletion        | Not permitted                                     |
| Audit                      | Required                                          |
| Performance                | Fast daily POS operation                          |

---

## 62. Business Analysis Boundary

This document defines the business requirements for POS and order management.

The following remain implementation decisions:

* POS frontend technology
* Local POS storage technology
* Database schema
* Order API structure
* Exact technical state-machine implementation
* Printer communication protocol
* Printer driver architecture
* Printer retry implementation
* Offline synchronization protocol
* UI component design
* Receipt formatting implementation
* Background processing implementation
* Performance optimization techniques

These decisions must be documented later in:

* `04_Architecture`
* `05_Database`
* `06_Backend`
* `07_Frontend`
* `09_API`
* `10_Deployment`
* `11_Security`
* `12_Testing`
* `14_Operations`

---

## Related Documents

* `01_Business_Analysis/01_Product_Overview.md`
* `01_Business_Analysis/02_Business_Model.md`
* `01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
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
* `07_Frontend`
* `09_API`
* `10_Deployment`
* `11_Security`
* `12_Testing`
* `14_Operations`
* `adr/ADR-001-Documentation-First.md`

