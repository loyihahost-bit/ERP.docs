# POS and Order Management

**Document ID:** FF-BA-008
**Status:** Accepted
**Version:** 1.0
**Scope:** Point of Sale (POS), order lifecycle, order types, order items, modifications, printing, and order-related business rules
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
* Receipt and kitchen printing
* Offline operation
* Auditability

The POS must remain lightweight and practical for everyday restaurant operations.

---

## 2. POS Operating Model

The initial POS model is based on physical order entry by restaurant employees.

The primary order-entry user is the cashier.

The system must support the following order types:

1. Hall / Dine-in
2. Takeaway
3. Phone Delivery

Online customer ordering is outside the current scope.

Future integrations such as:

* Customer mobile applications
* Online ordering
* Telegram ordering
* External delivery platforms
* Full CRM

must not require redesigning the core order model.

---

## 3. Order Identity

Every order must have a permanent unique transaction identity.

The order uses the existing UUID model.

The UUID is the primary technical identity of the order and must remain unchanged throughout its lifecycle.

The customer-facing order number is separate from the UUID.

Therefore:

**Order UUID ≠ Customer-Facing Order Number**

The UUID must be used for synchronization, auditability, and reliable identification.

---

## 4. Customer-Facing Order Number

The POS displays a short customer-facing order number for practical restaurant operations.

The current requirement is a three-digit order number.

The three-digit number:

* Is easy to communicate to customers
* Is displayed on relevant restaurant screens and receipts
* Resets when a new cash session begins
* Is not the permanent identity of the order

The same three-digit number may therefore appear again in a later cash session.

Historical records must remain distinguishable through the order UUID and cash-session information.

---

## 5. Order Types

### 5.1 Hall / Dine-in

The order is consumed inside the restaurant.

The order may be associated with the relevant hall/table information where the branch uses tables.

The system should allow employees to see the current table state where applicable.

A table may be shown as:

* Available
* Occupied / Busy
* Waiting for order

The exact table workflow may be expanded later without changing the basic order identity.

---

### 5.2 Takeaway

The customer receives the order for consumption outside the restaurant.

The order does not require a permanent customer profile.

The order remains associated with the employee, branch, cash session, and other relevant transaction information.

---

### 5.3 Phone Delivery

The customer places an order through the restaurant's phone.

The system records the delivery information required to complete the order.

At minimum, the current model may store:

* Phone number
* Delivery address

A permanent customer record is not required.

The delivery information belongs to the order itself.

---

## 6. Customer Data

The current system does not require a permanent customer database.

Customer information may be stored directly on the relevant order.

This avoids introducing unnecessary CRM complexity at the initial business-analysis stage.

The order may contain customer-related information such as:

* Phone number
* Delivery address
* Other operational notes where required

Future customer management functionality may build on the existing order structure.

---

## 7. Order Creation

A cashier creates an order through the POS.

When an order is created, the system associates it with the relevant operating context.

Important order context includes:

* Order UUID
* Business
* Branch
* Employee
* Device
* Cash register
* Cash session
* Order type
* Creation time
* Order state

The system must not allow an order to be silently created under the wrong business or branch.

---

## 8. Product Selection

The cashier selects products from the active branch menu.

Only products available to the branch should normally be selectable.

The POS must display the current applicable selling price.

The menu and product availability rules are defined in the Menu and Pricing document.

The POS must use the approved product and pricing configuration available to the current branch.

---

## 9. Order Items

An order may contain multiple products.

Each order item must preserve the information required to understand what was actually ordered.

Relevant information includes:

* Product
* Quantity
* Applied price
* Modifications
* Extras
* Discount, where applicable
* Relevant comments
* Final item amount

Historical orders must not depend exclusively on the current product configuration.

If a product price or recipe changes later, historical orders must continue to represent the original transaction.

---

## 10. Quantity

The cashier may change the quantity of an order item when permitted.

The system must recalculate the order amount according to the applicable price and quantity.

Inventory deduction must reflect the actual ordered quantity.

The system must not allow invalid quantities according to the product's business rules.

---

## 11. Product Modifications

The POS must support permitted product modifications.

Selecting **Modify** on an item may display the relevant recipe components and inventory-related components when the employee has permission to view them.

Permitted modifications may include:

* Adding a component
* Removing a component
* Adding an approved extra

The modification must affect the order price when the business rule requires it.

---

## 12. Recipe Component Removal

When a customer removes a recipe component:

* The component is removed from the order configuration.
* The applicable price reduction is calculated automatically where defined.
* The corresponding inventory deduction is adjusted.

The system must not treat the removed component as consumed.

This rule applies only where the product recipe and modification rules permit the component to be removed.

---

## 13. Additional Components and Extras

The POS must support approved extras/add-ons.

When an extra has an associated price:

* The order amount increases accordingly.
* The extra is recorded as part of the order.
* Relevant inventory consumption is applied.

Extras must be based on approved business configuration.

