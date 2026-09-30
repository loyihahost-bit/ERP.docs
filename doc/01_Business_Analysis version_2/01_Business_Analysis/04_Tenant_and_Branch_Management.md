# Tenant and Branch Management

**Document ID:** BA-04
**Status:** Accepted
**Version:** 2.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for Business/Tenant and Branch management in FastFood ERP.

It describes:

* how Businesses/Tenants are represented;
* how branches belong to a Business;
* how business-level and branch-level responsibilities are separated;
* how employees can work across multiple branches;
* how branch-specific permissions are applied;
* how branch scope affects operational access;
* how branch configuration is managed;
* how branch lifecycle and historical data are preserved;
* how tenant and branch isolation applies to reports, exports, offline operation, and synchronization.

The document defines business behavior. Technical database, API, security, synchronization, and infrastructure implementation is defined in later documents.

---

## 2. Business/Tenant Definition

A Business/Tenant is the primary organizational entity using FastFood ERP.

A Business represents one restaurant or fast-food organization and owns its operational data.

A Business may contain:

* branches;
* Owners;
* employees;
* roles;
* permissions;
* products;
* global menu;
* recipes;
* Sets;
* pricing configuration;
* warehouses;
* inventory;
* cash registers;
* orders;
* payments;
* debt records;
* expenses;
* attendance;
* payroll records;
* reports;
* notifications;
* audit history;
* business-level settings.

All operational data must belong to exactly one Business.

A Business must not share operational ownership of the same record with another Business.

---

## 3. Platform and Business Separation

The platform contains multiple independent Businesses/Tenants.

The high-level structure is:

**FastFood ERP Platform → Business/Tenant → Branches**

The platform is managed by Super Admin.

The Business is operated by its authorized Owners, Managers, and Employees.

Super Admin is a platform-level role and is not automatically a Business Owner.

Business operational ownership and platform administration are separate concepts.

---

## 4. Business Creation

Business creation is performed by the **Super Admin**.

When creating a Business, the platform establishes a new tenant boundary.

The Business then receives:

* an applicable subscription/tariff;
* one or more authorized Owners;
* required initial configuration.

The initial setup may include:

* Business information;
* subscription configuration;
* Owner configuration;
* initial branch;
* employee setup;
* role and permission configuration;
* menu/product configuration;
* recipe configuration;
* other required business settings.

Normal business operations must not be enabled until required initial configuration has been completed.

Business creation must be auditable.

---

## 5. Business Ownership

A Business may have multiple Owners.

The number of active Owners is controlled by the selected subscription tariff.

Owners operate at Business level unless their access is explicitly restricted by the applicable permission and scope model.

Owner responsibilities may include:

* branch management;
* employee management;
* roles;
* permissions;
* menu;
* products;
* recipes;
* Sets;
* pricing;
* inventory;
* expenses;
* reports;
* payroll;
* business configuration;
* operational corrections;
* other Owner-authorized management functions.

Owner access does not remove the requirement for business rules, subscription entitlement, or auditability.

---

## 6. Tenant Isolation

Business data must be logically and operationally isolated.

A user belonging to one Business must not access another Business's operational data.

Tenant isolation applies to:

* Business data;
* branch data;
* employee data;
* products;
* recipes;
* Sets;
* menu;
* orders;
* payments;
* debt;
* inventory;
* warehouses;
* cash sessions;
* expenses;
* payroll;
* reports;
* exports;
* notifications;
* audit records;
* offline data;
* synchronization operations;
* background jobs.

Tenant isolation must not depend only on user-interface restrictions.

It must be preserved throughout the application and data lifecycle.

---

## 7. Branch Definition

A Branch represents a physical or operational location belonging to a Business.

Every Branch belongs to exactly one Business.

A Branch operates within the Business's global configuration but maintains its own operational state.

A Branch may have:

* employees;
* branch-specific permissions;
* warehouse;
* inventory;
* cash register;
* cash sessions;
* orders;
* expenses;
* attendance;
* production activity;
* purchases;
* operational reports;
* branch-specific pricing overrides;
* branch-specific operational settings.

---

## 8. Branch Ownership

Every Branch belongs to exactly one Business.

A Branch cannot simultaneously belong to multiple Businesses.

A Branch must not be transferred between Businesses through a normal reassignment operation.

This prevents historical data from becoming ambiguous.

If a future Business-transfer capability is required, it must be defined as a separate controlled business process.

