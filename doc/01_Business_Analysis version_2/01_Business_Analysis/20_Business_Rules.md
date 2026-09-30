# Business Rules

**Document ID:** FF-BA-020
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document consolidates the core business rules of the FastFood ERP system.

The purpose is to provide a single business-level reference for rules that affect multiple modules and business processes.

These rules are derived from the approved business requirements defined throughout the Business Analysis documentation.

This document defines **what the business requires**. Technical implementation details are intentionally excluded.

---

# 2. Rule Categories

The business rules are grouped into:

* Business and Tenant Rules
* Subscription Rules
* Branch Rules
* User and Permission Rules
* Authentication and Trusted Device Rules
* Offline Rules
* Order Rules
* Cash Register Rules
* Shift Handover Rules
* Inventory Rules
* Recipe Rules
* Menu and Pricing Rules
* Payment Rules
* Refund Rules
* Employee and Payroll Rules
* Reporting Rules
* Notification Rules
* Audit Rules
* Data Lifecycle Rules
* Cross-Module Rules

---

# 3. Business and Tenant Rules

### BR-BUS-001 — Business Isolation

Every business is an independent tenant.

Data belonging to one business must not be accessible to another business.

Business isolation applies to operational data, historical data, reports, exports, offline data, synchronization, and background processing.

---

### BR-BUS-002 — Business Ownership

A business may have one or more Owners.

The maximum number of Owners is controlled by the active subscription tariff.

---

### BR-BUS-003 — Super Admin

Super Admin is the highest platform-level role.

Super Admin may manage:

* businesses;
* subscription tariffs;
* platform-level limits;
* enabled platform functions.

Super Admin is not a normal restaurant operational role.

---

### BR-BUS-004 — Business Data Scope

Business-scoped data belongs to the corresponding tenant within the platform model.

This may include:

* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* inventory;
* orders;
* payments;
* cash sessions;
* refunds;
* payroll;
* expenses;
* reports;
* notifications;
* audit history;
* synchronization records.

---

### BR-BUS-005 — Cross-Tenant Isolation

Business isolation must be preserved across:

* application operations;
* APIs;
* database operations;
* reports;
* exports;
* offline storage;
* synchronization;
* background jobs.

---

# 4. Subscription Rules

### BR-SUB-001 — Active Subscription

Normal modifying business operations require an active subscription.

---

### BR-SUB-002 — Tariff Entitlements

A subscription tariff may define:

* branch limits;
* Owner limits;
* employee limits;
* enabled functions;
* other configurable resource limits.

---

### BR-SUB-003 — Resource Limit

When a configured tariff limit is reached, creation of additional resources must be blocked.

Existing resources must not be silently deleted.

---

### BR-SUB-004 — Subscription and Permission

An operation is allowed only when both conditions are satisfied:

```text
Subscription Entitlement
        +
Employee Permission
        =
Operation Allowed
```

---

### BR-SUB-005 — Subscription Expiration

When a subscription expires:

* modifying operations become blocked;
* historical data remains available;
* applicable read-only access remains available;
* authorized Excel exports remain available.

Offline operation must not extend the subscription.

---

### BR-SUB-006 — Expired Read-Only State

An expired business enters a read-only state.

Users may, subject to their normal access permissions:

* authenticate;
* view historical information;
* view reports and history;
* export relevant information to Excel.

Normal modifying operations are blocked.

---

### BR-SUB-007 — Retention Period

The business receives a **60-calendar-day reactivation period** beginning from the authoritative subscription expiration date.

---

### BR-SUB-008 — Reactivation

If the business is reactivated before permanent deletion:

* existing business data remains intact;
* historical records remain available;
* normal operations may resume according to the new subscription;
* existing data is not recreated from scratch.

---

### BR-SUB-009 — Permanent Deletion Eligibility

If the business is not reactivated during the 60-day retention period, its business data becomes eligible for permanent deletion.

There is no additional user-accessible archive period after the retention period.

---

### BR-SUB-010 — Deletion Eligibility Check

Deletion eligibility must be evaluated using the authoritative subscription state.

A business that has been reactivated before deletion execution must not be permanently deleted.

---

### BR-SUB-011 — Tariff Downgrade

A tariff downgrade must not automatically delete existing data.

If existing resources exceed the new tariff limits:

* historical data remains;
* existing resources remain;
* creation of additional resources may be blocked;
* operations may be restricted according to the new entitlement.

---

### BR-SUB-012 — Trusted Device Restriction

A trusted device must not bypass subscription restrictions.

---

# 5. Branch Rules

### BR-BRN-001 — Branch Ownership

Every branch belongs to exactly one business.

---

### BR-BRN-002 — Branch Operational Isolation

Branch-specific operational data must remain isolated between branches according to the employee's authorized scope.

---

### BR-BRN-003 — Branch Data

Branch-specific data may include:

* employees;
* branch assignments;
* permissions;
* inventory;
* warehouses;
* cash register;
* cash sessions;
* orders;
* expenses;
* branch-specific prices;
* branch reports.

---

### BR-BRN-004 — Business-Level Data

Business-level data may include:

* business identity;
* subscription;
* tariff;
* global menu;
* approved recipes;
* role definitions;
* global settings.

---

### BR-BRN-005 — Employee Branch Assignment

An employee may be assigned to:

* one branch;
* multiple branches;
* business-wide scope where explicitly authorized.

---

### BR-BRN-006 — Branch-Specific Permissions

The same employee may have different permissions in different branches.

---

### BR-BRN-007 — Branch Context

Changing the selected branch changes the operational context.

It does not automatically grant or remove permissions.

The effective permission must always be evaluated against the selected branch scope.

---

### BR-BRN-008 — New Branch Permission Initialization