Employees must not create arbitrary inventory-consuming extras unless the relevant permission and business configuration allow it.

---

## 14. Component Swapping

Component swapping is not supported in the current business model.

For example, the system must not treat:

**Remove Component A + Add Component B**

as an automatic component exchange unless a separately defined business rule supports it.

Employees may use supported removal and extra mechanisms where appropriate.

More advanced customization can be introduced later without changing the basic order model.

---

## 15. Non-Recipe Changes

Not every order modification needs to be represented as a recipe component.

For permitted non-recipe changes, the employee may record the change as a comment.

The comment must provide enough operational information for the restaurant to understand the requested preparation or handling instruction.

Such comments must not silently change inventory unless a configured inventory-affecting modification exists.

---

## 16. Discounts

The POS supports discounts.

A discount must be applied according to the employee's permission and the configured business rules.

The order must retain enough information to determine:

* Original amount
* Discount
* Final amount
* Employee responsible for the discount
* Relevant reason or configuration where required

Discounts must be traceable in historical records.

---

## 17. Order Comments

Order comments may be used for operational instructions or explanations that are not represented by structured fields.

Comments must not be used to silently bypass structured business rules.

Where a business rule requires a structured action, such as a refund reason or cash-session correction reason, the relevant structured field remains mandatory.

---

## 18. Order Editing

An order may be edited while it is still in an editable state and the employee has the required permission.

Typical editable information may include:

* Quantity
* Product selection
* Permitted modifications
* Extras
* Discounts
* Comments
* Other allowed order information

The system must preserve important changes through the appropriate audit mechanism.

---

## 19. Order State

An order progresses through business states.

The exact technical state machine will be defined later, but the business lifecycle must distinguish at least:

* Order creation
* Order acceptance
* Preparation / kitchen processing
* Payment
* Completion / closure

The system must prevent invalid transitions.

For example, a fully closed order must not simply become an active order again without an authorized business process.

---

## 20. Order Acceptance

The cashier confirms the order after entering the required information.

After acceptance, the system sends the relevant information to the configured kitchen printers.

The order number must be included in the kitchen-facing information so restaurant staff can identify the order.

The system must ensure that the accepted order is associated with the correct branch and cash session.

---

## 21. Kitchen Printing

The POS must support kitchen printer routing.

Different products or categories may be assigned to different printers.

For example:

* Pizza items → Pizza printer
* Lavash items → Lavash printer

The routing configuration belongs to the branch.

A single order may therefore produce output on multiple printers.

Each printer should receive only the information relevant to its configured preparation area.

---

## 22. Printer Output

Kitchen printer output should contain the information necessary for preparation.

Typical information includes:

* Order number
* Relevant order items
* Quantities
* Permitted modifications
* Extras
* Preparation comments

Customer payment information does not need to be included in kitchen output unless separately required by configuration.

---

## 23. Printer Failure

If a configured printer is unavailable, the system must not silently treat the order as successfully printed.

The POS should make the printing problem visible to the responsible user.

The order itself must remain identifiable and must not be duplicated merely because a print attempt failed.

The technical retry and printer recovery mechanism belongs to the deployment and printer-integration design.

---

## 24. Payment Relationship

Payment is a separate stage of the order lifecycle.

The order must retain its payment information after payment is completed.

The payment process is defined in detail in:

`14_Payments_Discounts_and_Refunds.md`

The POS must not mark an order as successfully paid without recording the corresponding payment state.

---

## 25. Inventory Deduction

Order processing must affect inventory according to the approved product and recipe configuration.

For recipe-based products:

**Order → Recipe → Inventory Consumption**

The inventory system must deduct the relevant components.

For products with permitted modifications, the final inventory consumption must reflect those modifications.

Inventory deduction must not be based solely on the product's current recipe if the order was created under a different approved configuration.

Historical order data must preserve the relevant transaction context.

---

## 26. Insufficient Inventory

Negative inventory is not allowed.

If the system determines that an order cannot be fulfilled because required inventory is insufficient, the affected order operation must be blocked.

The cashier may remove or modify the affected item where permitted.

After modification, the system must recalculate:

* Order amount
* Required inventory
* Applicable discounts
* Final payable amount

If sufficient inventory becomes available, the operation may proceed according to normal rules.

---

## 27. Order and Inventory Consistency

The system must avoid a situation where:

* The customer is charged for an item that the system did not record correctly,
* Inventory is deducted without a corresponding order,
* An order is duplicated because of a synchronization retry,
* A modification changes the price but not the relevant inventory effect.

Order, payment, and inventory records must remain linked through the appropriate transaction identities.

---

## 28. Offline POS

The POS must support approved offline operations on trusted devices.

Offline order creation follows the rules defined in:

`07_Offline_Operation_and_Synchronization.md`

The cashier should be able to continue supported order operations without manually recreating transactions after reconnection.

Every offline order must retain its UUID and operating context.

---

## 29. POS Authentication

The POS must always operate under an authenticated employee session.

