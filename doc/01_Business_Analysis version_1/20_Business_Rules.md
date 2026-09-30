# Business Rules

**Document ID:** FF-BA-020
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document consolidates the core business rules of the FastFood ERP system.

The purpose is to provide a single business-level reference for rules that affect multiple modules and processes.

These rules are derived from the approved business requirements defined throughout the Business Analysis documentation.

Technical implementation details are intentionally excluded.

---

## 2. Rule Categories

The business rules are grouped into:

* Business and Tenant Rules;
* Subscription Rules;
* Branch Rules;
* User and Permission Rules;
* Authentication and Device Rules;
* Offline Rules;
* Order Rules;
* Cash Register Rules;
* Handover Rules;
* Inventory Rules;
* Recipe Rules;
* Menu and Pricing Rules;
* Payment Rules;
* Refund Rules;
* Employee and Payroll Rules;
* Reporting Rules;
* Notification Rules;
* Audit Rules;
* Data Lifecycle Rules.

---

# 3. Business and Tenant Rules

### BR-BUS-001 — Business Isolation

Every business is an independent tenant.

Data belonging to one business must not be accessible to another business.

---

### BR-BUS-002 — Business Ownership

A business may have one or more Owners.

The maximum number of Owners is controlled by the subscription tariff.

---

### BR-BUS-003 — Super Admin

Super Admin is the highest platform-level role.

Super Admin may manage:

* businesses;
* subscription tariffs;
* platform-level limits;
* enabled functions.

Super Admin is not a normal restaurant operational role.

---

### BR-BUS-004 — Business Data Ownership

Business operational data belongs to the corresponding business within the platform.

Business data includes, where applicable:

* branches;
* employees;
* orders;
* inventory;
* recipes;
* cash sessions;
* payments;
* reports;
* payroll;
* audit history.

---

### BR-BUS-005 — Cross-Tenant Isolation

Business isolation must be enforced across:

* application operations;
* APIs;
* database queries;
* reports;
* exports;
* offline data;
* synchronization;
* background processes.

---

# 4. Subscription Rules

### BR-SUB-001 — Subscription Required

Normal modifying business operations require an active subscription.

---

### BR-SUB-002 — Tariff Limits

A subscription tariff may define limits for:

* branches;
* Owners;
* employees;
* enabled functions;
* other configurable resources.

---

### BR-SUB-003 — Resource Limit

When a configured tariff limit is reached, creation of additional resources must be blocked.

Existing resources must not be silently deleted.

---

### BR-SUB-004 — Permission and Subscription

A user may perform an operation only when both conditions are satisfied:

```text
Subscription Allows
+
User Has Permission
=
Operation Allowed
```

---

### BR-SUB-005 — Subscription Expiration

When the subscription expires, modifying functions are restricted.

Historical information remains available during the defined retention period.

---

### BR-SUB-006 — Expired Read-Only State

An expired business enters a read-only state.

Users may:

* log in according to applicable access rules;
* view historical information;
* export relevant information to Excel.

Normal modifying operations are blocked.

---

### BR-SUB-007 — Retention Period

The expired business receives a 60-day reactivation period.

---

### BR-SUB-008 — Reactivation

If the business reactivates within the 60-day period, existing business data remains available and normal operation may resume according to the new subscription.

---

### BR-SUB-009 — Permanent Deletion

If the business does not reactivate within the 60-day period, its business data becomes eligible for permanent deletion.

---

### BR-SUB-010 — Tariff Downgrade

A tariff downgrade must not automatically delete existing data.

If existing resources exceed the new limits, creation of additional resources may be blocked.

---

### BR-SUB-011 — Trusted Device Restriction

A trusted device must not bypass subscription restrictions.

---

# 5. Branch Rules

### BR-BRN-001 — Branch Ownership

Every branch belongs to exactly one business.

---

### BR-BRN-002 — Branch Isolation

Branch-specific operational data must remain isolated between branches.

---

### BR-BRN-003 — Branch Data

Branch-specific data may include:

* employees;
* permissions;
* inventory;
* warehouse;
* cash register;
* cash sessions;
* orders;
* expenses;
* reports;
* branch-specific prices.

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

### BR-BRN-007 — Branch Switching

Changing the selected branch changes the operational context but does not change the user's permissions.

---