Existing role or permission configuration may be used as the initial configuration for a new branch.

The configuration may then be changed by an authorized user.

---

### BR-BRN-009 — Branch Deactivation

A branch containing historical data must be deactivated or archived rather than permanently deleted through normal operations.

---

# 6. User and Permission Rules

### BR-USR-001 — Individual Identity

Each employee must have an individual account.

Shared employee identities must not be used for normal operations.

---

### BR-USR-002 — Role-Based Permissions

Roles provide reusable permission configurations.

---

### BR-USR-003 — Employee Overrides

Individual employees may receive permission overrides where authorized.

---

### BR-USR-004 — Effective Permission

Effective permission is determined by the applicable combination of:

* employee identity;
* role;
* employee overrides;
* branch scope;
* subscription entitlement.

---

### BR-USR-005 — Permission Scope

Permissions may be:

* single-branch;
* multi-branch;
* business-wide.

---

### BR-USR-006 — Permission Grant Authority

An employee may grant only permissions and scopes that they are themselves authorized to grant.

---

### BR-USR-007 — Privilege Escalation Prevention

An employee must not be able to:

* grant unauthorized permissions to themselves;
* grant unauthorized broader scope;
* create equivalent unrestricted privileges;
* promote themselves to Owner;
* remove protected Owner privileges.

---

### BR-USR-008 — Owner Protection

Owners must be protected from unauthorized removal or privilege reduction.

---

### BR-USR-009 — Permission History

Important permission changes must preserve:

* actor;
* target employee;
* permission;
* scope;
* previous state;
* new state;
* timestamp.

---

### BR-USR-010 — Latest Explicit Command

For the same permission and scope, the latest explicit authorized command determines the current effective configuration.

Previous commands remain historically preserved.

---

### BR-USR-011 — Permission Revert

Reverting a permission creates a new historical event.

Previous permission history is never erased.

---

### BR-USR-012 — Recipe Permissions

Recipe visibility and recipe modification are separate permissions.

Menu access does not automatically grant recipe access.

---

### BR-USR-013 — Employee Deactivation

Employees with historical activity must be deactivated rather than deleted.

Historical records remain associated with the employee identity.

---

# 7. Authentication and Trusted Device Rules

### BR-AUTH-001 — Employee Authentication

Operational employees authenticate using their individual account.

---

### BR-AUTH-002 — New Device Registration

A new device must initially connect online before becoming a trusted device.

---

### BR-AUTH-003 — Trusted Device Verification

A device must be verified before receiving trusted-device offline authorization.

---

### BR-AUTH-004 — Trusted Device Offline Access

Only trusted and currently authorized devices may perform supported offline operations.

---

### BR-AUTH-005 — Device Scope

Trusted-device authorization must remain limited to the applicable:

* business;
* branch;
* employee;
* permissions;
* subscription state;
* offline validity period.

---

### BR-AUTH-006 — Device Revocation

An Owner may revoke a trusted device according to the applicable security rules.

---

### BR-AUTH-007 — Offline Authorization Security

Offline authorization must be:

* cryptographically protected;
* time-bounded;
* protected against replay;
* protected against clock manipulation.

---

### BR-AUTH-008 — Device Does Not Replace Employee Identity

Device identity does not replace employee identity.

Where relevant, both identities must remain associated with the operation.

---

# 8. Offline Rules

### BR-OFF-001 — Supported Offline Operations

Supported branch operations may continue during temporary internet outages when performed from an authorized trusted device.

---

### BR-OFF-002 — Initial Online Requirement

A device cannot perform its first trusted-device registration entirely offline.

---

### BR-OFF-003 — Offline Permission Enforcement

Offline operations must respect the employee's valid offline authorization and permissions.

---

### BR-OFF-004 — Offline Subscription Enforcement

Offline operation must not be used to bypass subscription restrictions.

---

### BR-OFF-005 — Permanent Transaction UUID

Every transaction requiring durable identity must have a permanent UUID.

A separate Client Transaction ID is not required.

---

### BR-OFF-006 — Offline Transaction Context

Offline transactions must preserve, where applicable:

* transaction UUID;
* business UUID;
* branch UUID;
* employee UUID;
* device UUID;
* cash register UUID;
* cash session UUID;
* timestamp;
* operation state.

---

### BR-OFF-007 — Idempotent Synchronization

The same transaction must not be applied multiple times during synchronization.

---

### BR-OFF-008 — Server Authority

After synchronization, the central server is authoritative for final business state.

---

### BR-OFF-009 — Rejected Offline Transactions

Rejected offline transactions must remain traceable.

They must not silently disappear.

---

### BR-OFF-010 — Offline Business and Branch Isolation

Offline data must remain isolated according to business and branch scope.

---

### BR-OFF-011 — Offline Rule Consistency

Offline-supported operations must follow the same core business rules as online operations.

Offline mode must not provide a less restrictive business workflow.

---

# 9. Order Rules

### BR-ORD-001 — Current Order Intake

The current primary order-entry method is physical cashier entry.

---

### BR-ORD-002 — Current Order Types

The current supported order types are:

* Hall / Dine-in;
* Takeaway.

Phone Delivery remains a planned order type for the relevant future workflow.

---

### BR-ORD-003 — Customer Database

A permanent customer CRM/database is not currently required.

---

### BR-ORD-004 — Delivery Information

When the applicable delivery workflow is introduced, delivery information may include:

* phone number;
* delivery address.

Such information belongs to the order unless a future customer-management model is introduced.

---

### BR-ORD-005 — Order Identity

Every order has a permanent UUID.

---

### BR-ORD-006 — Customer-Facing Order Number

The customer-facing order number is three digits.

The sequence resets when a new cash session opens.

---