---

## 9. Branch Limit

The maximum number of active branches is controlled by the Business subscription tariff.

The initial product model supports up to **10 branches**, depending on the selected tariff.

If the active branch limit is reached:

* a new branch cannot be created;
* existing branches remain preserved;
* existing branches continue operating;
* the authorized user is informed that the subscription limit has been reached.

Increasing the subscription limit allows additional branches to be created.

A subscription downgrade must not silently delete branches that exceed the new limit.

---

## 10. Branch Creation

A Branch may be created only when:

* the responsible user has branch-management permission;
* the subscription permits another active branch;
* required Business information is available;
* required branch information is provided.

Branch creation must establish the Branch as a new operational identity.

A newly created Branch must not inherit historical transactions from another Branch.

Branch creation must be auditable.

The system should record:

* Business;
* Branch identity;
* creator;
* creation time;
* initial configuration;
* applicable subscription state;
* relevant permissions or scope.

---

## 11. Branch Activation

A Branch has an operational status.

At minimum, the Business model distinguishes:

* **Active**
* **Inactive/Archived**

An Active Branch may perform normal permitted operations.

An Inactive/Archived Branch must not receive new normal operational transactions unless explicitly reactivated.

Historical information belonging to an inactive Branch remains part of the Business's historical records.

---

## 12. Branch Deactivation

A Business may deactivate a Branch when the location is no longer operating.

Deactivation must not silently delete:

* orders;
* payments;
* cash sessions;
* inventory history;
* purchases;
* production history;
* reports;
* employee history;
* payroll history;
* audit records;
* other historical Business data.

The Branch identity remains preserved.

Historical records continue to reference the original Branch.

---

## 13. Branch Reuse

An inactive Branch must not be reused by replacing its identity or historical records.

If a Business opens a new physical location, a new Branch should normally be created.

This preserves the distinction between:

* different locations;
* different operational periods;
* different employees;
* different cash sessions;
* different inventory;
* different reports.

Historical data must not be reassigned to a new Branch merely for convenience.

---

## 14. Branch Deletion

Normal Branch deletion is not permitted when historical Business data exists.

The preferred operation is:

**Deactivate / Archive**

rather than destructive deletion.

Permanent deletion of Branch data, where applicable, follows the broader Business data lifecycle and deletion process.

Branch deactivation and Business deletion are separate concepts.

---

## 15. Business-Level vs Branch-Level Data

The Business model distinguishes between global Business data and branch-specific operational data.

### 15.1. Business-Level Data

Examples include:

* Business identity;
* subscription;
* tariff;
* global menu;
* products;
* approved recipes;
* recipe versions;
* Sets;
* Set configurations;
* role definitions;
* permission definitions;
* pricing rules;
* discount rules;
* service-fee configuration;
* business-wide settings.

### 15.2. Branch-Level Data

Examples include:

* branch employees;
* branch assignments;
* branch permissions;
* warehouses;
* inventory;
* purchases;
* production;
* cash register;
* cash sessions;
* orders;
* payments;
* debt activity;
* branch expenses;
* attendance;
* branch reports;
* branch-specific price overrides;
* branch-specific operational settings.

The technical data model must preserve this distinction.

---

## 16. Global Products and Menu

Products and the global menu are Business-level concepts.

An approved product may be made available to applicable Branches according to Business configuration and permissions.

Each product belongs to exactly one menu category.

An inactive product:

* is not displayed as an available product for normal sale;
* cannot be sold through normal POS operations;
* remains preserved for historical records.

Historical orders must continue to reference the product even if the product later becomes inactive.

---

## 17. Global Recipes

Recipes are Business-level definitions.

Approved recipes may be used by applicable Branches.

A shared product recipe is not independently redefined for each Branch.

Recipe changes are versioned and historically preserved.

A recipe change does not silently recalculate historical orders.

Recipe changes become effective according to the configured effective-session rule.

Current business rules require approved recipe changes to become effective from the next cash session.

---

## 18. Sets

Sets are Business-level product configurations.

A Set contains predefined component products.

A Set:

* has its own selling price;
* has component-based inventory consumption;
* has component-based cost;
* does not allow arbitrary component swapping during normal sale;
* retains its configured composition.

If a mandatory component is unavailable because of insufficient stock or Equipment Broken status, the Set is unavailable for sale.

Changing a component product's selling price does not automatically change the Set selling price.