### BR-BRN-008 — New Branch Permission Initialization

Existing role configuration may be used as the initial permission configuration when a new branch is created.

The configuration may then be edited according to the user's permissions.

---

### BR-BRN-009 — Branch Deactivation

A branch with historical data should be deactivated or archived rather than permanently deleted.

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

The effective permission of an employee is determined by:

* employee identity;
* role;
* permission configuration;
* branch scope;
* applicable overrides;
* subscription entitlement.

---

### BR-USR-005 — Permission Scope

Permissions may be:

* single-branch;
* multi-branch;
* business-wide.

---

### BR-USR-006 — Permission Grant Authority

An employee may grant only permissions that they themselves are authorized to grant.

---

### BR-USR-007 — Privilege Escalation Prevention

An employee must not be able to:

* grant permissions to themselves;
* grant unauthorized broader scope;
* create equivalent unrestricted privileges;
* promote themselves to Owner;
* remove protected Owner privileges.

---

### BR-USR-008 — Owner Protection

Owners are protected from unauthorized removal or privilege reduction.

---

### BR-USR-009 — Permission History

Every important permission change must be auditable.

The history must preserve:

* actor;
* target;
* permission;
* scope;
* previous state;
* new state;
* timestamp.

---

### BR-USR-010 — Latest Explicit Command

For the same permission and scope, the latest explicit authorized command determines the effective configuration.

Previous commands remain in history.

---

### BR-USR-011 — Permission Revert

Reverting a permission creates a new event.

Previous permission history remains preserved.

---

### BR-USR-012 — Recipe Permission

Recipe visibility and recipe modification are separate permissions.

Menu access does not automatically grant recipe access.

---

### BR-USR-013 — Employee Deactivation

Employees with historical activity must be deactivated rather than deleted.

Historical records remain associated with the employee.

---

# 7. Authentication and Trusted Device Rules

### BR-AUTH-001 — Employee Authentication

Employees authenticate using their individual account credentials.

---

### BR-AUTH-002 — New Device Registration

A new device must initially connect online before it can become a trusted device.

---

### BR-AUTH-003 — Trusted Device Verification

A device must be verified before receiving trusted-device offline authorization.

---

### BR-AUTH-004 — Offline Device Authorization

Only trusted and authorized devices may perform supported offline operations.

---

### BR-AUTH-005 — Device Scope

Trusted-device authorization must remain limited to the authorized:

* business;
* branch;
* employee;
* permissions;
* offline scope.

---

### BR-AUTH-006 — Device Revocation

An Owner may revoke a trusted device according to the security rules.

---

### BR-AUTH-007 — Offline Authorization Security

Offline authorization must be:

* cryptographically protected;
* time-bounded;
* protected against replay;
* protected against clock manipulation.

---

### BR-AUTH-008 — Device Does Not Equal Employee

Device identity does not replace employee identity.

The system must preserve both where relevant.

---

# 8. Offline Rules

### BR-OFF-001 — Offline-First Operation

Supported branch operations must continue during temporary internet outages when performed from authorized trusted devices.

---

### BR-OFF-002 — Initial Online Requirement

A device cannot perform its first trusted-device registration entirely offline.

---

### BR-OFF-003 — Offline Permissions

Offline operation must respect the employee's valid offline authorization and permissions.

---

### BR-OFF-004 — Offline Subscription

Offline operation must not be used to bypass subscription restrictions.

---

### BR-OFF-005 — Transaction UUID

Every transaction must have a permanent transaction UUID.

A separate Client Transaction ID is not required.

---

### BR-OFF-006 — Offline Transaction Identity

Offline transactions must preserve, where applicable:

* transaction UUID;
* business UUID;
* branch UUID;
* employee UUID;
* device UUID;
* cash register UUID;
* cash session UUID;
* timestamp;
* state.

---

### BR-OFF-007 — Idempotent Synchronization

The same transaction must not be applied multiple times during synchronization.

---

### BR-OFF-008 — Server Authority

After synchronization, the central server is authoritative for business state.

---

### BR-OFF-009 — Rejected Transactions

Rejected offline transactions must remain traceable.

They must not silently disappear.

---

### BR-OFF-010 — Offline Business Isolation

Offline data must remain isolated by business and branch.

---

# 9. Order Rules

### BR-ORD-001 — Order Intake