### BR-ORD-007 — Order Number Is Not Identity

The three-digit customer-facing number is not the permanent order identity.

The order UUID remains the permanent identity.

---

### BR-ORD-008 — Order Lifecycle

The business order lifecycle is:

```text
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Served
```

There is no separate `Completed` order state in the current business model.

Payment is a separate financial operation and does not create a new order lifecycle state.

---

### BR-ORD-009 — Draft Order

A Draft order:

* is autosaved;
* is not sent to the kitchen;
* does not deduct inventory;
* does not occupy the table.

---

### BR-ORD-010 — Accepted Order

When an order becomes Accepted:

* inventory is validated;
* required inventory is deducted atomically;
* kitchen routing is triggered;
* the relevant table becomes occupied for the open order.

---

### BR-ORD-011 — Multiple Orders Per Table

A table may have multiple open orders.

The table is considered available only after all relevant open orders are resolved according to the business workflow.

---

### BR-ORD-012 — Main Waiter

If no permanent waiter is assigned, the first waiter who saves the applicable order becomes the main waiter for that order.

---

### BR-ORD-013 — Waiter Assignment

A waiter may be assigned according to the applicable employee and permission rules.

Permanent or temporary assignment may be supported.

---

### BR-ORD-014 — Unit-Level Customization

Each individual unit of the same product may have different customization.

An `Apply to All` operation is not supported.

---

### BR-ORD-015 — Ingredient Removal

Removing an ingredient sets the applicable quantity to zero for that order unit.

The base recipe is not changed.

---

### BR-ORD-016 — Extra Ingredient

Increasing an ingredient quantity creates an additional inventory deduction and applicable price adjustment.

---

### BR-ORD-017 — Customization Stock Validation

If additional required stock is unavailable, the entire customization change must be rejected.

The previous valid order state remains unchanged.

---

### BR-ORD-018 — Accepted Order Modification

A modification to an already accepted order is handled as a delta operation.

The system must preserve the previous state and record the inventory and price changes separately.

---

### BR-ORD-019 — Post-Kitchen Modification

If an accepted order has already reached the kitchen and is modified:

* the previous kitchen instruction is preserved;
* the updated instruction is issued;
* the change is associated with the same order;
* the change is auditable;
* inventory is reconciled according to the delta.

---

### BR-ORD-020 — Cancellation

Order or item cancellation is a separate operation from refund.

Cancellation requires the applicable permission and reason/comment.

---

### BR-ORD-021 — Inventory Return on Cancellation

For eligible non-served items, the cancellation workflow includes a `Return Inventory` option.

It is enabled by default where applicable.

---

### BR-ORD-022 — Served Inventory

Served items must never return inventory through cancellation.

---

### BR-ORD-023 — Kitchen Routing

Accepted orders must be routed to the appropriate kitchen printer according to configured branch/product/category routing.

---

### BR-ORD-024 — Printer Failure

Kitchen printer failure must not roll back the ERP order transaction.

Print status and attempts remain traceable.

---

### BR-ORD-025 — Set Product

A Set is treated as a bundle product with:

* its own selling price;
* defined component products;
* stable component composition.

Component swapping is not supported.

---

### BR-ORD-026 — Set Availability

A mandatory unavailable Set component blocks sale of the Set.

---

### BR-ORD-027 — Set Inventory

Selling a Set deducts inventory according to its component products.

---

# 10. Cash Register Rules

### BR-CASH-001 — Register per Branch

The current business model uses one cash register per branch.

The architecture must not prevent future support for multiple registers.

---

### BR-CASH-002 — Manual Opening

Cash sessions are opened manually.

---

### BR-CASH-003 — Manual Closing

Cash sessions are closed manually.

---

### BR-CASH-004 — Overnight Session

A cash session may remain open overnight.

The system must not automatically close it only because the calendar day changed.

---

### BR-CASH-005 — One Active Session

Only one active cash session is allowed for the current branch/register under the current business model.

---

### BR-CASH-006 — Session Reporting Period

A cash session's reporting period is:

```text
Opening
→
Closing
```

It is not automatically equal to a calendar day.

---

### BR-CASH-007 — Payment Types

The supported payment methods are:

* Cash;
* Card;
* Debt;
* Mixed.

---

### BR-CASH-008 — Physical Cash Entry

The cashier manually enters only the physical cash counted.

Card and other non-cash totals are derived from recorded transactions.

---

### BR-CASH-009 — Expected Cash Visibility

Expected cash remains hidden until the cashier enters the actual physical cash amount.

---

### BR-CASH-010 — Cash Difference

After actual cash is entered, the system calculates:

* no difference;
* shortage;
* overage.

---

### BR-CASH-011 — Recount

When a discrepancy exists, the workflow may require or allow a recount according to the applicable handover/closing rules.

---

### BR-CASH-012 — Discrepancy Explanation

A persistent discrepancy requires the responsible cashier to provide the required explanation/comment.

---

### BR-CASH-013 — Owner Notification

Relevant cash shortages, overages, and closing discrepancies generate the applicable Owner notification.

---

### BR-CASH-014 — Closed Session

A closed cash session remains permanently closed as an active session.

---

### BR-CASH-015 — Correction Instead of Reopening

Corrections do not reopen a closed session.

A correction is a separate historical operation against the closed session.

---

### BR-CASH-016 — Initial Correction Limit

A closed cash session initially allows a maximum of three corrections under the defined correction workflow.

---

### BR-CASH-017 — Additional Correction Authorization

After the initial correction limit is reached, an authorized Owner or Manager may authorize exactly one additional correction.

The authorization is consumed by that correction opportunity.

---

### BR-CASH-018 — Correction Authorization Record

An additional correction authorization requires:

* authorizing actor;
* requesting actor;
* reason;
* timestamp;
* audit history.

