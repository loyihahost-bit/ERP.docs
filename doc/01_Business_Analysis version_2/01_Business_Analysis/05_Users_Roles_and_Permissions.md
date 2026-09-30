# Users, Roles and Permissions

**Document ID:** BA-05
**Status:** Accepted
**Version:** 2.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for users, employees, roles, permissions, permission overrides, authorization scope, and employee access in FastFood ERP.

The permission model must provide strong access control while remaining understandable and practical for daily business operations.

The system must support:

* reusable roles;
* role permissions;
* employee-specific permission overrides;
* branch-specific access;
* multi-branch employees;
* Business-wide scope where authorized;
* action-level permissions;
* protected Owner privileges;
* permission delegation restrictions;
* subscription entitlement checks;
* trusted-device separation;
* offline authorization;
* permission history and auditability.

The permission model must not create unnecessary operational friction for POS users.

---

## 2. User and Employee Model

An employee represents a person working for a Business.

An employee has one persistent identity within the Business and may be assigned to one or more Branches.

An employee must not need separate accounts for each Branch.

Effective access is determined by:

**Employee Identity + Role + Permission + Employee Override + Branch Scope + Subscription Entitlement**

An employee's Business membership alone does not grant unrestricted access.

---

## 3. Platform and Business Roles

The system distinguishes between platform-level and Business-level roles.

### 3.1. Platform-Level Role

* Super Admin

### 3.2. Business-Level Roles

The system supports predefined and custom roles, including:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* other custom roles.

Roles are reusable permission configurations.

A role does not automatically determine every permission an employee may perform because employee overrides and Branch scope may further restrict or extend access.

---

## 4. Super Admin

Super Admin is the highest platform-level role.

Super Admin may:

* create Businesses;
* configure tariffs;
* configure subscription limits;
* manage platform-level functionality;
* perform authorized platform administration.

Super Admin is separate from the normal Business role hierarchy.

Super Admin status must not automatically grant a Business employee operational permissions.

Platform administration and Business operational authorization are separate security contexts.

---

## 5. Owner

Owner is a protected Business-level role.

A Business may have multiple Owners, subject to the active subscription limit.

Owners may manage, according to the applicable permission model:

* Branches;
* employees;
* roles;
* permissions;
* products;
* recipes;
* menu;
* Sets;
* pricing;
* inventory;
* expenses;
* reports;
* payroll;
* business settings;
* discounts;
* corrections;
* other Business functions.

Owner authority is subject to:

* subscription entitlement;
* applicable business rules;
* protected system operations;
* audit requirements.

---

## 6. Owner Protection

Owner privileges are protected.

An ordinary Business employee must not be able to:

* promote themselves to Owner;
* grant themselves Owner privileges;
* create an equivalent unrestricted permission set for themselves;
* remove another Owner's protected status through ordinary permission configuration;
* reduce protected Owner privileges without the required authorized process.

Owner protection is separate from normal employee permission customization.

If Owner removal or replacement is required, it must be handled through an explicitly authorized Business administration workflow.

---

## 7. Manager

Manager is a configurable Business-level role.

A Manager may receive permissions such as:

* employee management;
* report access;
* inventory management;
* cash corrections;
* Branch management;
* cancellation;
* refund-related operations if explicitly granted;
* other authorized management functions.

Manager capabilities depend on actual assigned permissions and Branch scope.

Being assigned the Manager role alone does not automatically grant every management capability.

A Manager cannot grant another user a permission that the Manager does not possess within the applicable scope.

---

## 8. Cashier

Cashier is the primary POS operational role.

A Cashier may receive permissions for:

* creating orders;
* modifying orders;
* accepting orders;
* recording payments;
* managing cash sessions;
* cash handover;
* debt operations;
* cancellation where authorized;
* corrections where authorized;
* other POS functions.

Cashier permissions may be restricted by Branch.

Cashier actions must remain traceable to:

* employee;
* Business;
* Branch;
* cash register;
* cash session;
* device where applicable.

---

## 9. Waiter

Waiter permissions may include:

* viewing halls;
* viewing tables;
* creating orders;
* modifying orders;
* viewing order status;
* serving Ready items;
* requesting assistance;
* other waiter-specific operations.

Waiter permissions are configurable.

A Waiter does not automatically receive cashier, refund, inventory, payroll, or administrative permissions.