Changing the underlying recipe of a component does not automatically change the Set composition.

Set configuration changes are effective from the next cash session and retain configuration history.

---

## 19. Branch Menu Availability

The Business may determine which global products are available in a Branch.

A Branch may therefore use a subset of the Business's global menu.

Branch availability does not create a separate product identity.

The same Business product may be available in one Branch and inactive or unavailable in another according to Business configuration.

Branch-specific availability must not alter historical orders.

---

## 20. Branch Pricing

A Business may define global product prices.

A Branch may have a branch-specific price override where permitted.

Changing a Branch price override:

* affects future applicable sales;
* does not rewrite historical orders;
* must require the appropriate permission;
* must be auditable.

Cashiers and ordinary employees must not manually change the standard menu price unless a specific authorized business rule permits it.

Discounts are handled separately from normal product pricing.

---

## 21. Employee Identity

Employees are Business-level identities.

An employee does not need a separate account for every Branch.

One employee may be assigned to:

* one Branch;
* multiple Branches;
* Business-wide scope where explicitly authorized.

Employee identity remains the same across Branch assignments.

The employee's effective access depends on:

**Employee Identity + Role + Permission + Branch Scope + Subscription Entitlement**

---

## 22. Employee Branch Assignment

Branch assignment determines where an employee may operate.

However, Branch assignment alone does not grant unrestricted access.

An employee may belong to a Branch while lacking permission to:

* view certain information;
* modify certain records;
* perform financial operations;
* manage employees;
* manage inventory;
* manage recipes;
* perform corrections;
* perform other restricted actions.

Therefore:

**Branch Membership ≠ Permission**

---

## 23. Multiple Branch Assignment

An employee may work in multiple Branches.

The same employee may have different permissions in different Branches.

For example:

* Employee A may have Cashier permissions in Branch 1;
* Employee A may have Manager permissions in Branch 2;
* Employee A may have no operational access to Branch 3.

Separate employee accounts are not required for these assignments.

Each Branch assignment must be evaluated according to the effective permission model.

---

## 24. Branch-Specific Permissions

The same employee may receive different permissions for different Branches.

Branch-specific permission configuration must support:

* selected Branch;
* selected employee or employees;
* selected permissions;
* applicable role;
* employee overrides;
* effective scope.

An employee must not gain permissions in one Branch merely because the employee has stronger permissions in another Branch.

---

## 25. Role Scope

A role or permission assignment may have:

* single-Branch scope;
* multi-Branch scope;
* Business-wide scope.

The scope must be explicitly defined.

Business-wide access must not be assumed simply because the employee is a Manager.

The Owner or other authorized administrator configures applicable scope according to the permission model.

---

## 26. Manager Scope

Managers operate within permissions granted by the Business.

A Manager may receive access to one or multiple Branches.

A Manager cannot grant another user a permission that the Manager does not possess within the relevant scope.

Therefore:

**Permission Granting Authority ≤ Grantor's Own Authority**

Branch scope must also be respected when permissions are granted.

---

## 27. Permission Inheritance for New Branches

When a new Branch is created, existing role configuration may be used as the initial permission configuration.

This configuration is a starting point rather than an immutable rule.

The Owner may customize permissions for the new Branch.

The resulting Branch configuration may therefore differ from other Branches.

A new Branch must not automatically receive permissions that the responsible user is not authorized to configure.

---

## 28. Branch Selection

When an employee has access to multiple Branches, the application must clearly identify the currently selected Branch.

The selected Branch must be visually distinguishable.

Branch-specific screens must clearly operate within the selected Branch context.

The interface should minimize the risk of accidentally performing an operation in the wrong Branch.

---

## 29. Branch Context

The selected Branch context must be consistently applied to branch-scoped operations.

Examples include:

* order creation;
* order modification;
* payment;
* debt operations;
* cash session operations;
* inventory changes;
* warehouse operations;
* production;
* purchases;
* branch expenses;
* attendance;
* payroll where branch-scoped;
* branch reports;
* employee branch permissions.

A user must not unintentionally perform an operation against another Branch simply because both Branches are accessible.

---

## 30. Branch Switching

Users with access to multiple Branches may switch their active Branch context.

Switching Branch context must not:

* modify historical data;
* change the user's identity;
* create new permissions;
* grant additional access;
* bypass subscription limits;
* bypass business rules.

The system must recalculate effective access for the selected Branch.

---

## 31. Branch and Cash Register