---

### BR-CASH-019 — Correction Rejection

A rejected correction request requires an explanation.

The requester cannot automatically treat the rejection as authorization.

---

### BR-CASH-020 — Correction History

Every correction preserves:

* original values;
* corrected values;
* reason;
* actor;
* timestamp.

---

### BR-CASH-021 — Opening Cash

Opening a new cash session records the opening cash amount.

---

# 11. Shift Handover Rules

### BR-HAND-001 — Handover Creates a New Cash Session

A cashier handover closes the previous cashier's cash session and creates a new cash session for the new cashier.

Handover does **not** continue the same Cash Session UUID.

---

### BR-HAND-002 — Physical Register Identity

The physical cash register remains the same.

The cash session identity changes.

```text
Same Cash Register
        ↓
Previous Cash Session
        ↓
Closed
        ↓
New Cash Session
        ↓
New Cashier
```

---

### BR-HAND-003 — Previous Cashier Responsibility

The previous cashier remains historically responsible for the previous cash session.

The previous session's discrepancies remain associated with that session and cashier.

---

### BR-HAND-004 — New Cashier Authentication

The new cashier must authenticate using their own employee account.

---

### BR-HAND-005 — New Cash Session

The new cashier opens a new cash session using the same physical register.

The new session receives a new Cash Session UUID.

---

### BR-HAND-006 — Cash Acceptance

The new cashier explicitly accepts responsibility for the physical cash according to the handover workflow.

---

### BR-HAND-007 — Physical Cash Count

The new cashier counts and enters the physical cash amount.

Expected cash remains hidden until the actual amount is entered.

---

### BR-HAND-008 — Payment Totals

The system derives:

* expected cash;
* card totals;
* debt totals;
* relevant payment totals

from recorded transactions.

The cashier physically counts and enters cash only.

---

### BR-HAND-009 — Previous Session Discrepancy

A discrepancy belonging to the previous session remains associated with the previous session.

It is not automatically transferred to the new cashier.

---

### BR-HAND-010 — Handover Confirmation Workflow

The applicable handover workflow may require the previous cashier to:

* Confirm;
* Recalculate.

There is no separate Reject action.

---

### BR-HAND-011 — Handover Completion

Responsibility transfers only after the defined handover workflow is successfully completed and the new cash session is opened.

---

### BR-HAND-012 — Open Orders During Handover

Open orders do not disappear during handover.

The new cashier may continue applicable operations according to their permissions.

---

### BR-HAND-013 — Order Identity During Handover

An existing order keeps its original Order UUID.

Historical actions remain associated with the original actor and session.

New actions are associated with the new cashier and new cash session.

---

### BR-HAND-014 — Payment Ownership During Handover

Payments recorded before the handover belong to the previous cash session.

Payments recorded after the handover belong to the new cash session.

---

### BR-HAND-015 — Inventory During Handover

Handover does not reset inventory state and must not cause duplicate inventory deductions.

---

### BR-HAND-016 — Offline Handover

Handover may be performed offline only on a trusted and authorized device.

Offline handover must not bypass authentication, permission, subscription, cash, or audit rules.

---

# 12. Inventory Rules

### BR-INV-001 — Branch Inventory

Inventory is maintained separately by branch.

---

### BR-INV-002 — Product Types

Inventory supports:

* raw materials;
* semi-finished products;
* finished products.

---

### BR-INV-003 — Product Code

Product codes are automatically generated.

---

### BR-INV-004 — Stock Source

Stock batches identify whether inventory was:

* prepared in branch;
* bought ready.

---

### BR-INV-005 — FIFO Consumption

Inventory consumption follows FIFO where applicable.

---

### BR-INV-006 — Costing Methods

Inventory costing may support:

* Average Cost;
* Last Purchase Cost.

FIFO remains the stock-consumption rule.

---

### BR-INV-007 — No Negative Inventory

Inventory must never become negative.

---

### BR-INV-008 — Order Deduction Timing

Inventory is deducted when an order is Accepted.

Draft orders do not deduct inventory.

---

### BR-INV-009 — Atomic Stock Validation

Inventory validation and deduction must prevent concurrent operations from creating negative stock.

---

### BR-INV-010 — Insufficient Inventory

An operation requiring unavailable stock must be blocked unless the applicable customization removes or reduces the relevant requirement.

---

### BR-INV-011 — Stock Count

A stock count records:

* expected quantity;
* counted quantity;
* variance.

A resulting stock adjustment requires the applicable permission and confirmation.

---

### BR-INV-012 — Inventory History

Inventory adjustments and variances remain historically traceable.

---

### BR-INV-013 — Low Stock

Low-stock thresholds generate warnings and may generate shopping-list entries.

Low stock alone does not block sale.

---

### BR-INV-014 — Out of Stock

Actual insufficient stock blocks the affected sale or operation.

---

### BR-INV-015 — Shopping List

The shopping list is advisory.

Items may be added automatically from stock conditions or manually.

A purchase does not require the shopping-list item to be marked complete first.

---

### BR-INV-016 — Purchase Record

A purchase may contain:

* supplier/source;
* quantity;
* unit price;
* total price;
* date;
* batch information;
* comment.

---

### BR-INV-017 — Purchase Receipt

A confirmed purchase receipt increases the applicable inventory quantity.

---

### BR-INV-018 — Manual Stock Exit

Manual stock exits require the applicable Inventory Adjustment permission and a reason/comment.

---

### BR-INV-019 — Equipment Broken

A product may be temporarily marked unavailable because required equipment is broken.

The affected product or Set cannot be sold while the condition is active.

---

### BR-INV-020 — Branch Transfer

Inter-branch inventory transfer is outside the current business scope.

---