Waiter assignment and permissions are separate concepts.

---

## 10. Cook and Other Employees

Cook and other employee types are not required to have an inflexible permission set.

Their effective access is determined through:

**Role Permission + Employee Override + Branch Scope + Subscription**

This allows the Business to create customized operational roles without requiring separate hard-coded authorization models for every employee type.

---

## 11. Role Permission

A Role Permission defines the default permission configuration for employees assigned to that role.

For example:

**Cashier Role → Create Order = Allowed**

Employees assigned to that role receive the role permission unless an applicable employee override or higher-level restriction changes the effective result.

Role permissions are reusable and reduce repetitive configuration.

---

## 12. Employee Permission Override

An individual employee may receive an override.

An override may:

* grant a permission the employee's role normally does not have;
* remove a permission the employee's role normally has.

The override applies only to the selected employee and applicable scope.

Employee overrides must not allow the employee to exceed the authority of the person configuring the override.

---

## 13. Branch Scope

Permissions may be restricted by Branch.

An employee may have:

* permission in one Branch;
* permission in several selected Branches;
* Business-wide permission where explicitly authorized.

The system must evaluate the Branch where the operation is being performed.

Access to one Branch must not automatically grant access to another Branch.

---

## 14. Multi-Branch Employees

One employee may work in multiple Branches.

The same employee may have different effective permissions in different Branches.

For example:

* Cashier permissions in Branch A;
* Manager permissions in Branch B;
* no operational access to Branch C.

A separate account is not required for each Branch.

The employee's effective authorization must be resolved using the current Branch context.

---

## 15. Business-Wide Permissions

Business-wide permissions may be assigned where supported.

Business-wide scope allows the applicable operation across the Business, subject to:

* subscription entitlement;
* action-level permission;
* protected operations;
* Business rules;
* audit requirements.

Business-wide permission does not mean unrestricted system administration.

---

## 16. Effective Permission

The effective authorization for an operation is determined by all applicable authorization layers.

Conceptually:

**Effective Access = Subscription Eligibility + Permission + Branch Scope**

The permission component includes:

* employee identity;
* role;
* role permission;
* employee override;
* applicable scope.

All relevant conditions must be satisfied before an operation is allowed.

---

## 17. Subscription Entitlement

Permissions do not override subscription restrictions.

An employee may have permission for a function but still be unable to use it if the Business subscription does not include the function.

For example:

* an employee may have Payroll permission;
* the tariff may not include Payroll;
* Payroll remains unavailable.

Therefore:

**Permission ≠ Subscription Entitlement**

Both must be satisfied where applicable.

---

## 18. Permission Categories

Permissions should be organized into understandable functional groups.

Possible categories include:

* Business Management;
* Branch Management;
* Employee Management;
* Role and Permission Management;
* POS;
* Orders;
* Order Modification;
* Order Cancellation;
* Cash Register;
* Cash Session;
* Shift Handover;
* Inventory;
* Warehouse;
* Production;
* Purchases;
* Recipes;
* Menu;
* Sets;
* Pricing;
* Discounts;
* Payments;
* Debt;
* Refunds;
* Corrections;
* Reports;
* Payroll;
* Attendance;
* Expenses;
* Notifications;
* Audit;
* Subscription-related visibility.

The permission catalog may expand as the product grows.

---

## 19. Action-Level Permissions

Permissions should be defined at the action level where an operation has meaningful security or financial consequences.

Examples include:

* Create Order;
* Modify Order;
* Accept Order;
* Cancel Order;
* Refund;
* Record Payment;
* Manage Debt;
* Open Cash Session;
* Close Cash Session;
* Perform Cash Correction;
* Manage Inventory;
* Perform Inventory Adjustment;
* Create/Edit Recipe;
* Approve Recipe;
* Manage Sets;
* Override Branch Price;
* Manage Employees;
* Manage Permissions;
* View Reports;
* Export Reports.

A user having permission to view a resource does not automatically grant permission to modify it.

---

## 20. Recipe Permissions

Recipe access is a dedicated permission area.

Recipe permissions are independent from general product visibility.

An employee may be allowed to:

* view products;
* use products in POS;

while not being allowed to:

* view recipe components;
* view ingredient quantities;
* modify recipes;
* approve recipes.

