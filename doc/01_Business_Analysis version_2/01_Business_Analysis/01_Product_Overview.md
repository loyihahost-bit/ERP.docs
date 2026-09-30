# Product Overview

**Document ID:** BA-01
**Status:** Accepted
**Version:** 2.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

FastFood ERP is a SaaS-based ERP system designed for restaurants and fast-food businesses.

The system allows business owners to manage one or multiple branches from a unified platform, including employees, permissions, POS operations, orders, cash operations, inventory, recipes, menu, pricing, payments, payroll, reports, notifications, audit history, and business operations.

The primary product requirement is that the system may contain many advanced capabilities while keeping daily workflows simple, fast, practical, and suitable for ordinary POS and office hardware.

The system is designed around the following core principles:

* operational simplicity;
* strong auditability;
* offline continuity;
* security without unnecessary user friction;
* historical integrity;
* modularity;
* scalability;
* documentation-first development.

## 2. Product Scope

FastFood ERP covers the following major business areas:

1. Business/Tenant Management
2. Branch Management
3. Employees and Roles
4. Permissions and Access Control
5. Authentication and Trusted Devices
6. Offline Operation and Synchronization
7. POS and Order Management
8. Cash Register and Cash Sessions
9. Shift Handover
10. Inventory and Warehouse Management
11. Products and Recipes
12. Menu and Pricing
13. Payments, Discounts, and Refunds
14. Attendance and Payroll
15. Reports and Dashboards
16. Notifications and Alerts
17. Audit and Change History
18. Subscription and Tariff Management
19. Data Lifecycle and Deletion

The system is intended to provide a unified operational platform while keeping business domains logically separated.

## 3. Target Users

The main user categories are described below.

### 3.1. Super Admin

Super Admin is the highest-level platform administrator.

Primary responsibilities include:

* creating restaurant/business networks;
* creating and managing subscription tariffs;
* defining business, branch, owner, employee, and feature limits;
* configuring which functions are available under each tariff;
* managing platform-level configuration.

Super Admin is not intended to perform ordinary day-to-day restaurant operations.

### 3.2. Owner

Owner is a business-level administrator.

Depending on permissions, an Owner can manage:

* branches;
* employees;
* roles;
* permissions;
* menu;
* recipes;
* prices;
* inventory;
* expenses;
* reports;
* payroll;
* dashboards;
* business-level settings;
* discounts;
* Sets;
* recipe approvals;
* relevant corrections and operational controls.

A business may have multiple Owners.

The maximum number of Owners is controlled by the applicable subscription tariff.

### 3.3. Manager

Manager performs management operations within the permissions assigned by the business.

A Manager may:

* be assigned to one or multiple branches;
* receive branch-specific permissions;
* perform selected operations on behalf of the business;
* perform employee management when the required permission is assigned;
* perform cancellation, refund, correction, or other operational actions when explicitly permitted.

A Manager cannot grant permissions that they do not personally possess.

### 3.4. Cashier

Cashier is a primary POS user.

Depending on assigned permissions, a Cashier can:

* create orders;
* modify orders;
* process payments;
* work with cash sessions;
* close a cash session;
* participate in shift handover;
* work with debt records;
* perform permitted order cancellation actions;
* participate in correction workflows;
* handle table/order operational actions assigned to the cashier workflow.

Cashier actions must be associated with the employee identity, business, branch, cash register, cash session, and trusted device.

Cashiers use their own employee accounts rather than shared user identities.

### 3.5. Waiter

Waiter capabilities are determined by the assigned role and permissions.

Possible responsibilities include:

* working with halls and tables;
* creating orders;
* viewing orders;
* monitoring order status;
* serving Ready items;
* temporarily helping another Waiter when the Help permission is available;
* performing temporary table assignment actions when authorized.

The exact capabilities are controlled by the permission system rather than being hard-coded exclusively to the employee type.

### 3.6. Cook and Other Employees

Cook and other employee categories use the same general permission architecture.

Their effective access is determined through:

**Role Permission + Employee Permission Override + Branch Scope**

This allows the same role to have different permissions for different branches or individual employees.

## 4. Multi-Branch Model

A business may operate multiple branches.

Each branch has its own operational context, including:

* branch-specific employees and permission scopes;
* inventory and warehouse data;
* cash sessions;
* operational transactions;
* POS operations;
* offline operation capability.

An employee may work in multiple branches.