### BR-INV-021 — Offline Inventory

Offline inventory operations are locally validated and later revalidated by the server during synchronization.

Synchronization must not create duplicate deductions.

---

# 13. Recipe Rules

### BR-REC-001 — Recipe Components

Recipes may contain:

* raw materials;
* semi-finished products.

---

### BR-REC-002 — Nested Dependencies

Semi-finished products may themselves have recipes.

The system must support:

```text
Raw Material
    ↓
Semi-Finished Product
    ↓
Finished Product
```

dependency tracing.

---

### BR-REC-003 — Recipe Approval

A new or modified recipe requires approval before becoming active for normal use.

---

### BR-REC-004 — Recipe Modification Permission

Recipe modification requires dedicated permission.

---

### BR-REC-005 — Global Recipe

Approved recipes are business-level and are consistent across branches under the current business model.

---

### BR-REC-006 — Recipe History

Previous recipe versions are archived and remain historically traceable.

---

### BR-REC-007 — Product With Recipe

A product with historical recipe relationships cannot be permanently deleted through normal operations.

It must be archived/inactivated where applicable.

---

### BR-REC-008 — Recipe Visibility

Recipe visibility is controlled separately from normal menu visibility.

---

### BR-REC-009 — Shrinkage and Loss

Prepared items may include configured shrinkage/loss percentages.

---

### BR-REC-010 — Semi-Finished Production

Semi-finished production uses the applicable recipe and actual output quantity.

Recipe quantities scale proportionally according to the actual production quantity.

---

### BR-REC-011 — Recipe Change Effective Time

Approved recipe changes become effective from the next cash session.

Existing historical transactions are not rewritten.

---

# 14. Menu and Pricing Rules

### BR-MENU-001 — Global Menu

The business has a central/global menu.

---

### BR-MENU-002 — Branch Menu

Branches may enable or disable permitted products from the global menu.

---

### BR-MENU-003 — Product Category

Each product belongs to exactly one menu category.

---

### BR-MENU-004 — Product Activation

A product may be active or inactive.

Inactive products are not available for new sale but remain in historical data.

---

### BR-MENU-005 — Product Availability

The following concepts are distinct:

* product active/inactive;
* branch menu availability;
* physical stock availability;
* equipment-broken availability.

---

### BR-MENU-006 — Branch Price Override

A branch may override the global product price when the user has the required permission.

The override applies only to that branch.

---

### BR-MENU-007 — Historical Prices

Historical transactions retain the price applicable at transaction time.

Later price changes do not rewrite historical transactions.

---

### BR-MENU-008 — Open Order Price

Open orders must not be silently rewritten because the current product price changes.

---

### BR-MENU-009 — Recipe and Price Independence

Recipe changes do not automatically rewrite historical order prices.

---

### BR-MENU-010 — Discounts

Discounts are separate from the base product price.

Applying a discount does not modify the global or branch product price.

---

### BR-MENU-011 — Standard Product Price

A cashier must not freely modify the normal product price.

Any special price adjustment must use an authorized business mechanism.

---

### BR-MENU-012 — Custom Order Markup

Authorized custom order pricing may use a markup from **0% to 100%**.

The final custom price is calculated from Last Purchase Cost:

```text
Final Price =
Last Purchase Cost × (1 + Markup / 100)
```

This is a controlled custom-pricing mechanism and does not grant unrestricted price editing to cashiers.

---

### BR-MENU-013 — Product Images

Product images are optional.

---

### BR-MENU-014 — Taxes

Taxes are currently included in product prices.

A separate tax-detail engine is outside the current business scope.

---

### BR-MENU-015 — Set Composition

A Set has its own selling price and stable component composition.

Underlying product or recipe changes do not automatically rewrite the existing Set composition.

---

### BR-MENU-016 — Set Changes

Changing a Set creates a new configuration/version.

The new Set configuration becomes effective from the next cash session.

Historical Set transactions retain their original composition.

---

### BR-MENU-017 — Set Component Availability

A mandatory unavailable component blocks sale of the Set.

Component swapping is not supported.

---

### BR-MENU-018 — Offline Menu Configuration

Trusted offline devices use the latest valid authorized menu configuration available to them.

The server remains authoritative after synchronization.

---

# 15. Payment Rules

### BR-PAY-001 — Supported Payment Methods

The supported payment methods are:

* Cash;
* Card;
* Debt;
* Mixed.

---

### BR-PAY-002 — Payment Identity

Every payment has a unique transaction identity and must be idempotent.

---

### BR-PAY-003 — Payment Context

Where applicable, a payment remains associated with:

* business;
* branch;
* order;
* employee;
* device;
* cash register;
* cash session;
* payment method;
* amount;
* timestamp;
* status.

---

### BR-PAY-004 — Cash Relationship

Cash payments affect the physical cash session.

---

### BR-PAY-005 — Card Relationship

Card payments are recorded separately from physical cash.

---

### BR-PAY-006 — Debt

Debt supports:

* one debt customer record;
* multiple debt orders;
* partial repayment;
* duplicate phone numbers where necessary.

Historical orders retain the customer information applicable when the order was created.

---

### BR-PAY-007 — Mixed Payment

A single order may be paid using multiple payment portions.

Only the cash portion contributes to physical cash reconciliation.

---

### BR-PAY-008 — Successful Payment

Successful payment closes the financial obligation of the order according to the applicable payment rules.

Payment completion does not create a separate `Completed` order state.

---

### BR-PAY-009 — Duplicate Payment Protection

The same payment transaction must not be applied more than once.

---

### BR-PAY-010 — Offline Payment

Supported payment operations may continue offline on authorized trusted devices.

The server revalidates them during synchronization.

---

### BR-PAY-011 — External Card Authorization

