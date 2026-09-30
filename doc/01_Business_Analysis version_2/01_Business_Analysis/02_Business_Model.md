# Business Model

**Document ID:** BA-02
**Status:** Accepted
**Version:** 2.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

FastFood ERP is a multi-tenant SaaS ERP platform for restaurant and fast-food businesses.

The business model is based on a clear separation between:

* the FastFood ERP platform;
* businesses/tenants;
* branches;
* employees;
* business-level configuration;
* branch-level operations;
* subscriptions and tariff entitlements.

The platform provides a common ERP foundation while ensuring that each business operates within its own isolated business environment.

The model must support multiple branches, multiple Owners, branch-specific employees and permissions, subscription-based feature access, offline branch operations, and future platform expansion.

---

## 2. Platform-Level Business Structure

FastFood ERP operates as a SaaS platform.

The high-level structure is:

```text
FastFood ERP Platform
│
├── Super Admin
│
└── Businesses / Tenants
    │
    ├── Business A
    │   ├── Branch 1
    │   ├── Branch 2
    │   └── Branch N
    │
    ├── Business B
    │   ├── Branch 1
    │   └── Branch N
    │
    └── Business N
```

The platform itself is responsible for platform-level administration.

Each Business/Tenant is an independent operational customer environment.

---

## 3. Business / Tenant

A Business is the primary commercial and operational customer entity.

A Business owns and controls its:

* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* Sets;
* pricing configuration;
* inventory;
* warehouses;
* cash operations;
* orders;
* payments;
* debt records;
* expenses;
* attendance;
* payroll;
* reports;
* notifications;
* audit history;
* business-level settings.

All business-owned operational data belongs to exactly one Business.

Business data must be isolated from other Businesses.

---

## 4. Business Ownership

A Business may have multiple Owners.

Owners are business-level administrators and may manage business configuration and operations according to their permissions and the active subscription.

Owner responsibilities may include:

* managing branches;
* managing employees;
* configuring roles and permissions;
* managing menu and products;
* creating and approving recipes;
* managing Sets;
* configuring prices;
* configuring discounts;
* configuring service-fee rules;
* configuring customization pricing rules;
* managing inventory;
* managing expenses;
* managing payroll;
* reviewing reports;
* managing business dashboards;
* performing authorized corrections and operational controls.

The maximum number of Owners is controlled by the active subscription tariff.

Being an Owner of one Business does not automatically grant access to another Business.

---

## 5. Super Admin and Business Ownership

Super Admin operates at the platform level.

Super Admin may:

* create Businesses;
* configure subscription tariffs;
* define platform-level limits;
* configure enabled modules/features by tariff;
* manage platform-level settings.

Super Admin is not automatically a Business Owner.

Platform-level administration and Business operational ownership are separate concepts:

```text
Platform Administration
        ≠
Business Operational Ownership
```

A Super Admin does not automatically become part of a Business's normal employee or Owner permission model.

---

## 6. Business Lifecycle

A Business follows a subscription-driven lifecycle.

The general lifecycle is:

```text
Business Creation
        ↓
Tariff Configuration
        ↓
Subscription Activation
        ↓
Branch Configuration
        ↓
Owner Configuration
        ↓
Employee and Permission Setup
        ↓
Menu / Product / Recipe / Set Setup
        ↓
Pricing and Business Rule Setup
        ↓
Inventory Setup
        ↓
Daily Operations
        ↓
Reports and Monitoring
        ↓
Subscription Renewal or Expiry
```

The exact implementation of subscription lifecycle is defined in:

`docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`

---

## 7. Business Configuration vs Branch Operations

The system separates Business-level configuration from Branch-level operations.

### 7.1. Business-Level Configuration

Business-level configuration may include:

* subscription and tariff;
* global menu;
* products;
* approved recipes;
* recipe versions;
* Sets;
* Set configurations;
* role definitions;
* permission definitions;
* business-wide pricing rules;
* discount rules;
* service-fee rules;
* customization pricing rules;
* markup configuration;
* business settings.

### 7.2. Branch-Level Operations

Branch-level operations include:

* employees assigned to the branch;
* POS operations;
* orders;
* tables;
* cash register;
* cash sessions;
* inventory;
* warehouse operations;
* production;
* purchases;
* inventory adjustments;
* branch expenses;
* attendance;
* branch-level reporting;
* offline operation.

Business-level configuration may be shared across branches, while operational transactions remain associated with the branch where they occur.

---

## 8. Multi-Branch Business Model

A Business may operate multiple branches.

The initial commercial model supports up to 10 branches under the relevant tariff, while the architecture must not prevent future expansion.

Each branch:

* belongs to exactly one Business;
* has its own operational data;
* may have its own employees;
* has branch-specific permission scope;
* has its own inventory and warehouse context;
* has its own cash operations;
* may operate offline;
* produces branch-specific operational history.

A single employee may be assigned to multiple branches.

The same employee may have different permissions in different branches.

Example:

```text
Employee A
│
├── Branch 1
│   └── Manager-level permissions
│
├── Branch 2
│   └── Cashier permissions
│
└── Branch 3
    └── View-only permissions
```

---