Each Branch normally has one cash register.

The current business model is:

**Business → Branch → Cash Register → Cash Sessions**

The current operational workflow uses one register per Branch.

The architecture should not unnecessarily prevent future support for multiple registers.

Cash register operations remain Branch-specific.

Cash sessions must always remain associated with the correct:

* Business;
* Branch;
* Cash Register;
* Cashier;
* Device where applicable.

---

## 32. Branch and POS

POS operations occur within a Branch context.

Orders created in a Branch belong to that Branch.

The order must remain associated with:

* Business;
* Branch;
* employee;
* applicable cash session;
* device;
* order identity.

A Branch must not access another Branch's operational orders unless the user has appropriate cross-Branch reporting or management access.

Cross-Branch access must not cause operational transactions to be created in the wrong Branch.

---

## 33. Branch and Tables

Tables and halls are Branch-specific operational resources.

A Branch may configure:

* halls;
* tables;
* table availability;
* table operational state.

Table state belongs to the Branch.

One Branch must not share table state with another Branch.

Multiple independent orders may exist for one table.

The table remains occupied while an applicable open order exists.

The table may return to free state only when all relevant open orders are resolved according to the POS business rules.

---

## 34. Branch and Inventory

Inventory is managed within Branch and warehouse scope.

A Branch may have one or more warehouse structures as supported by the product model.

Stock quantities must remain traceable to:

* Business;
* Branch;
* Warehouse;
* product;
* applicable batch/history.

Inventory changes in one Branch must not silently modify another Branch's stock.

The current business scope does not include normal branch-to-branch inventory transfers.

Any future transfer mechanism must be defined as a separate business operation.

---

## 35. Branch and Production

Semi-finished product production occurs within the relevant Branch.

Production:

* consumes required ingredients;
* records actual output;
* updates Branch inventory;
* retains production history.

Production records must remain associated with the Branch where production occurred.

Production in one Branch must not silently affect another Branch's inventory.

---

## 36. Branch and Purchases

Purchases are associated with the Branch and warehouse receiving the stock.

Purchase records may include:

* supplier/source;
* quantity;
* unit price;
* total amount;
* purchase date;
* batch;
* comment.

Purchased stock is added to the relevant Branch inventory after the purchase/receipt operation is confirmed.

Historical purchase records remain associated with their original Branch.

---

## 37. Branch and Expenses

Expenses may be recorded at Branch level.

Branch expenses must remain associated with the Branch where they occurred.

Owner-defined expense categories or manually added expense types may be used according to the expense configuration.

Expense modification and creation remain permission-controlled.

Historical expense records are preserved.

---

## 38. Branch and Employees

A Branch may have:

* Cashiers;
* Waiters;
* Cooks;
* Managers;
* other employees.

Employee access is determined by the effective permission model.

Branch membership alone does not grant access to all Branch operations.

Employee actions must remain traceable to the correct Business and Branch.

---

## 39. Branch and Attendance

Attendance records may be associated with the relevant Branch.

An employee working in multiple Branches must have attendance records associated with the Branch where the relevant work occurred, according to the attendance model.

Historical attendance records must not be silently reassigned when an employee's Branch assignment changes.

---

## 40. Branch and Payroll

Payroll may be calculated at Business or Branch scope depending on the configured employee and payroll model.

Where payroll is Branch-specific, the relevant Branch must remain identifiable.

Changing an employee's Branch assignment must not rewrite historical payroll records.

Payroll access remains permission-controlled.

---

## 41. Branch and Reports

Reports may be generated for:

* one Branch;
* multiple selected Branches;
* the entire Business.

Available scope depends on:

* employee permissions;
* Branch scope;
* report permissions;
* Business configuration;
* subscription entitlement.

A user without access to a Branch must not receive that Branch's data through:

* reports;
* dashboards;
* Excel exports;
* background-generated report files;
* notifications containing restricted data.

Report and export scope must follow the same Branch access rules as normal application operations.

---

## 42. Branch and Notifications

Branch-specific notifications must contain only information the recipient is authorized to receive.

Examples include:

* cash discrepancy;
* inventory variance;
* branch loss;
* salary due;
* persistent printer failure;
* correction request;
* handover notification.

A Manager assigned to Branch 1 must not receive restricted Branch 2 operational information merely because both Branches belong to the same Business.

Business-wide Owners may receive Business-level notifications according to their permissions.

---

## 43. Branch and Offline Operation