Recording a card payment in the ERP does not by itself mean that an external card processor has authorized the payment.

External processor integration is a separate concern.

---

### BR-PAY-012 — Payment Correction

Completed payment records must not be silently overwritten.

Corrections are represented by separate authorized financial operations.

---

### BR-PAY-013 — Historical Payment Snapshot

Historical payment information remains associated with the transaction state at the time of payment.

---

# 16. Refund Rules

### BR-REF-001 — Refund Permission

Refunds require the appropriate permission.

---

### BR-REF-002 — Refund Authorization

Where configured, refunds require approval by an authorized employee.

---

### BR-REF-003 — Refund Reason

Every refund requires a mandatory reason.

---

### BR-REF-004 — Refund Types

Refunds may be:

* full;
* partial;
* item-level;
* quantity-level.

---

### BR-REF-005 — Refund Methods

Current refund methods are:

* Cash;
* Card.

---

### BR-REF-006 — Manual Refund

Refund processing is manual.

Automatic physical cash/card reversal is outside the current business scope.

---

### BR-REF-007 — Refund Does Not Rewrite Original Payment

The original payment and order history remain unchanged.

The refund is recorded as a separate financial operation.

---

### BR-REF-008 — Refund and Inventory

A refund does not automatically return inventory.

---

### BR-REF-009 — Served Items

Served items must never return inventory as a consequence of a refund.

---

### BR-REF-010 — Cash Refund

A cash refund affects the applicable cash session.

---

### BR-REF-011 — Card Refund

A card refund retains the original card-payment context.

---

### BR-REF-012 — Large Refund

A refund exceeding the configured significant-refund threshold generates the applicable alert.

---

### BR-REF-013 — Cancellation Is Not Refund

Order cancellation and financial refund are separate business operations.

---

# 17. Employee and Payroll Rules

### BR-EMP-001 — Employee Identity

Every employee has an individual identity.

---

### BR-EMP-002 — Employee Lifecycle

Employee lifecycle includes:

```text
Created
  ↓
Active
  ↓
Inactive
```

Historical employee data remains after deactivation.

---

### BR-EMP-003 — Employee Creation

Employee creation is permission-controlled.

---

### BR-EMP-004 — Manager Employee Creation

A Manager may create employees only when the required permission has been explicitly granted.

A Manager cannot grant themselves additional authority.

---

### BR-EMP-005 — Attendance

Attendance rules may differ according to employee role and configuration.

---

### BR-EMP-006 — Salary Models

The system supports:

* Fixed;
* Percentage;
* Shift;
* Hybrid;
* Daily Pay;
* Bonuses.

---

### BR-EMP-007 — Salary Configuration Separation

Salary configuration is separate from operational permissions.

Normal operational permissions must not allow an employee to modify their own salary configuration.

---

### BR-EMP-008 — Salary Change History

Salary changes preserve:

* previous configuration;
* new configuration;
* effective date;
* actor;
* reason.

---

### BR-EMP-009 — Payroll Period

Payroll is calculated for defined payroll periods.

---

### BR-EMP-010 — Payroll Calculation Snapshot

A finalized payroll calculation preserves the information necessary to explain how the result was calculated.

---

### BR-EMP-011 — Payroll Correction

Finalized payroll is not silently overwritten.

Corrections are separate and auditable.

---

### BR-EMP-012 — Payroll Access

Payroll access is permission-controlled.

Viewing one's own payroll and managing other employees' payroll may require different permissions.

---

### BR-EMP-013 — Branch Salary Scope

Branch-specific salary configuration remains associated with the applicable employee/branch scope.

---

### BR-EMP-014 — Salary Due Notification

Relevant authorized users may receive salary-due notifications.

---

### BR-EMP-015 — Deactivated Employee

Deactivation does not remove historical attendance, salary, payroll, order, payment, or audit records.

---

# 18. Reporting Rules

### BR-REP-001 — Report Permissions

Report access is permission-controlled and follows business/branch scope.

---

### BR-REP-002 — Report Categories

Reports may cover:

* sales;
* orders;
* payments;
* cash sessions;
* cashiers;
* discrepancies;
* refunds;
* discounts;
* inventory;
* inventory movements;
* inventory variances;
* purchases;
* employees;
* attendance;
* payroll;
* expenses;
* branch performance;
* audit history;
* change history.

---

### BR-REP-003 — Excel Export

Excel (`.xlsx`) is the supported report export format.

PDF and CSV are outside the current scope.

---

### BR-REP-004 — Manual Report Period

A manually generated report may cover a maximum period of one month.

---

### BR-REP-005 — Invalid Date Range

A report request where the start date is after the end date must be rejected.

---

### BR-REP-006 — Open Cash Sessions

Open cash sessions are excluded from finalized cash reports.

---

### BR-REP-007 — Empty Reports

Reports are generated even when no relevant data exists.

Values with no data are represented as `0` where applicable.

---

### BR-REP-008 — Automatic Monthly Report

The monthly report process starts on the last calendar day of the month.

If an applicable cash session remains open, finalization waits until the required session is closed.

---

### BR-REP-009 — Report Generation Failure

Failed automatic report generation must be:

* recorded;
* retried where applicable;
* reported to authorized users when persistent.

---

### BR-REP-010 — Report Version

Each materially generated report state is treated as a report version.

---

### BR-REP-011 — Immutable Report Versions

Previous report versions cannot be silently modified.

---

### BR-REP-012 — No Unnecessary Version

If the same report period is requested and relevant underlying data has not changed, a new version is not required.

---

### BR-REP-013 — Selective Re-Versioning

Only reports affected by relevant business-data changes require a new version.

---

### BR-REP-014 — Correction and Reports

When a correction changes data relevant to a report, the affected report receives a new version.