## 9. Business-Wide Menu and Recipe Model

The Business owns the global menu and approved recipe structure.

A product may be enabled or disabled for operational sale according to business configuration.

Each product belongs to exactly one menu category.

Approved recipes are shared as the business's standard recipe definitions and may be used by permitted branches.

Recipe versions are preserved historically.

A later recipe change does not recalculate or rewrite historical transactions.

New approved recipe versions become effective according to the defined cash-session activation rule.

Detailed recipe rules are defined in:

`docs/01_Business_Analysis/12_Products_and_Recipes.md`

---

## 10. Set Business Model

Sets are business-level configurable products composed of predefined component products.

A Set has:

* a configured component structure;
* its own selling price;
* a derived component-based cost;
* inventory requirements based on its components.

The Owner controls Set configuration.

A Set's selling price is independent from the current selling prices of its component products.

Changes to component product selling prices do not automatically change the Set selling price.

Changes to underlying component recipes do not automatically change the Set composition.

The Set itself must be edited to change its composition.

A new Set configuration becomes effective from the next cash session.

Previous configurations remain available for historical reference.

Detailed Set rules are defined in:

`docs/01_Business_Analysis/13_Menu_and_Pricing.md`

---

## 11. Pricing and Business Rules

Business-level pricing behavior may include:

* standard product prices;
* branch price overrides;
* discounts;
* service fees;
* ingredient markup;
* customization pricing;
* custom order markup;
* Set selling prices.

These rules are configurable within the permissions granted to authorized business users.

The system separates:

```text
Base Product Price
        +
Discount
        +
Service Fee
        +
Customization / Extra Adjustments
        ↓
Final Order Amount
```

The exact calculation rules are defined in the relevant pricing and payment documents.

---

## 12. Subscription-Based SaaS Model

FastFood ERP is sold as a subscription service.

Subscription tariffs may control:

* branch limits;
* Owner limits;
* employee limits;
* enabled modules;
* enabled functions;
* other business-level entitlements.

The system separates:

```text
Subscription Entitlement
        +
User Permission
        ↓
Allowed Operation
```

Having a permission does not bypass a tariff restriction.

Having a tariff feature enabled does not automatically grant a user permission.

Both conditions must be satisfied where applicable.

---

## 13. Subscription Expiry

When a Business subscription expires:

* modifying operations are blocked;
* existing data remains viewable;
* historical records remain accessible;
* permitted exports remain available;
* destructive modification is restricted.

The Business enters a read-only retention period.

If the subscription is not reactivated within the defined retention period, the Business data is permanently deleted according to the data lifecycle rules.

The current retention period is 60 days.

Users are notified before permanent deletion.

Detailed rules are defined in:

`docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`

and

`docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`.

---

## 14. Subscription Downgrade

Subscription downgrade must not silently destroy existing data.

If the new tariff has lower limits than the current state, the system must preserve existing historical data.

The Business may be restricted from creating additional entities or using restricted functions until the business state satisfies the new tariff or the subscription is upgraded.

Historical records must remain preserved.

---

## 15. Employee and Permission Model

Employees belong to the Business and may be assigned to one or multiple branches.

Effective access is determined through:

```text
Role Permission
        +
Employee Permission Override
        +
Branch Scope
        +
Subscription Entitlement
```

An employee cannot grant permissions beyond their own authorized scope.

Permission changes are recorded as immutable events.

The business model does not assume that an employee type automatically determines all access.

For example, a Manager may have different capabilities in different branches.

Detailed permission rules are defined in:

`docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`.

---

## 16. Operational Business Model

The Business operates through a collection of connected operational domains:

```text
Business
│
├── Employees / Permissions
│
├── Menu / Products / Recipes / Sets
│
├── Inventory / Warehouse / Production
│
├── POS / Orders
│
├── Payments / Debt / Refunds
│
├── Cash Register / Cash Sessions
│
├── Attendance / Payroll
│
├── Expenses
│
└── Reports / Notifications / Audit
```

These domains are logically separated but interact through defined business rules.

For example:

```text
Order Accepted
      ↓
Inventory Deduction
      ↓
Kitchen Notification
      ↓
Payment
      ↓
Cash Session
      ↓
Reports / Audit
```

The exact transaction rules are defined in the relevant domain documents.

---

## 17. Branch Operational Independence

Branches are operationally independent within the Business.

A branch may continue core operations during temporary internet failure when using a previously trusted device and valid offline authorization.

Offline operation does not create a separate Business.

Offline transactions remain associated with:

* Business;
* Branch;
* Employee;
* Device;
* relevant operational session;
* transaction UUID.

When connectivity returns, transactions are synchronized and validated by the server.

---

## 18. Business Data Isolation

Business isolation is a core requirement.

A user operating within Business A must not access Business B data unless explicitly authorized through a platform-level mechanism.

Isolation must apply to:

* API requests;
* database queries;
* reports;
* exports;
* background jobs;
* notifications;
* offline synchronization;
* local operational data;
* audit history.

Branch scope must also be enforced within a Business.

A user authorized for Branch A must not automatically access Branch B operational data.

---

## 19. Historical Data Ownership