The same employee may have different permissions in different branches.

Branch-specific permissions are therefore part of the core business model rather than an optional extension.

Each branch belongs to exactly one business.

Business-level configuration may include:

* subscription and tariff;
* global menu;
* approved recipes;
* Sets;
* role definitions;
* business settings;
* pricing rules.

Branch-level operational data remains associated with the relevant branch.

## 5. POS and Order Model

POS is one of the primary operational components of the system.

### 5.1. Current Order Types

The current core order types are:

* Hall / Dine-in
* Takeaway

Phone delivery, online ordering, and advanced delivery management are not part of the current core operational scope.

They may be introduced later as separate business requirements.

### 5.2. Customer Information

The current system does not maintain a full permanent customer CRM.

For normal:

* Dine-in orders;
* Takeaway orders;

customer information is not required.

Customer information may be stored when required by a debt transaction.

For debt customers:

* name is required;
* phone number is required;
* address is optional;
* comment is optional.

The debt ledger may contain multiple debt orders for the same customer.

### 5.3. Order Number and Identity

Each order has a persistent database UUID.

The customer-facing order number is a short operational number that resets when the cash session is opened/closed according to the defined business process.

The customer-facing number must not be used as the primary database identity.

UUID-based transaction identity is required for idempotency, synchronization, audit, and historical integrity.

### 5.4. Order Lifecycle

The core operational order lifecycle is:

**Draft → Accepted → Preparing → Ready → Served**

There is no separate `Completed` state.

`Served` represents that all currently existing items of the order have been delivered.

A Served order is not intended to receive additional products.

If the customer requests additional products after the order has reached Served, a new order is created and linked to the same table where applicable.

Intermediate statuses may be disabled by the Owner according to business configuration.

For example, a business may use:

**Accepted → Served**

while the order is still sent to the kitchen and processed through the operational workflow.

### 5.5. Draft Orders

Draft orders are temporary working records.

A Draft:

* may be automatically saved;
* may remain open for an extended period;
* may be freely edited;
* does not deduct inventory;
* does not notify the kitchen;
* does not make a table occupied.

When the user saves/submits the order:

1. inventory availability is checked;
2. required inventory is deducted atomically;
3. the order becomes Accepted;
4. the kitchen is notified;
5. the table becomes Occupied when applicable.

If required inventory is insufficient, the save operation is rejected and the Draft remains unchanged.

### 5.6. Table and Order Relationship

A table may have multiple separate open orders.

Each order has its own:

* lifecycle;
* payment state;
* inventory transactions;
* audit history.

Orders are linked to the table but remain independent transactional records.

A table becomes Occupied only when the first actual order is successfully saved.

A table becomes Free only when all relevant open orders/accounts are resolved according to the business rules.

Open orders cannot simply be removed from the table to make the table Free.

### 5.7. Waiter Assignment

The system supports both:

* permanent table assignment;
* operational temporary assignment.

When no permanent assignment exists, the first authorized Waiter who successfully saves the first order becomes the main Waiter for that table.

A table has one main Waiter.

Other Waiters may help when the Help permission is available, but helping does not transfer main Waiter ownership.

A temporary assignment may allow another Waiter to operate the table for a limited period.

Temporary assignment ends when the table becomes Free.

Permanent assignment remains unchanged.

All assignment changes are auditable.

### 5.8. Help Workflow

A Waiter with Help permission may assist another Waiter.

Help is intentionally limited.

A helper may:

* select the relevant table/order/item;
* deliver a Ready item;
* mark the item Served.

A helper may not:

* create a new order;
* change permanent table assignment;
* free the table;
* manage payment unless separately permitted.

Help actions are recorded in history.

### 5.9. Walkout

Walkout is a dedicated operational action for a customer leaving without completing the normal order/payment flow.

Walkout is performed by the Cashier or another explicitly authorized employee.

Only items that were actually Served by the main Waiter are included in the walkout amount.

Items that remain:

* Draft;
* Preparing;
* Ready;
* or otherwise not Served

are not included as served sales in the walkout calculation.

The walkout action records relevant operational and audit information, including:

* branch;
* table;
* related orders;
* cash session;
* cashier;
* main Waiter;
* order timestamps;
* item statuses;
* served items;
* walkout amount;
* reason/comment;
* table release time.

After the walkout workflow is completed, the table may become Free if no other open order remains.