The previous version remains unchanged.

---

### BR-REP-015 — No-Change Correction

A correction that does not change any report-relevant result does not require a new report version.

---

### BR-REP-016 — Report Creation Source

Each report version preserves its creation source, such as:

* automatic generation;
* manual generation;
* correction-driven regeneration.

---

### BR-REP-017 — Report Retention

Generated report versions are retained and cannot be deleted through normal business operations.

---

### BR-REP-018 — Report Generation and POS

Report generation must not block or materially disrupt normal POS operations.

---

# 19. Notification Rules

### BR-NOT-001 — Permission Scope

Notifications must respect user permissions.

---

### BR-NOT-002 — Branch Scope

Branch-specific notifications must respect branch access.

---

### BR-NOT-003 — Low Stock Alert

Low-stock conditions generate the applicable warning/alert.

---

### BR-NOT-004 — Out-of-Stock Alert

Actual out-of-stock conditions generate the applicable alert.

---

### BR-NOT-005 — Subscription Lifecycle Alerts

The system may notify authorized users about:

* subscription expiration;
* read-only state;
* approaching deletion deadline;
* other relevant lifecycle states.

---

### BR-NOT-006 — Salary Due Alert

Relevant authorized users may receive salary-due notifications.

---

### BR-NOT-007 — Large Refund Alert

Significant refunds generate the applicable alert.

---

### BR-NOT-008 — Inventory Variance Alert

Significant inventory variance generates the applicable alert.

---

### BR-NOT-009 — Branch Loss Alert

A significant current-day branch loss generates the applicable alert according to the configured business rule.

---

### BR-NOT-010 — Cash Discrepancy

Relevant cash shortage or overage generates the applicable notification.

---

### BR-NOT-011 — Cash Close Comment

A cashier's relevant closing comment may generate an Owner notification and corresponding report/history entry.

---

### BR-NOT-012 — Handover Notifications

The handover workflow may generate notifications for the relevant cashier and authorized management users according to the configured workflow.

---

### BR-NOT-013 — Correction Notifications

Correction requests, authorizations, rejections, and completed corrections may generate notifications for relevant users.

---

### BR-NOT-014 — Report Ready

Authorized users may receive report-ready notifications.

---

### BR-NOT-015 — Report Change

Authorized users may receive notifications when a report is re-versioned because relevant business data changed.

---

### BR-NOT-016 — No-Change Notification

A correction that produces no actual report-affecting change must not generate a report-change notification.

---

### BR-NOT-017 — Persistent Alerts

Alerts representing an unresolved condition may remain active until the condition is resolved.

Historical alert records remain preserved.

---

### BR-NOT-018 — Duplicate Notification Prevention

The same business event must not unnecessarily generate repeated duplicate notifications.

---

### BR-NOT-019 — Notification Does Not Grant Permission

A notification cannot grant the recipient permission to perform the related action.

---

### BR-NOT-020 — Notification Failure Isolation

Failure of a non-critical notification must not roll back or fail the underlying business transaction.

---

# 20. Audit Rules

### BR-AUD-001 — Important Actions

Important business and administrative actions must be auditable.

---

### BR-AUD-002 — Actor

The responsible employee or system process must be identifiable.

---

### BR-AUD-003 — Business Context

Important audit events preserve applicable:

* business;
* branch;
* employee;
* device;
* cash register;
* cash session;
* related entity;
* transaction identity.

---

### BR-AUD-004 — Old and New Values

Important changes preserve old and new values where applicable.

---

### BR-AUD-005 — Reason

Required reasons/comments remain part of the historical record.

---

### BR-AUD-006 — Immutable Audit

Audit records cannot be silently edited or deleted through normal business operations.

---

### BR-AUD-007 — Correction History

Corrections create new historical events rather than erasing previous events.

---

### BR-AUD-008 — Permission History

Permission changes remain historically traceable.

---

### BR-AUD-009 — Employee History

Employee deactivation does not remove historical actions.

---

### BR-AUD-010 — Offline History

Offline transactions remain traceable after synchronization.

---

### BR-AUD-011 — Cash Session History

Cash session history preserves:

* opening;
* closing;
* cashier;
* opening cash;
* closing cash;
* discrepancies;
* corrections;
* authorization events.

---

### BR-AUD-012 — Handover History

A handover preserves:

* previous cashier;
* previous cash session;
* new cashier;
* new cash session;
* physical register;
* cash acceptance;
* relevant discrepancy;
* handover actions.

A handover does **not** reuse the previous Cash Session UUID.

---

### BR-AUD-013 — Financial History

Payments and refunds remain historically linked to their original financial context.

Corrections do not erase original financial records.

---

### BR-AUD-014 — Payroll History

Salary and payroll changes remain historically traceable.

---

### BR-AUD-015 — Report History

Report versions remain historically traceable.

---

### BR-AUD-016 — Audit Access

Audit history follows business, branch, and permission authorization.

---

# 21. Data Lifecycle Rules

### BR-LIFE-001 — Deactivation

Deactivation preserves historical data.

---

### BR-LIFE-002 — Historical Records

Important historical records must not be silently deleted.

---

### BR-LIFE-003 — Entity Lifecycle

Where applicable, entities follow a lifecycle such as:

```text
Active
  ↓
Inactive / Archived
```

rather than destructive deletion.

---

### BR-LIFE-004 — Subscription Expiration

Subscription expiration starts the read-only lifecycle.

---

### BR-LIFE-005 — Retention Period

The expired business receives 60 calendar days for reactivation.

---

### BR-LIFE-006 — Permanent Deletion Eligibility

After 60 days without reactivation, the business becomes eligible for permanent deletion.

---

### BR-LIFE-007 — Deletion Warning