Recipe visibility must therefore be explicitly controlled.

Only authorized users may approve a new or changed recipe.

The current business rule requires Owner approval for recipe activation.

---

## 21. Inventory Permissions

Inventory permissions must distinguish between different levels of operation.

Examples include:

* view inventory;
* view stock quantities;
* manage purchases;
* perform production;
* perform inventory adjustment;
* confirm stock discrepancy;
* manage warehouse configuration.

Manual stock removal must require the appropriate inventory adjustment permission.

Inventory adjustment requires an appropriate reason/comment according to the inventory rules.

Having inventory visibility does not automatically grant permission to alter stock.

---

## 22. Price and Menu Permissions

Menu and pricing permissions must be separated where appropriate.

Examples include:

* view menu;
* activate/deactivate product;
* modify product;
* manage categories;
* manage global prices;
* manage Branch price overrides;
* manage discounts;
* manage Sets.

Cashiers and ordinary employees must not be allowed to silently change standard menu prices unless explicitly authorized.

Discount usage is permission-controlled and follows Business-defined discount rules.

---

## 23. Order Modification Permissions

Order modification permissions must distinguish normal modification from sensitive operations.

Depending on Business configuration, separate permissions may exist for:

* modifying Draft orders;
* modifying Accepted orders;
* modifying quantities;
* changing customization;
* adding extras;
* removing ingredients;
* changing payment-related information;
* cancelling an order.

The permission model must not allow a user to bypass inventory or audit rules when modifying an order.

---

## 24. Order Cancellation Permission

Cancellation is a permission-controlled operation.

A user may cancel an order only if the user has the required cancellation permission.

The cancellation workflow requires:

* cancellation permission;
* reason;
* comment where required;
* applicable item-level inventory-return decision;
* kitchen notification where applicable;
* audit history.

Cancellation does not automatically grant refund authority.

Cancellation and refund are separate permissions and operations.

---

## 25. Refund Permission

Refund is a separate financial permission.

Refund authorization may be granted to:

* Manager;
* Owner;
* another explicitly authorized role.

Refund requires:

* refund permission;
* reason;
* comment where required;
* applicable payment type;
* full or partial refund scope.

A user with cancellation permission does not automatically receive refund permission.

A refund does not return inventory.

---

## 26. Cash and Correction Permissions

Cash permissions may include:

* open cash session;
* close cash session;
* record cash;
* handover cash;
* view expected amount after cashier entry;
* request correction;
* perform correction;
* approve exceptional correction.

Closed cash sessions are not reopened through ordinary workflows.

Corrections are handled through the correction mechanism and preserve the original information.

Correction limits and exceptional reopening rules are defined in the cash-session documents.

---

## 27. Shift Handover Permissions

Shift handover permissions must distinguish between:

* closing the current cashier's session;
* opening the next cashier's session;
* confirming received cash;
* viewing expected values after entry;
* recording shortage/overage;
* adding handover comments;
* handling correction requests.

A cashier must not gain administrative permission merely by performing a handover.

The handover remains associated with the responsible employees, Branch, register, and cash sessions.

---

## 28. Debt Permissions

Debt operations are permission-controlled.

Possible permissions include:

* create debt;
* edit debt customer information;
* record debt payment;
* record partial repayment;
* view debt;
* manage debt records.

The default operational workflow may allow Cashiers to manage debt where the Business grants the corresponding permission.

Debt access does not grant unrelated financial permissions such as refunds or cash corrections.

---

## 29. Set Permissions

Set management is separate from ordinary product sale.

Possible permissions include:

* view Sets;
* create Set;
* edit Set;
* activate/deactivate Set;
* configure Set composition;
* configure Set selling price.

A Set sale itself follows normal POS permissions.

Changing Set composition or configuration is a management operation and must require the appropriate permission.

Set configuration changes must retain history.

---

## 30. Employee Management Permissions

Employee management may include separate permissions for:

* view employees;
* create employee;
* edit employee;
* deactivate employee;
* assign Branch;
* assign role;
* configure permissions;
* change Branch scope;
* manage payroll-related information.

Having permission to create an employee does not automatically grant permission to give that employee every available permission.

The grantor must remain within their own authority.

---

## 31. Role Management Permissions

Role management may include:

* create role;
* edit role;
* clone role;
* assign role;
* modify role permissions;
* deactivate role where supported.