## 6. Order Modification and Customization

Accepted orders may be modified before Served.

Modifications must preserve historical integrity and must not silently overwrite the fact that a change occurred.

### 6.1. Inventory Reconciliation

When an Accepted order is modified, inventory is reconciled by delta.

Examples:

* `30g → 0g` returns 30g to inventory;
* `30g → 50g` deducts an additional 20g;
* `30g → 20g` returns 10g.

If additional required inventory is unavailable, the entire modification is rejected.

The original order state remains unchanged.

No partial inventory modification is allowed.

### 6.2. Unit-Level Customization

When multiple units of the same product exist in one order, each unit may have different customization.

For example:

* one Lavash without sauce;
* one normal Lavash.

For quantity three, each individual unit may have its own customization.

The system therefore supports customization at unit level when required.

An unnecessary global `Apply to all` workflow is not required.

### 6.3. Customization Types

Customization may include:

* removing an ingredient;
* reducing an ingredient;
* increasing an ingredient;
* adding an allowed extra ingredient.

For example:

* `Sauce −30g`;
* `Cheese +20g`;
* `Meat +50g`.

The base recipe is never changed by a one-time customer customization.

### 6.4. Kitchen and Receipt Output

When an order customization is changed after kitchen output has already been sent:

1. the previous kitchen ticket is marked as cancelled/updated;
2. a new kitchen ticket is created;
3. the order number remains unchanged;
4. inventory is reconciled according to the new state.

The new kitchen ticket represents the current required state.

The complete change history remains available through audit/history mechanisms.

Cashier-facing receipt information must also reflect the current customization.

## 7. Kitchen Printing and External Printer Operations

Kitchen printing is an external operational process and must remain separate from the core business transaction.

The ERP transaction must not be rolled back merely because a printer fails.

A printer failure results in a printer job state such as:

* Pending;
* Failed;
* Retrying;
* Printed.

The system must support:

* print job identity;
* printer identity;
* attempt history;
* retry behavior;
* duplicate protection;
* failure notification;
* escalation when failure persists.

Duplicate printing must be prevented using transaction/job identities and print attempt tracking.

If a printer is temporarily unavailable, the order remains valid and the print job is retried after recovery.

Persistent printer failures are escalated to the appropriate Manager and, where required, Owner.

## 8. Cash Register and Cash Session Model

Each branch normally operates with one cash register.

The architecture should not prevent future support for multiple registers, but the current business process is designed around one register per branch.

The primary relationship is:

**Branch → Cash Register → Cash Sessions**

The current branch model also assumes one primary POS/Cashier computer.

A cash session:

* is opened manually;
* belongs to one cashier shift;
* is closed manually;
* may remain open overnight;
* calculates expected values;
* receives the cashier's actual cash amount;
* records the resulting difference.

A cash session does not automatically close because a calendar day has changed.

Cashier changes are handled by closing the previous cashier's session and opening a new session for the next cashier.

A closed cash session is never directly reopened.

Required corrections use the dedicated correction workflow.

## 9. Payment and Debt Model

The system supports the following payment methods:

* Cash;
* Card;
* Debt;
* Mixed.

Mixed payment may combine:

* Cash;
* Card;
* Debt.

The system validates that the total allocated payment amount matches the final order amount.

Card payment is currently recorded manually.

The architecture must allow future integration with external payment providers without requiring a redesign of the core payment domain.

### 9.1. Debt

Debt is a supported payment state and is managed through a debt ledger.

A debt customer record requires:

* name;
* phone number.

Address and comment are optional.

The same customer may have multiple debt orders.

Partial repayment is supported.

The cashier may select an existing debtor or create a new debt customer.

Duplicate phone numbers are allowed.

Customer information may be edited by the Cashier or another authorized employee.

A customer may only be deleted after all associated debts are fully settled, while historical order records retain the required historical customer information.

## 10. Cancellation and Refund

Cancellation and refund are separate business operations.

### 10.1. Cancellation

Cancellation requires appropriate permission.

An authorized employee may cancel an order or relevant items before the order is fully served.

A cancellation requires a reason/comment where defined by the business rule.

For each item, the authorized employee determines whether inventory should be returned.

By default, non-Served items are eligible for inventory return.

A Served item can never be returned to inventory.

This reflects the physical reality that a served product may already have been consumed or cannot reliably be separated back into its original ingredients.

Cancellation may therefore contain a mixture of:

* returned inventory items;
* non-returned items.

The selected inventory-return decisions are recorded in audit history.

The kitchen is notified of the cancellation/update.

The original transaction remains historically preserved, while cancellation is recorded as a separate event.

### 10.2. Refund

Refund is separate from cancellation.

If an already-paid order is cancelled, the refund workflow is handled separately.

Refund permissions are restricted to authorized roles such as Manager, Owner, or another role with explicit refund permission.

Refund supports:

* full order refund;
* selected product refund;
* selected quantity refund.

Refund reason/comment is mandatory.

Current refund methods are:

* Cash;
* Card.

The current implementation records the refund in the ERP; physical money return is handled operationally.

Future payment-provider integration may automate provider-side refunds.

A refund does not return inventory.

## 11. Inventory and Recipe Model

The inventory system supports:

* Raw Material;
* Semi-Finished Product;
* Finished Product.

Recipe dependencies can represent relationships such as:

**Raw Material → Semi-Finished Product → Finished Product**

A product that has a recipe cannot be permanently deleted.

Instead, it is archived.

Recipes are versioned.

Historical recipe versions remain available for review and audit.

### 11.1. Inventory Deduction

Inventory is deducted when an order is Accepted/saved, not while it remains Draft.

Normal order processing does not allow negative stock.

Inventory availability is checked atomically before deduction.

If multiple transactions compete for the same stock, the successful transaction consumes the available stock and later transactions must re-check availability before deduction.

### 11.2. Cost Model

The inventory model supports:

* Last Purchase Cost;
* Average Cost;
* FIFO actual consumption.

A product may retain relevant cached/derived values such as:

* Current Quantity;
* Average Cost;
* Last Purchase Cost;
* Last Purchase Date.

Inventory batches remain available for historical tracking and FIFO consumption.

### 11.3. Semi-Finished Production

Semi-finished products are produced through approved recipes.

A production transaction:

1. consumes the required ingredients;
2. uses the approved recipe;
3. records the actual prepared output;
4. adds the actual output quantity to inventory;
5. records the production event in history.

Recipe quantities scale proportionally according to actual output where applicable.

Low stock for semi-finished products is a warning condition and does not itself block production.

### 11.4. Stock Thresholds

Each relevant product may have its own low-stock threshold.

Low stock generates a warning.

A threshold of zero represents an out-of-stock condition.

Low-stock warnings do not automatically block sales when sufficient actual stock exists.

Actual ingredient shortage blocks an order when required inventory cannot be provided.

### 11.5. Inventory Adjustments

Manual inventory exit is restricted by the appropriate Inventory Adjustment permission.

A manual adjustment requires a reason/comment and is audited.

Branch-to-branch stock transfer is not part of the current core scope.

Permissioned inventory adjustment may remove stock when required by the business process, but it must not silently behave as a branch transfer.

## 12. Products and Recipes

Recipes define the ingredients, quantities, expected output/yield, unit information, and relevant loss/shrink rules.

Recipe changes create new versions.

Historical executed transactions are not recalculated when a recipe changes.

A newly approved recipe version becomes effective from the next cash session.

Only the Owner approves recipes.

Employees may create or edit recipes when the relevant permissions are granted, but approval remains an Owner responsibility.

An ingredient/product used by active recipes cannot simply be archived until the active recipe dependencies have been replaced through the appropriate new recipe versions.

### 12.1. One-Time Customer Customization

One-time customer customization does not modify the base recipe.

A customized order item may:

* remove an ingredient;
* reduce an ingredient;
* increase an ingredient;
* add an allowed extra ingredient.

Customization applies only to the relevant order item/unit.

### 12.2. Custom Order Items

A custom order item may use an available ingredient selection when the business workflow permits it.

The quantity of the selected ingredient is mandatory.

The system calculates the custom item's cost using the relevant Last Purchase Cost.

An authorized employee may specify a markup percentage.

The markup must be between 0% and 100%.

The final custom-item selling price is calculated from cost and markup.

Invalid negative markup or markup above 100% is rejected.

## 13. Menu and Pricing

The system maintains a global menu and recipe structure for the business.

Approved recipes may become part of the global menu and may then be enabled for permitted branches.

The same approved recipe structure is intended to remain consistent across branches.

A branch may override a global product selling price for its own operation if the responsible user has the required permission.

Each product belongs to exactly one menu category.