The current primary order-entry method is physical cashier entry.

---

### BR-ORD-002 — Order Types

Supported order types are:

* Hall/Dine-in;
* Takeaway;
* Phone Delivery.

---

### BR-ORD-003 — Customer Database

A permanent customer database is not currently required.

---

### BR-ORD-004 — Delivery Information

Phone delivery orders may store:

* phone number;
* delivery address.

This information belongs to the order.

---

### BR-ORD-005 — Order Identity

Every order has a permanent UUID.

---

### BR-ORD-006 — Customer-Facing Order Number

The customer-facing order number is three digits.

It resets to zero when a new cash session opens.

---

### BR-ORD-007 — Order Number and UUID

The three-digit order number is not the permanent database identity.

The UUID remains the permanent order identity.

---

### BR-ORD-008 — Historical Order Values

Historical orders must preserve the values applicable when the transaction occurred.

Later menu or price changes must not rewrite historical orders.

---

### BR-ORD-009 — Recipe Modification

Removing or adding permitted recipe components during order customization must update the price according to the configured business rule.

---

### BR-ORD-010 — Extras

Additional extras/add-ons are supported.

---

### BR-ORD-011 — Component Swapping

Component swapping is not supported.

---

### BR-ORD-012 — Non-Recipe Modification

Non-recipe modifications may be recorded using order comments.

---

### BR-ORD-013 — Inventory Validation

An order requiring unavailable inventory must be blocked unless the relevant item/component is removed or otherwise adjusted according to permitted customization rules.

---

### BR-ORD-014 — No Negative Stock

Order processing must not create negative inventory.

---

### BR-ORD-015 — Kitchen Routing

Accepted orders must be routed to the appropriate kitchen printer according to configured routing rules.

---

# 10. Cash Register Rules

### BR-CASH-001 — Register per Branch

The current model uses one cash register per branch.

The architecture must not prevent future expansion to multiple registers.

---

### BR-CASH-002 — Manual Opening

Cash sessions are opened manually.

---

### BR-CASH-003 — Manual Closing

Cash sessions are closed manually.

---

### BR-CASH-004 — No Automatic Closing

A cash session may remain open overnight.

The system must not automatically close it solely because the calendar day changed.

---

### BR-CASH-005 — One Active Session

Only one active cash session is allowed for the current branch/register under the current business model.

---

### BR-CASH-006 — Session Period

A cash session's reporting period is:

```text
Opening
→
Closing
```

It is not automatically equal to a calendar day.

---

### BR-CASH-007 — Payment Types

Cash and card payments are currently supported.

---

### BR-CASH-008 — Physical Cash Entry

The cashier manually enters only the physical cash counted.

Card totals are derived from recorded transactions.

---

### BR-CASH-009 — Expected Cash Visibility

Expected cash remains hidden until the cashier enters the actual physical cash amount.

---

### BR-CASH-010 — Difference

After actual cash is entered, the system calculates:

* no difference;
* shortage;
* overage.

---

### BR-CASH-011 — Recount

When a discrepancy exists, the system should allow a recount.

---

### BR-CASH-012 — Discrepancy Explanation

If the discrepancy remains, the responsible cashier must provide the required explanation.

---

### BR-CASH-013 — Owner Notification

The Owner is notified about relevant cash discrepancies.

---

### BR-CASH-014 — Closed Session

A closed cash session remains closed.

---

### BR-CASH-015 — Correction

Corrections do not reopen the cash session.

---

### BR-CASH-016 — Correction Limit

A closed cash session initially allows a maximum of three corrections under the defined correction workflow.

---

### BR-CASH-017 — Additional Correction

After the initial correction limit is reached, an authorized Owner or Manager may grant exactly one additional correction.

---

### BR-CASH-018 — Correction Authorization

Every additional correction authorization requires:

* authorized actor;
* requesting cashier;
* reason;
* timestamp;
* audit history.

---

### BR-CASH-019 — Correction Rejection

A correction request rejection requires an explanation.

The requester cannot automatically submit another request for the same case.

---

### BR-CASH-020 — Correction History

Every correction preserves the original and corrected values.

---

# 11. Shift Handover Rules

### BR-HAND-001 — Handover Is Not a New Session

Cash handover transfers responsibility within the same cash session.

---

### BR-HAND-002 — New Cashier Authentication