Each Branch may continue supported operations offline through trusted devices.

Offline transactions must remain associated with:

* Business;
* Branch;
* employee;
* device;
* relevant cash session;
* relevant operational context.

A trusted device for one Branch must not automatically become trusted for another Branch.

Offline authorization does not bypass Branch scope.

When synchronization occurs, the server must validate:

* Business ownership;
* Branch ownership;
* employee identity;
* permission;
* subscription state;
* transaction identity;
* applicable business rules.

---

## 44. Branch and Trusted Devices

Trusted devices are associated with the authorized Business/Branch operating context.

A trusted device does not grant:

* Business-wide permissions;
* Branch-wide permissions;
* employee permissions;
* subscription entitlement.

If an employee changes Branch assignment or loses access to a Branch, the device must not be used to bypass the updated authorization state.

---

## 45. Branch and Audit History

Important Branch operations must be auditable.

Examples include:

* Branch creation;
* Branch configuration;
* Branch activation;
* Branch deactivation;
* employee assignment;
* permission changes;
* pricing changes;
* inventory changes;
* cash operations;
* order operations;
* corrections;
* branch-specific configuration changes.

Audit records must identify the relevant:

* Business;
* Branch;
* actor;
* action;
* entity;
* timestamp;
* previous state where applicable;
* new state where applicable;
* reason where applicable;
* device where applicable.

---

## 46. Branch Configuration

Branch configuration may include:

* Branch identity;
* operational status;
* employees;
* employee assignments;
* permissions;
* warehouse;
* inventory configuration;
* menu availability;
* pricing overrides;
* cash register;
* halls;
* tables;
* operational settings;
* branch-specific notifications;
* other supported branch configuration.

Configuration changes must respect:

* user permissions;
* subscription limits;
* Business rules;
* Branch scope;
* audit requirements.

---

## 47. Branch Management Permissions

Branch management is permission-controlled.

Authorized users may receive permissions for operations such as:

* create Branch;
* edit Branch;
* deactivate Branch;
* configure Branch;
* manage Branch employees;
* assign employees;
* manage Branch permissions;
* configure Branch menu availability;
* manage Branch pricing overrides;
* view Branch reports.

Access to one Branch does not automatically grant management access to all Branches.

---

## 48. Cross-Branch Access

An Owner or authorized employee may receive cross-Branch access.

Cross-Branch access must be explicitly granted.

The user must still operate within the permissions assigned to each Branch.

Cross-Branch access is not automatically equivalent to unrestricted Business-wide access.

For example, a Manager may be able to view reports for several Branches while still being unable to modify inventory or employee permissions in those Branches.

---

## 49. Business-Wide Access

Business-wide access may be granted to authorized users where the permission model supports it.

Business-wide access allows applicable operations across the Business, but does not automatically bypass:

* subscription limits;
* restricted functions;
* action-specific permissions;
* audit requirements;
* business rules.

Business-wide scope is therefore an authorization scope, not an unrestricted administrative bypass.

---

## 50. Branch-Level Security

Branch scope must be enforced across all relevant layers.

This includes:

* user interface;
* API authorization;
* business logic;
* database access;
* reports;
* dashboards;
* Excel export;
* background processing;
* notifications;
* offline synchronization;
* audit access.

Branch restrictions must not be implemented only as UI filters.

---

## 51. Branch and Subscription

Branch creation and active Branch capacity are controlled by the Business subscription.

Subscription entitlement determines whether another Branch may exist.

Employee permissions determine whether a particular user may create or manage a Branch.

Therefore:

**Subscription Entitlement + Permission + Business Scope**

must all be satisfied where applicable.

A subscription downgrade must not silently delete Branches that exceed the new limit.

Instead, existing Branches remain preserved while creation of additional Branches is restricted until the Business resolves the limit conflict.

---

## 52. Branch Lifecycle

The general Branch lifecycle is:

**Created → Configured → Active → Inactive/Archived**

A Branch may later be reactivated if the Business chooses to resume operations and the applicable rules permit reactivation.

Deactivation does not erase historical records.

A new physical location should normally receive a new Branch identity rather than reusing an old Branch.

---

## 53. Business Lifecycle

The broader Business lifecycle is:

**Business Creation**
→ **Subscription Assignment**
→ **Owner Configuration**
→ **Branch Creation**
→ **Branch Configuration**
→ **Employee Assignment**
→ **Menu/Product/Recipe Configuration**
→ **Inventory Setup**
→ **Operational Activity**
→ **Branch Deactivation if Required**
→ **Business Expiry/Retention/Deletion if Applicable**

Business-level deletion and Branch-level deactivation are separate processes.

---

## 54. Historical Integrity

Changes to Business or Branch configuration must not silently rewrite historical operational records.

For example:

* changing a Branch name must not change the historical meaning of old transactions;
* changing an employee's Branch assignment must not move historical orders;
* changing a Branch price override must not recalculate old orders;
* changing a recipe must not recalculate historical inventory consumption;
* deactivating a product must not remove it from old orders;
* deactivating a Branch must not delete its reports;
* changing subscription limits must not delete existing Branch history.

Historical records retain their original Business and Branch context.

---

## 55. Business Isolation During Data Export

Excel exports must respect Business and Branch scope.

A user must not be able to obtain another Business's data through:

* filters;
* export parameters;
* report IDs;
* direct API requests;
* background export jobs;
* offline data.

A cross-Branch export is permitted only when the user has the required scope.

---

## 56. Business Isolation During Background Processing

Background jobs must preserve Business and Branch context.

Examples include:

* report generation;
* notifications;
* inventory alerts;
* payroll processing;
* subscription notifications;
* printer failure processing;
* synchronization.

A background job must not process records from another Business merely because the record identifiers are accessible.

---

## 57. Branch Configuration Changes

Branch configuration changes must follow the effective configuration rules.

Changes that affect operational behavior may be subject to an effective-session rule where defined by the relevant domain document.

For example:

* recipe changes;
* Set configuration changes;
* certain operational configuration changes.

When an effective-session rule applies, the existing active cash session continues using the current configuration and the new configuration becomes effective at the defined boundary.

Historical orders are not recalculated.

---

## 58. Business and Branch Data Lifecycle

Business and Branch data follow the broader data lifecycle rules.

Branch deactivation does not immediately delete Branch data.

Business subscription expiration places the Business into the defined read-only retention state.

Permanent deletion of the Business after the retention period may also remove its Branch data according to the Data Lifecycle and Deletion document.

Branch-level deactivation and Business-level permanent deletion must remain distinguishable.

---

## 59. Business Rules Summary

| Rule                         | Requirement                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| Business ownership           | One Business owns its operational data                                              |
| Tenant isolation             | Required                                                                            |
| Business creation            | Super Admin                                                                         |
| Business Owners              | Multiple allowed, tariff-limited                                                    |
| Initial branch capacity      | Up to 10 depending on tariff                                                        |
| Branch ownership             | One Business per Branch                                                             |
| Branch status                | Active / Inactive or Archived                                                       |
| Historical Branch data       | Preserved                                                                           |
| Normal Branch deletion       | Not allowed where historical data exists                                            |
| New physical location        | Normally creates a new Branch                                                       |
| Employee multi-Branch access | Supported                                                                           |
| Branch-specific permissions  | Supported                                                                           |
| Business-wide scope          | Supported where authorized                                                          |
| Branch membership            | Does not automatically grant permissions                                            |
| Manager authority            | Cannot grant permissions beyond own authority                                       |
| Global products              | Business-level                                                                      |
| Global recipes               | Business-level                                                                      |
| Recipe versioning            | Required                                                                            |
| Sets                         | Business-level with Branch operational use                                          |
| Branch price override        | Supported with permission                                                           |
| Cash register                | Normally one per Branch                                                             |
| Inventory                    | Branch/Warehouse scoped                                                             |
| Production                   | Branch scoped                                                                       |
| Purchases                    | Branch scoped                                                                       |
| Expenses                     | Branch scoped                                                                       |
| POS                          | Branch scoped                                                                       |
| Tables/Halls                 | Branch scoped                                                                       |
| Reports                      | Branch/multi-Branch/Business scope according to permission                          |
| Excel exports                | Must respect Business and Branch scope                                              |
| Offline operation            | Branch-aware and server-validated                                                   |
| Trusted device               | Does not grant permissions                                                          |
| Audit                        | Required for important Branch changes                                               |
| Subscription                 | Controls Branch capacity                                                            |
| Downgrade                    | Must not destructively delete existing Branches                                     |
| Historical integrity         | Required                                                                            |
| Tenant isolation             | Applies across UI, API, DB, reports, exports, jobs, notifications, offline and sync |

---

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