Authorized users receive appropriate warnings before the permanent deletion deadline.

---

### BR-LIFE-008 — No Additional User Archive

There is no additional user-accessible archive period after the 60-day retention period.

---

### BR-LIFE-009 — Tenant-Safe Deletion

Permanent deletion affects only the target business.

---

### BR-LIFE-010 — Deletion Scope

Permanent deletion includes applicable business-owned data, including:

* business configuration;
* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* inventory;
* orders;
* payments;
* cash sessions;
* handovers;
* refunds;
* discounts;
* payroll;
* expenses;
* reports;
* report versions;
* notifications;
* audit history;
* synchronization records;
* other business-owned data.

---

### BR-LIFE-011 — Cross-Reference Handling

Deletion must not leave the deleted business accessible through another business's operational context.

---

### BR-LIFE-012 — Offline Expiration

An expired or deleted business cannot use an offline device to bypass lifecycle restrictions.

---

### BR-LIFE-013 — Post-Deletion Synchronization

After permanent deletion, the affected business cannot continue normal synchronization or business operations.

---

### BR-LIFE-014 — Deletion Audit

The platform retains sufficient platform-level information to demonstrate that the deletion process occurred.

This record must not expose deleted business data through normal business access.

---

### BR-LIFE-015 — Deletion Failure

A failed deletion process must not be represented as successful.

Failure must remain traceable and the platform must support appropriate retry or operational handling.

---

### BR-LIFE-016 — Data Export Before Deletion

During the retention period, authorized users may export relevant business information through supported Excel exports.

---

# 22. Cross-Module Rules

### BR-CROSS-001 — Subscription + Permission

Neither subscription entitlement nor employee permission alone is sufficient.

Both must permit the operation.

---

### BR-CROSS-002 — Business + Branch Isolation

Business and branch scope must remain valid across all related modules.

---

### BR-CROSS-003 — Historical Data Integrity

Current configuration changes must not rewrite historical transactions.

This applies to:

* products;
* prices;
* recipes;
* employees;
* permissions;
* payroll;
* payments;
* refunds;
* reports.

---

### BR-CROSS-004 — Correction Instead of Overwrite

When an important completed record requires correction, the correction process must preserve the original state.

---

### BR-CROSS-005 — Auditability

Important cross-module operations must preserve their relationship to the relevant business entity and transaction.

---

### BR-CROSS-006 — Offline Consistency

Offline operations must follow the same core business rules as online operations whenever the operation is supported offline.

---

### BR-CROSS-007 — Server Authority

After synchronization, the central server is authoritative for final business state.

---

### BR-CROSS-008 — Historical Actor Preservation

When responsibility changes, previous actions remain associated with the original actor.

New actions are associated with the new actor.

This is especially applicable to:

* cashier handover;
* order modifications;
* payments;
* corrections;
* inventory operations;
* payroll;
* permissions.

---

### BR-CROSS-009 — No Silent Deletion

A record with historical business significance must be archived, deactivated, corrected, or otherwise preserved according to its lifecycle rather than silently deleted.

---

### BR-CROSS-010 — Transaction Atomicity

Where a business operation contains multiple dependent changes, the operation must not leave a partially applied business state.

For example, an accepted order requiring inventory deduction must not become accepted while the corresponding required inventory deduction fails.

---

# 23. Business Rule Priority

When multiple business rules apply to the same operation, the applicable control layers are considered in the following order:

```text
Business / Tenant Isolation
        ↓
Subscription Entitlement
        ↓
Branch Scope
        ↓
Employee Identity
        ↓
Role
        ↓
Permission / Override
        ↓
Business Operation Rules
        ↓
Transaction State
        ↓
Audit / History
```

A lower-level permission cannot override a higher-level restriction.

For example:

An employee with permission to edit an order cannot perform the modification when the subscription state blocks modifying operations.

Similarly, a permission granted to an employee in one branch does not automatically authorize the same operation in another branch.

---

# 24. Business Rule Enforcement

Business rules must be enforced consistently across all relevant interfaces.

A rule must not be bypassable simply by using:

* another UI screen;
* another API endpoint;
* offline mode;
* synchronization;
* report export;
* background processing;
* another branch context;
* a different device.

The same business rule must produce the same business-level result regardless of the interface through which the operation is attempted.

---

# 25. Business Rule Changes

Changes to these business rules must be documented before implementation.

A significant business rule change should identify:

* affected rule;
* previous behavior;
* new behavior;
* reason;
* affected modules;
* related documentation.

Architectural or technical decisions resulting from business-rule changes should be documented separately in the ADR system where appropriate.

Business rules remain the authoritative business-level reference when detailed module documents describe the same requirement.

---

# 26. Business Rule Summary

The core business model can be summarized as:

```text
Business
  ↓
Subscription
  ↓
Branches
  ↓
Employees
  ↓
Roles + Permissions + Branch Scope
  ↓
Business Operations
  ↓
Transactions
  ↓
Reports + Notifications
  ↓
Audit + Change History
  ↓
Lifecycle / Retention / Deletion
```

The system must preserve these relationships throughout the business lifecycle.

---

# 27. Business Boundaries

This document defines business rules only.

It does not define:

* database schema;
* API contracts;
* authentication algorithms;
* encryption algorithms;
* exact token formats;
* infrastructure;
* deployment architecture;
* programming language;
* framework selection;
* database indexes;
* queue technology;
* caching technology;
* cloud provider;
* server topology;
* exact synchronization protocol;
* exact database transaction implementation;
* exact backup/deletion implementation.

These concerns belong to later documentation sections.

---

# 28. Related Documents

* `01_Product_Overview.md`
* `02_Business_Model.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `19_Data_Lifecycle_and_Deletion.md`