The new cashier must authenticate using their own account.

---

### BR-HAND-003 — Cash Acceptance

The new cashier must explicitly accept responsibility for the cash register.

---

### BR-HAND-004 — Open Orders

Open orders remain in the same cash session and transfer to the new cashier.

---

### BR-HAND-005 — Order History

Previous cashier actions remain associated with the previous cashier.

New actions are associated with the new cashier.

---

### BR-HAND-006 — Cash Count

The new cashier counts the physical cash.

Expected cash remains hidden until the actual amount is entered.

---

### BR-HAND-007 — Handover Actions

The previous cashier has exactly two required actions:

* Confirm;
* Recalculate.

---

### BR-HAND-008 — No Reject Action

There is no separate Reject action in the handover workflow.

---

### BR-HAND-009 — Handover Completion

Responsibility transfers only after the handover workflow is successfully completed.

---

### BR-HAND-010 — Same Session Identity

The Cash Session UUID remains unchanged during handover.

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

* Prepared in Branch;
* Bought Ready.

---

### BR-INV-005 — FIFO

Inventory consumption follows FIFO where applicable.

---

### BR-INV-006 — No Negative Inventory

Inventory cannot become negative.

---

### BR-INV-007 — Order Deduction

Orders deduct required inventory according to the applicable recipe and inventory rules.

---

### BR-INV-008 — Insufficient Inventory

An operation requiring unavailable stock must be blocked.

---

### BR-INV-009 — Stock Count

A stock count records:

* expected quantity;
* counted quantity;
* variance;
* resulting stock adjustment.

---

### BR-INV-010 — Inventory History

Inventory adjustments and variances remain historically traceable.

---

### BR-INV-011 — Low Stock

Low-stock thresholds may generate alerts and shopping-list entries.

---

### BR-INV-012 — Shopping List

The shopping list is advisory.

A purchase does not require the item to be marked as completed in the shopping list first.

---

### BR-INV-013 — Purchase Record

A purchase record may contain:

* quantity;
* price;
* source;
* date.

---

### BR-INV-014 — Equipment Broken

A product may temporarily be marked unavailable because equipment is broken.

---

# 13. Recipe Rules

### BR-REC-001 — Recipe Components

Recipes may contain raw materials and semi-finished products.

---

### BR-REC-002 — Nested Dependencies

Semi-finished products may themselves have recipes.

The system must support dependency tracing:

```text
Raw Material
    ↓
Semi-Finished Product
    ↓
Finished Product
```

---

### BR-REC-003 — Recipe Approval

A new or modified recipe requires approval before active use.

---

### BR-REC-004 — Recipe Modification Permission

Recipe modification requires a dedicated permission.

---

### BR-REC-005 — Global Recipe

Approved recipes are business-level and apply consistently across branches under the current business model.

---

### BR-REC-006 — Recipe History

Old recipes are archived and remain historically traceable.

---

### BR-REC-007 — Product With Recipe

A product with a recipe cannot be permanently deleted through normal operations.

---

### BR-REC-008 — Recipe Visibility

Recipe visibility is controlled separately from normal menu visibility.

---

### BR-REC-009 — Shrinkage

Prepared items may include configured shrinkage/loss percentages.

---

# 14. Menu and Pricing Rules

### BR-MENU-001 — Global Menu

The business has a central/global menu.

---

### BR-MENU-002 — Branch Menu

Branches use permitted products from the global menu.

---

### BR-MENU-003 — Product Activation

A product may be active or inactive in a branch menu.

---

### BR-MENU-004 — Product Availability

Menu activation and physical product availability are separate concepts.

---

### BR-MENU-005 — Branch Price Override

A branch may have a different product price from the global price when the user has the required permission.

---

### BR-MENU-006 — Historical Prices

Historical transactions retain the price applicable at transaction time.

---

### BR-MENU-007 — Open Order Price

Open orders must not be silently rewritten because the current product price changes.

---

### BR-MENU-008 — Product Images

Product images are optional.

---

### BR-MENU-009 — Taxes

Taxes are currently included in product prices.

A separate tax-detail engine is not currently required.

---

# 15. Payment and Refund Rules

### BR-PAY-001 — Supported Payments

Current payment types are:

* cash;
* card.

---

### BR-PAY-002 — Cash Relationship

Cash payments affect the physical cash session.