A user may configure only permissions they are authorized to grant.

A role must not be used as a mechanism for self-escalation.

---

## 32. Role Creation

Authorized users may create custom roles.

A role may be created:

* from scratch;
* from an existing role;
* from an employee's current permission configuration.

The resulting role becomes an independent configuration.

The source role or employee must not remain silently linked to the cloned role.

---

## 33. Role Cloning from Employee Permissions

A role may be created from an existing employee's current effective permission configuration.

The copied configuration becomes the starting state.

After cloning, the new role may be edited according to the creator's authority.

The new role does not remain dynamically linked to the original employee.

---

## 34. Role Cloning from Existing Roles

A role may be cloned from an existing role.

The cloned role receives a copy of the source configuration.

Later changes to the source role must not silently modify the cloned role.

The cloned role is an independent permission configuration.

---

## 35. Employee Creation

An authorized user may create an employee when:

* the user has employee-management permission;
* the Business has available employee capacity under the tariff;
* required employee information is provided;
* the user has authority to assign the selected role;
* the user has authority to assign the selected Branch scope.

Employee creation may include:

* identity information;
* role;
* Branch assignment;
* permission configuration;
* Branch-specific permission;
* employment-related configuration.

---

## 36. Manager Employee-Creation Restriction

A Manager may create employees only if the Manager has been granted the required employee-management permission.

The Manager role alone does not automatically provide employee-creation authority.

The Manager must also remain within the applicable Branch scope and subscription limits.

---

## 37. Permission Granting Rule

A user may grant only permissions that the user possesses and is authorized to delegate.

A user must not grant a permission above their own authority.

For example:

If Manager A does not possess `Manage Payroll`, Manager A cannot grant `Manage Payroll` to another employee.

Likewise, if Manager A has permission only for Branch A, Manager A cannot use that permission to grant Branch B access unless Manager A has authority over Branch B.

---

## 38. Privilege Escalation Prevention

The permission model must prevent employees from using permission configuration to elevate themselves.

An employee must not be able to:

* grant themselves new permissions;
* grant themselves broader Branch scope;
* promote themselves to Owner;
* create a role that gives themselves unauthorized privileges;
* use another role to bypass their actual authority;
* grant permissions beyond their own scope.

Permission-management operations must evaluate the actor's own effective authorization.

---

## 39. Permission Change Scope

When changing permissions, the authorized user may apply the change to:

* all employees assigned to a role;
* selected employees;
* selected Branches where permitted.

The target scope must be explicit.

A change intended for one employee must not silently affect unrelated employees.

---

## 40. Multiple Employee Selection

The permission interface may allow an administrator to select multiple employees.

If a permission change is applied to multiple selected employees:

* the command is explicit;
* each affected employee is identifiable;
* each affected scope is identifiable;
* the audit history preserves the affected targets.

The system must not obscure which employees were changed.

---

## 41. Latest Explicit Command Wins

For a specific permission and applicable scope, the latest explicit permission command determines the current effective state.

Example:

1. 10:00 — Recipe View = OFF
2. 11:00 — Recipe View = ON
3. 12:00 — Recipe View = OFF

The effective state after 12:00 is:

**Recipe View = OFF**

Previous states remain in history.

---

## 42. Permission Revert

Reverting a previous permission change does not delete history.

A revert creates a new permission event.

For example:

1. 10:00 — Recipe View = OFF
2. 11:00 — Recipe View = ON
3. 12:00 — Recipe View = OFF
4. 13:00 — Revert the 11:00 change

The 13:00 action is stored as a new event.

The original events remain unchanged.

---

## 43. Permission Conflict Resolution

When multiple permission sources apply to the same employee and action, the system must use deterministic rules.

The effective state must be explainable.

The system must be able to identify:

* which role supplied the permission;
* which employee override changed it;
* which Branch scope applies;
* which subscription entitlement applies;
* which explicit command is currently effective.

Permission evaluation must not depend on undocumented or unpredictable behavior.

---

## 44. Branch-Specific Role Configuration

The same role may have different effective permissions across Branches.

For example:

* Manager in Branch A → Inventory Management allowed;
* Manager in Branch B → Inventory Management denied.

The role model must support Branch-specific configuration without requiring separate employee accounts.

---

## 45. New Branch Permission Initialization