An inactive product is not shown or sold through the active menu/POS flow.

Historical inventory, recipe, order, and audit records remain preserved.

### 13.1. Product Pricing

Standard menu product prices cannot be manually changed by ordinary Cashiers or employees.

Discounts are separate from the standard product price.

The business may define rules for how permitted ingredient customizations affect price.

Supported business configurations may include:

1. customization does not change price;
2. customization changes price by the ingredient cost;
3. customization changes price by the ingredient selling value.

Ingredient selling value is based on cost plus the configured markup.

Business-level markup may have product/ingredient-specific overrides.

### 13.2. Extras and Ingredient Changes

When an extra ingredient is added:

* the additional quantity is deducted from inventory;
* its cost is calculated;
* its selling value is calculated according to the configured markup.

When an ingredient is removed or reduced for a specific order item:

* the base recipe remains unchanged;
* inventory is reconciled by delta;
* price impact follows the configured business rule.

### 13.3. Sets

The system supports Sets as predefined product structures.

A Set contains configured component products.

Components cannot be freely swapped for other products during normal sale.

Set composition is intentionally stable.

Changes to the underlying component product recipe do not automatically change the Set composition.

A Set configuration changes only when the Set itself is edited through the appropriate configuration workflow.

A Set has:

* its own selling price;
* component-based cost;
* component inventory requirements.

The Set selling price is independently configured by the Owner and does not automatically change when component product prices change.

The Set cost may change as the underlying component costs change.

If any mandatory Set component is unavailable because of insufficient stock or an Equipment Broken state, the Set becomes unavailable for sale.

A Set configuration change becomes effective from the next cash session.

The previous Set configuration remains available for historical reference.

Historical orders are never recalculated because of a later Set configuration change.

## 14. Reports and Dashboards

The system provides operational and management reports covering major business activities.

Important reporting areas include:

* cash sessions;
* cashiers;
* orders;
* payments;
* debt;
* refunds;
* cancellations;
* discrepancies;
* corrections;
* correction requests;
* inventory;
* production;
* employees;
* payroll;
* branch performance;
* audit logs;
* change history;
* printer failures and relevant operational failures.

Report access is controlled by permissions and branch scope.

The supported user-facing export format is Excel (`.xlsx`).

Report data must preserve historical integrity and must reflect the relevant business rules and correction history.

## 15. Report Versioning

Reports use a versioned model.

Each report version is immutable and records information such as:

* reporting period;
* creation time;
* creator or system source;
* creation reason;
* relevant data state.

If relevant data changes after a report has been created, a new version is created for the affected report.

Previous versions remain unchanged and available for historical review.

If a report is requested again for the same period and the underlying relevant data has not changed, a new version is not created.

Open cash sessions are excluded from finalized report calculations where the relevant report requires closed-session data.

## 16. Notifications and Alerts

The system provides operational alerts for important business conditions.

Examples include:

* low stock;
* out of stock;
* subscription expiration;
* salary due;
* large refund;
* large inventory variance;
* branch loss;
* cash discrepancy;
* shift handover events;
* correction requests;
* report generation failure;
* report updates;
* persistent printer failure.

Notification visibility is controlled by role, permission, branch scope, and business rules.

Important operational failures should be visible without unnecessarily interrupting normal POS operation.

## 17. Audit and Historical Integrity

Important business operations must be traceable.

Audit history must preserve relevant information such as:

* actor;
* business;
* branch;
* device;
* timestamp;
* affected entity;
* action;
* previous state where applicable;
* resulting state;
* reason/comment where required.

The system must preserve historical records for:

* orders;
* order modifications;
* customization;
* cancellations;
* refunds;
* payments;
* inventory adjustments;
* recipe versions;
* Set configurations;
* permission changes;
* cash corrections;
* printer attempts where operationally relevant.

Original records must not be silently overwritten.

Corrections and changes are represented through dedicated history or correction mechanisms.

## 18. Subscription Lifecycle

FastFood ERP operates as a subscription-based SaaS product.

Subscription and permission are separate controls.

An operation is allowed only when both:

1. the user has the required permission; and
2. the business subscription grants access to the relevant capability.

When a subscription expires:

* modifying functions are blocked;
* existing data remains viewable;
* historical records remain accessible;
* relevant lists and reports can be exported to Excel;
* destructive data changes are not permitted.