---

### BR-PAY-003 — Card Relationship

Card payments are recorded separately from physical cash.

---

### BR-PAY-004 — Successful Payment

An order is closed after successful payment according to the order lifecycle.

---

### BR-PAY-005 — Duplicate Payment Protection

The system must prevent duplicate payment application to the same order.

---

### BR-PAY-006 — Offline Payment

Supported payment operations may continue offline when the device is authorized.

---

### BR-PAY-007 — Refund Permission

Refunds require the appropriate permission.

---

### BR-PAY-008 — Refund Reason

A refund requires a mandatory reason.

---

### BR-PAY-009 — Refund Approval

Where approval is required by the configured business rule, the refund must not be finalized without the required approval.

---

### BR-PAY-010 — Refund History

Refunds remain linked to the original payment/order history.

---

### BR-PAY-011 — Large Refund

Significant refunds generate the applicable alert.

---

# 16. Employee and Payroll Rules

### BR-EMP-001 — Employee Identity

Every employee has an individual identity.

---

### BR-EMP-002 — Employee Creation

Employee creation is permission-controlled.

---

### BR-EMP-003 — Manager Employee Creation

A Manager may create employees only if the Owner has granted the required permission.

---

### BR-EMP-004 — Attendance

Attendance rules may differ according to employee role.

---

### BR-EMP-005 — Salary Models

The system supports:

* Fixed;
* Percentage;
* Shift;
* Hybrid;
* Daily Pay;
* Bonuses.

---

### BR-EMP-006 — Payroll History

Historical payroll calculations remain traceable.

---

### BR-EMP-007 — Salary Changes

Salary configuration changes must preserve historical information.

---

### BR-EMP-008 — Salary Due Notification

Relevant authorized users may receive salary-due notifications.

---

# 17. Reporting Rules

### BR-REP-001 — Report Permissions

Report access is permission-controlled.

---

### BR-REP-002 — Excel Export

Excel is the supported report export format.

PDF and CSV are not currently required.

---

### BR-REP-003 — Manual Report Period

A manually generated report may cover a maximum of one month.

---

### BR-REP-004 — Invalid Date Range

A report request where the start date is after the end date must be rejected.

---

### BR-REP-005 — Open Cash Sessions

Open cash sessions are excluded from applicable reports.

---

### BR-REP-006 — Empty Reports

Reports are generated even when no relevant data exists.

Values with no data are displayed as `0`.

---

### BR-REP-007 — Automatic Monthly Report

The monthly report is automatically generated on the last calendar day after applicable cash sessions are closed.

---

### BR-REP-008 — Automatic Retry

Failed automatic report generation must be retried.

Persistent failure must be logged and reported to authorized users.

---

### BR-REP-009 — Report Versions

Each generated report is treated as a version.

---

### BR-REP-010 — Immutable Versions

Previous report versions cannot be silently modified.

---

### BR-REP-011 — No Unnecessary Version

If the same report period is requested and relevant data has not changed, a new version is not required.

---

### BR-REP-012 — Report Change

Only reports affected by relevant business-data changes need a new version.

---

### BR-REP-013 — Report Storage

Generated reports are retained and cannot be deleted through normal user operations.

---

# 18. Notification Rules

### BR-NOT-001 — Permission Scope

Notifications must respect user permissions.

---

### BR-NOT-002 — Branch Scope

Branch notifications must respect branch access.

---

### BR-NOT-003 — Low Stock Alert

Low-stock conditions generate relevant alerts.

---

### BR-NOT-004 — Out-of-Stock Alert

Out-of-stock conditions generate relevant alerts.

---

### BR-NOT-005 — Large Refund Alert

Significant refunds generate relevant alerts.

---

### BR-NOT-006 — Inventory Variance Alert

Significant inventory variance generates relevant alerts.

---

### BR-NOT-007 — Branch Loss Alert

Significant current-day branch loss generates the applicable alert.

---

### BR-NOT-008 — Cash Discrepancy

Relevant cash shortages/overages generate notifications.

---

### BR-NOT-009 — Report Ready

Authorized users may receive report-ready notifications.

---

### BR-NOT-010 — Report Change

Authorized users may receive notifications when a report is re-versioned because relevant data changed.

---

### BR-NOT-011 — No-Change Notification

A correction that produces no actual report-affecting change must not generate a report-change notification.