The system must know which employee is performing the order operation.

Trusted-device status does not replace employee authentication.

Authentication and permission rules are defined in:

`06_Authentication_and_Trusted_Devices.md`

---

## 30. Cash Register Relationship

Each order processed through the POS must be associated with the relevant cash register and cash session when the order is part of cash-session operations.

The current business assumption is one cash register per branch.

The architecture must not prevent future support for multiple registers.

The POS must not allow a cashier to process an order under an invalid or unauthorized cash-session context.

---

## 31. Open Orders During Shift Handover

During a cashier handover, open orders must transfer according to the cash-session handover rules.

The new cashier accepts responsibility through their own authenticated account.

Open orders remain associated with their original order identity.

The responsible employee history must remain traceable.

The order does not need to be recreated merely because the cashier changed.

---

## 32. Order History

Historical orders must remain available according to the system's data lifecycle rules.

Historical order information must preserve the information necessary to understand what was actually sold.

Later changes to:

* Menu
* Price
* Recipe
* Employee permissions
* Branch configuration

must not rewrite historical order facts.

---

## 33. Order Corrections

Order mistakes may be corrected where permitted.

Corrections must not silently overwrite important historical information.

Where the correction changes a significant business value, the system must preserve:

* Original value
* New value
* Employee responsible
* Time
* Reason where required

The detailed audit and correction model is defined in the relevant Audit and Business Rules documents.

---

## 34. Order Cancellation

Cancellation must be treated as a business event rather than silent deletion.

A cancelled order must remain traceable in history.

The exact cancellation rules depend on the order state.

Once an order has entered a financial or inventory-affecting state, cancellation may require an authorized process rather than simple deletion.

---

## 35. Order Deletion

Customer-facing users must not be able to permanently delete historical orders through normal POS operation.

Where an order is incorrect, the system should use an appropriate correction, cancellation, or reversal process.

This preserves business history and prevents silent manipulation of restaurant records.

---

## 36. Order Search and Identification

The POS should allow employees to identify an order using practical operational information such as:

* Customer-facing order number
* Current order state
* Cash session
* Relevant table
* Delivery information where applicable

The permanent UUID remains the system identity even if it is not normally displayed to customers.

---

## 37. Performance Requirements

The POS must prioritize fast daily operation.

Common actions such as:

* Opening the POS
* Selecting a product
* Changing quantity
* Adding an extra
* Applying a permitted discount
* Accepting an order
* Sending kitchen output

should not be unnecessarily delayed by complex background processing.

Security, audit, inventory validation, and synchronization must be designed so that normal cashier workflows remain responsive.

---

## 38. POS Business Rules Summary

| Area                     | Rule                                            |
| ------------------------ | ----------------------------------------------- |
| Order entry              | Physical cashier is the current primary channel |
| Order types              | Hall/Dine-in, Takeaway, Phone Delivery          |
| Customer database        | Not required currently                          |
| Delivery data            | Phone and address stored on order               |
| Order identity           | Permanent UUID                                  |
| Customer order number    | Three digits                                    |
| Order number reset       | At new cash session                             |
| Product selection        | From permitted active branch menu               |
| Modifications            | Supported where configured                      |
| Recipe component removal | Adjusts price and inventory                     |
| Extras                   | Supported                                       |
| Component swapping       | Not supported                                   |
| Non-recipe changes       | May use comments                                |
| Discounts                | Supported with permission                       |
| Negative stock           | Not allowed                                     |
| Insufficient stock       | Relevant operation blocked                      |
| Kitchen printing         | Supported                                       |
| Printer routing          | Configurable by product/category                |
| Payment                  | Separate lifecycle stage                        |
| Offline orders           | Supported on authorized devices                 |
| Employee identity        | Always traceable                                |
| Order deletion           | Historical deletion not permitted               |
| Corrections              | Auditable                                       |
| Cash session             | Order associated with relevant session          |
| Shift handover           | Open orders transfer without recreation         |
| Historical data          | Must preserve original transaction facts        |

---

## 39. Business Analysis Boundary

This document defines the business requirements for POS and order management.

The following remain implementation decisions:

* POS frontend technology
* Local POS storage technology
* Order API structure
* Database schema
* Exact order state machine implementation
* Printer communication protocol
* Printer driver architecture
* Offline synchronization protocol
* UI component design
* Receipt formatting implementation
* Performance optimization techniques

These decisions must be documented later in the Architecture, Database, Backend, Frontend, Deployment, and Operations documentation.

---

## Related Documents

* `01_Business_Analysis/01_Product_Overview.md`
* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `01_Business_Analysis/12_Products_and_Recipes.md`
* `01_Business_Analysis/13_Menu_and_Pricing.md`
* `01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `01_Business_Analysis/18_Audit_and_Change_History.md`
* `01_Business_Analysis/20_Business_Rules.md`
* `05_Database`
* `06_Backend`
* `07_Frontend`
* `10_Deployment`
* `14_Operations`