When a Business creates a new Branch, existing permission configuration may be used as the initial configuration for that Branch.

This provides a consistent starting point.

The Owner or another authorized administrator may then modify the new Branch's configuration.

The new Branch may ultimately have different permissions from existing Branches.

---

## 46. Permission UI Principles

The permission interface should remain simple even though the underlying authorization model is powerful.

When configuring an employee:

* Branch names should be clearly visible;
* the selected Branch should be visually identifiable;
* selected permissions should be clearly distinguishable;
* the effective configuration should be understandable;
* the interface should not expose unnecessary technical implementation details.

The interface must minimize accidental cross-Branch permission changes.

---

## 47. Role Templates

The system may provide role templates for common employee types.

Examples include:

* Cashier;
* Waiter;
* Cook;
* Manager.

Templates are starting configurations.

Authorized users may customize them according to their own authority and Business requirements.

Templates must not bypass subscription or permission restrictions.

---

## 48. Permission Changes and Audit

Important permission changes must be auditable.

The audit history must preserve:

* actor;
* target employee or role;
* Business;
* Branch scope;
* permission;
* previous state;
* new state;
* timestamp;
* change type;
* reason where required.

Permission history must not be silently deleted when an employee or role changes.

---

## 49. Employee Deactivation

When an employee leaves the Business or should no longer access the system, the employee should normally be deactivated rather than deleted.

Deactivation must:

* prevent unauthorized new access;
* preserve historical identity;
* preserve historical transactions;
* preserve audit references.

Historical operations must continue identifying the original employee.

---

## 50. Employee Role Changes

An employee's current role may change over time.

Changing the role must not rewrite historical records.

Historical operations must continue to represent the employee identity and authorization context relevant to the original event.

For example, if an employee was a Cashier when an order was created, later promotion to Manager must not change the historical order actor into a Manager.

---

## 51. Employee Branch Assignment Changes

An employee's Branch assignments may change over time.

Changing Branch assignment must not move historical transactions to the new Branch.

Historical operations retain their original Branch.

Future operations use the employee's new effective Branch scope.

---

## 52. Permission Changes and Historical Operations

Permission changes apply to future authorization decisions unless a specific offline authorization period temporarily preserves previously issued authorization.

Historical operations remain unchanged.

Changing a permission does not:

* modify old orders;
* change old cash sessions;
* change old inventory events;
* change old reports;
* rewrite audit history.

---

## 53. Permission and Trusted Devices

Trusted-device status does not grant Business permissions.

A trusted device establishes that the device is authorized for the relevant security context.

The employee's own:

* permissions;
* Branch scope;
* subscription entitlement;
* Business membership

must still be respected.

Trusted-device status cannot be used to bypass authorization.

---

## 54. Permission and Offline Operation

Offline transactions must operate using valid locally authorized permission state.

Offline authorization must be:

* server-issued;
* time-bounded;
* associated with the authorized employee/device context;
* protected against replay or tampering.

Offline mode must not become a mechanism for bypassing:

* permissions;
* Branch scope;
* subscription rules;
* Business isolation;
* business rules.

When synchronization occurs, the server validates the transaction against authoritative rules.

---

## 55. Permission Changes During Offline Operation

If an employee's permission changes while a trusted device is offline, the device may temporarily operate under its previously issued valid offline authorization according to the offline authorization period.

This does not create permanent permission.

Once the device reconnects:

* the server becomes authoritative;
* current permissions are evaluated;
* synchronization is validated;
* unauthorized future operations must be blocked.

The detailed conflict behavior belongs to the Offline Operation and Synchronization document.

---

## 56. Permission and Subscription Expiration

When the Business subscription expires:

* employee permissions do not disappear from history;
* modifying operations are blocked according to subscription rules;
* permitted read-only access remains available;
* Excel export remains available where allowed;
* Branch scope continues to restrict what the employee may view.

After reactivation, the employee's existing permission configuration may become effective again subject to the active subscription.

---

## 57. Permission and Report Access

Report visibility is permission-controlled.

A user may receive permission to:

* view reports;
* view specific report categories;
* view Branch reports;
* view Business-wide reports;
* export reports.

Report access must also respect Branch scope and subscription entitlement.

A user must not receive restricted Branch information through an export when the user cannot view that Branch directly.

---