If the subscription is not reactivated within 60 days, the business data is permanently deleted according to the data lifecycle rules.

Users receive advance notifications about the upcoming deletion deadline.

Downgrading a subscription must not silently or destructively delete existing data.

## 19. Offline-First Operation

A branch must be able to continue core operations when the internet connection is temporarily unavailable.

Offline operation is supported through:

* previously trusted devices;
* time-limited offline authorization;
* encrypted local storage;
* locally generated UUIDs;
* queued local transactions;
* synchronization when connectivity returns;
* server-side validation after synchronization.

A completely new device cannot start operating offline.

The device must first connect to the server while online, complete registration/verification, and become a trusted device.

Offline operation must not bypass:

* permissions;
* branch scope;
* subscription rules;
* business rules;
* transaction validation;
* audit requirements.

## 20. Security Model

The system must provide strong protection without noticeably slowing down normal POS operations.

Core security mechanisms include:

* employee authentication;
* role permissions;
* employee permission overrides;
* branch-level access scope;
* trusted devices;
* encrypted local storage;
* cryptographically signed offline authorization;
* UUID-based idempotency;
* audit logging;
* server-side validation;
* synchronization validation;
* clock rollback/tampering detection.

Every important order and transaction must be traceable to the relevant:

* Order UUID;
* Employee UUID;
* Business UUID;
* Branch UUID;
* Cash Register UUID;
* Cash Session UUID;
* Device UUID;
* timestamp.

Trusted devices provide device trust only.

A trusted device does not independently grant business permissions.

## 21. Performance Principle

The system follows the principle:

> A feature-rich ERP must not become a complicated or slow POS.

Daily operational workflows should remain fast and simple, especially:

* POS;
* order creation;
* payment;
* cash operations;
* shift handover;
* inventory operations;
* kitchen workflow.

The system must operate on ordinary POS and office hardware without requiring unnecessarily powerful hardware.

Security, audit, synchronization, inventory validation, and other infrastructure mechanisms must be designed to minimize impact on normal transactional performance.

## 22. Product Design Principles

### 22.1. Simplicity

Complex internal architecture must not unnecessarily increase the complexity of the user interface.

### 22.2. Auditability

Important business changes must not occur without traceable history.

The system must preserve who performed an action, what changed, when it changed, and why when a reason is required.

### 22.3. Offline Continuity

Temporary internet failure must not unnecessarily stop core branch operations.

### 22.4. Security Without Excessive Friction

Security controls should protect the system without requiring unnecessary verification for every normal operation.

### 22.5. Scalability

The initial subscription model supports up to 10 branches, while the architecture must not prevent future expansion.

### 22.6. Historical Integrity

Original business records must not be silently overwritten.

Corrections and changes must preserve the original value and maintain the relevant change history.

Historical transactions must not be recalculated because of later recipe, Set, pricing, or configuration changes.

### 22.7. Modular Architecture

Business capabilities should remain logically separated so that the system can evolve without tightly coupling unrelated domains.

### 22.8. Documentation-First Development

Business rules and major architectural decisions must be documented before implementation.

Major changes must be recorded through the project's ADR process.

## 23. Current Out of Scope

The following capabilities are not part of the current core scope:

* online ordering;
* phone delivery;
* Telegram bot;
* customer mobile application;
* full customer CRM;
* contracts;
* advanced delivery management;
* branch-to-branch inventory transfer;
* external payment-provider automation;
* automatic physical refund processing.

These capabilities may be considered later as separate business requirements.

The architecture should remain extensible where appropriate without prematurely implementing these capabilities.

## 24. Core Product Flow

At a high level, the product operates through the following structure:

**Business → Branch → Employees/Permissions → POS → Orders → Payments → Cash Sessions → Reports**

Inventory and recipes support the operational flow:

**Recipes → Inventory → Menu → Orders → Stock Deduction → Reports**

Production supports inventory:

**Recipes → Production → Semi-Finished/Finished Stock → Menu/POS**

The customization flow is:

**Base Recipe → Order Item Customization → Inventory Delta → Price Adjustment → Kitchen Output → Audit**

The Set flow is:

**Set Configuration → Component Products → Component Inventory → Set Sale → Set Cost → Reports**

The security and infrastructure layer supports these operations:

**Authentication → Trusted Device → Offline Authorization → Local Transaction → Synchronization → Server Validation → Audit**

This separation should remain clear as the system evolves.

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