---

### BR-NOT-012 — Notification Does Not Grant Permission

A notification cannot grant the recipient permission to perform the related action.

---

# 19. Audit Rules

### BR-AUD-001 — Important Actions

Important business and administrative actions must be auditable.

---

### BR-AUD-002 — Actor

The responsible employee or system process must be identifiable.

---

### BR-AUD-003 — Old and New Values

Important changes preserve old and new values where applicable.

---

### BR-AUD-004 — Reason

Required reasons/comments remain part of the historical record.

---

### BR-AUD-005 — Immutable Audit

Audit records cannot be silently edited or deleted through normal business operations.

---

### BR-AUD-006 — Correction History

Corrections create new historical events rather than erasing previous events.

---

### BR-AUD-007 — Permission History

Permission changes remain historically traceable.

---

### BR-AUD-008 — Employee History

Employee deactivation does not remove historical actions.

---

### BR-AUD-009 — Offline History

Offline transactions remain traceable after synchronization.

---

### BR-AUD-010 — Audit Scope

Audit history follows business and branch authorization.

---

# 20. Data Lifecycle Rules

### BR-LIFE-001 — Deactivation

Deactivation preserves historical data.

---

### BR-LIFE-002 — Historical Records

Important historical records must not be silently deleted.

---

### BR-LIFE-003 — Subscription Expiration

Subscription expiration starts the defined read-only lifecycle.

---

### BR-LIFE-004 — Retention Period

The expired business receives 60 days for reactivation.

---

### BR-LIFE-005 — Permanent Deletion

After the 60-day period without reactivation, business data becomes eligible for permanent deletion.

---

### BR-LIFE-006 — Deletion Warning

Authorized users must receive appropriate warnings before permanent deletion.

---

### BR-LIFE-007 — No Additional Archive

There is no additional user-accessible archive period after the 60-day retention period.

---

### BR-LIFE-008 — Tenant-Safe Deletion

Permanent deletion must affect only the target business.

---

### BR-LIFE-009 — Deletion Audit

The platform must retain sufficient information to demonstrate that the deletion process occurred.

---

# 21. Cross-Module Rules

### BR-CROSS-001 — Subscription + Permission

Neither subscription entitlement nor employee permission alone is sufficient.

Both must permit the operation.

---

### BR-CROSS-002 — Historical Data

Current configuration changes must not rewrite historical transactions.

This applies to:

* products;
* prices;
* recipes;
* employees;
* permissions;
* payroll.

---

### BR-CROSS-003 — Correction Instead of Overwrite

When an important completed record needs correction, the correction process must preserve the original state.

---

### BR-CROSS-004 — Auditability

Important cross-module operations must preserve their relationship to the relevant business entity and transaction.

---

### BR-CROSS-005 — Branch Isolation

Cross-module data access must preserve branch authorization.

---

### BR-CROSS-006 — Offline Consistency

Offline operations must follow the same core business rules as online operations whenever the operation is supported offline.

---

### BR-CROSS-007 — Server Authority

After synchronization, the central server is authoritative for final business state.

---

# 22. Business Rule Priority

When multiple business rules apply to the same operation, the following control layers must be considered:

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
Permission
        ↓
Business Operation
        ↓
Audit / History
```

A lower-level permission cannot override a higher-level restriction.

For example, an employee with permission to edit an order cannot edit orders when the subscription state blocks modifying operations.

---

# 23. Business Rule Enforcement

Business rules must be enforced consistently across all relevant interfaces.

A rule must not be bypassable simply by using:

* another UI screen;
* another API endpoint;
* offline mode;
* synchronization;
* report export;
* background processing;
* another branch context.

---

# 24. Business Rule Changes

Changes to these business rules must be documented before implementation.

A significant business rule change should identify:

* affected rule;
* previous behavior;
* new behavior;
* reason;
* affected modules;
* related documentation.

Architectural or technical decisions resulting from business-rule changes should be documented separately in the ADR system where appropriate.

---

# 25. Business Rule Summary

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

The system must preserve this relationship throughout the business lifecycle.

---

# 26. Business Boundaries

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
* UI implementation details;
* database indexes;
* queue technology;
* caching technology;
* cloud provider;
* server topology.

These concerns belong to later documentation sections.

---

# 27. Related Documents

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