## 58. Permission and Notifications

Notifications containing protected operational information must respect the recipient's authorization scope.

For example:

* a Branch Manager may receive Branch-specific cash discrepancy notifications;
* an Owner may receive Business-wide notifications;
* a user without inventory permission should not receive restricted inventory details merely through notifications.

Notifications must not become an authorization bypass.

---

## 59. Permission and Audit Access

Audit access is itself permission-controlled.

A user may be allowed to:

* view audit history;
* view selected categories;
* view Branch audit history;
* view Business-wide audit history;
* export audit data.

Access to audit records must respect Business and Branch scope.

---

## 60. Permission and Correction Operations

Correction operations must require dedicated authorization where applicable.

Examples include:

* cash correction;
* inventory correction;
* order correction;
* correction request handling;
* exceptional cash-session correction.

Correction permission does not automatically grant unrelated administrative authority.

Every correction must preserve the original information and record the reason.

---

## 61. Permission and Equipment Broken State

Equipment Broken is an operational availability state, not a permission.

An employee with POS permission cannot sell a product that is unavailable because the relevant equipment is marked as broken.

Likewise, granting permission does not override stock shortage or other business rules.

This demonstrates the distinction between:

**Authorization** and **Operational Availability**.

---

## 62. Permission Does Not Override Business Rules

Permissions allow an authorized user to attempt an operation.

They do not automatically override business rules such as:

* no negative stock;
* insufficient inventory blocks sale;
* Served inventory cannot be returned;
* Set with unavailable mandatory component cannot be sold;
* closed cash session cannot be reopened through normal workflow;
* historical records cannot be silently rewritten;
* subscription limits cannot be bypassed;
* tenant isolation cannot be bypassed.

Any exceptional override must be explicitly defined as a separate authorized business operation.

---

## 63. Permission Changes Must Be Auditable

Every important permission change must create an immutable historical event.

The event should identify:

* actor;
* target;
* Business;
* Branch scope;
* permission;
* old value;
* new value;
* timestamp;
* reason where required.

Deleting or modifying the historical permission event is not allowed through normal Business workflows.

---

## 64. Permission Model Summary

| Area                         | Rule                                       |
| ---------------------------- | ------------------------------------------ |
| Super Admin                  | Platform-level                             |
| Owner                        | Protected Business-level role              |
| Multiple Owners              | Allowed within tariff limit                |
| Manager                      | Permission-based                           |
| Cashier                      | POS-oriented permission set                |
| Waiter                       | Hall/order/service-oriented permission set |
| Cook                         | Configurable permission set                |
| Custom roles                 | Supported                                  |
| Role permissions             | Supported                                  |
| Employee overrides           | Supported                                  |
| Multi-Branch employee        | Supported                                  |
| Branch-specific permissions  | Supported                                  |
| Business-wide scope          | Supported where authorized                 |
| Action-level permissions     | Supported                                  |
| Recipe visibility            | Independently controlled                   |
| Recipe approval              | Owner authorization required               |
| Cancellation                 | Separate permission                        |
| Refund                       | Separate permission                        |
| Inventory adjustment         | Separate permission                        |
| Cash correction              | Separate permission                        |
| Employee creation            | Permission + tariff limit                  |
| Permission delegation        | Cannot exceed grantor authority            |
| Self-escalation              | Not allowed                                |
| Owner self-promotion         | Not allowed                                |
| Role cloning                 | Supported                                  |
| Employee-based role cloning  | Supported                                  |
| Latest explicit command      | Determines current state                   |
| Revert                       | Creates new event                          |
| Permission history           | Preserved                                  |
| Employee deactivation        | Supported                                  |
| Historical employee identity | Preserved                                  |
| Trusted device               | Does not grant permissions                 |
| Offline authorization        | Must remain bounded                        |
| Subscription                 | Can restrict functionality                 |
| Branch scope                 | Always enforced                            |
| Audit                        | Required for important changes             |

---

## 65. Business Model Boundary

This document defines business-level authorization behavior.

Detailed technical implementation belongs to later documents, including:

* authentication architecture;
* authorization middleware;
* permission storage;
* role storage;
* database constraints;
* API authorization;
* frontend authorization;
* offline permission snapshots;
* synchronization validation;
* audit event storage.

Technical implementation must preserve the business rules defined in this document.

---

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