Business data remains owned by the Business throughout its active lifecycle.

Important historical records include:

* orders;
* payments;
* refunds;
* cancellations;
* cash sessions;
* cash corrections;
* inventory transactions;
* production transactions;
* purchases;
* recipe versions;
* Set configurations;
* employee history;
* permission history;
* audit history;
* report versions.

Historical records must not be silently rewritten because of later configuration changes.

For example:

```text
Old Recipe
    ↓
Historical Order
    ↓
New Recipe
```

The historical order continues to represent the transaction executed under the old recipe.

The same principle applies to Set configurations, pricing configuration, permissions, and other versioned business rules.

---

## 20. Business Corrections

The Business Model distinguishes between:

* normal operational transactions;
* corrections;
* cancellations;
* refunds;
* configuration changes.

A correction does not erase the original event.

Instead, the system records the correction and preserves the original state.

This principle applies to areas such as:

* cash discrepancies;
* inventory adjustments;
* order modifications;
* cancellations;
* refunds;
* permission changes.

The exact correction limits and authorization rules are defined by the relevant business documents.

---

## 21. Business Reporting Model

The Business receives reports based on its operational data.

Reports may be generated at:

* business level;
* branch level;
* operational domain level.

Report visibility depends on:

* employee permissions;
* branch scope;
* subscription entitlement.

Important business reporting areas include:

* sales;
* orders;
* payments;
* debt;
* cash sessions;
* cash discrepancies;
* refunds;
* cancellations;
* inventory;
* production;
* purchases;
* employee activity;
* payroll;
* branch performance;
* audit history.

Reports use versioning where required.

Previous report versions remain immutable.

---

## 22. Business Notifications

Notifications are generated from important business events.

Examples include:

* low stock;
* out of stock;
* cash discrepancy;
* shift handover;
* large refund;
* large inventory variance;
* branch loss;
* salary due;
* subscription expiration;
* correction requests;
* report failures;
* persistent printer failures.

Notifications are targeted according to:

* business;
* branch;
* role;
* permission;
* event severity.

Notifications do not replace audit history.

---

## 23. Expenses

Expenses are part of the Business financial operation model.

Business-level expense configuration is controlled by authorized business users.

Branch expenses may be created by authorized users and require an appropriate comment/reason where defined.

Expenses remain associated with the relevant Business and, when applicable, Branch.

Expenses are included in relevant reports.

---

## 24. Payroll and Attendance

Employee attendance and payroll belong to the Business.

Payroll may support different payment models, including:

* fixed salary;
* percentage-based pay;
* shift-based pay;
* daily pay;
* hybrid models;
* bonuses.

Attendance and payroll access are controlled by permissions and branch scope.

Payroll records remain historically preserved and are included in relevant reports.

---

## 25. Business-Level Configuration Lifecycle

Business configuration changes must not unnecessarily alter historical transactions.

Configuration changes that affect future operations may use effective dates or operational activation boundaries.

For the current model, some configuration changes become effective when a new cash session starts.

Examples include:

* recipe versions;
* Set configurations.

The current session continues using the configuration active for that session.

Historical orders continue to use the configuration under which they were executed.

---

## 26. Business Model Principles

The FastFood ERP business model follows these principles:

### 26.1. Business Isolation

Each Business is an independent tenant with isolated operational data.

### 26.2. Branch Separation

Branches operate independently while remaining part of one Business.

### 26.3. Central Business Configuration

Global menu, approved recipes, Sets, roles, and business rules are managed at Business level.

### 26.4. Branch Operational Independence

Orders, inventory, cash sessions, employees, and other operational transactions remain branch-specific.

### 26.5. Permission-Based Operations

Employee access is determined by explicit permissions and scope.

### 26.6. Subscription-Based Entitlement

Tariffs determine which capabilities a Business may use.

### 26.7. Historical Integrity

Past transactions remain historically correct even after later configuration changes.

### 26.8. Offline Continuity

Temporary connectivity loss must not unnecessarily stop core branch operations.

### 26.9. Correction Instead of Silent Overwrite

Business corrections preserve the original event and record the correction separately.

### 26.10. Extensibility

The model should allow future integrations and features without forcing premature implementation of out-of-scope capabilities.

---

## 27. Current Business Scope

The current business model includes:

* multi-tenant SaaS operation;
* multi-branch businesses;
* multiple Owners;
* employee and permission management;
* POS;
* Dine-in/Hall orders;
* Takeaway orders;
* tables and Waiters;
* Sets;
* recipes;
* inventory;
* warehouse operations;
* semi-finished production;
* cash registers;
* cash sessions;
* shift handover;
* payments;
* debt;
* refunds;
* discounts;
* service fees;
* attendance;
* payroll;
* reports;
* notifications;
* audit history;
* offline operation;
* subscription lifecycle.

The following remain outside the current core business model:

* online ordering;
* phone delivery;
* customer mobile application;
* full CRM;
* Telegram bot;
* contracts;
* advanced delivery management;
* branch-to-branch inventory transfer;
* automated external payment-provider processing;
* automated physical refund processing.

These capabilities may be added later as separate business requirements.

---

## 28. Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
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

