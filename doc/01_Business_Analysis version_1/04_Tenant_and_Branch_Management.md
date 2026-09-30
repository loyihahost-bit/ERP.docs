# Tenant and Branch Management

**Document ID:** BA-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for Business/Tenant and Branch management in FastFood ERP.

It describes how businesses are represented, how branches belong to a business, how branch-specific operations are separated, and how users can be granted access across one or multiple branches.

## 2. Business/Tenant Definition

A Business/Tenant is the primary organizational entity that uses FastFood ERP.

A business represents one restaurant company or fast-food organization and owns its operational data.

A business may contain:

* branches;
* Owners;
* employees;
* roles;
* permissions;
* menus;
* recipes;
* warehouses;
* inventory;
* cash registers;
* orders;
* expenses;
* payroll records;
* reports;
* audit history.

All operational data must belong to exactly one business.

## 3. Tenant Isolation

Business data must be logically isolated.

A user belonging to one business must not access another business's operational data unless the user has an explicitly authorized platform-level role.

Tenant isolation applies to:

* business data;
* branch data;
* employee data;
* orders;
* inventory;
* recipes;
* cash sessions;
* reports;
* exports;
* audit records;
* offline data;
* synchronization operations.

Tenant isolation is a core business requirement and must not depend only on user-interface restrictions.

## 4. Business Creation

Business creation is performed by the **Super Admin**.

When creating a business, the platform establishes the business as a separate tenant.

The business must then receive:

* an applicable subscription/tariff;
* one or more authorized Owners;
* required business configuration.

The business cannot perform normal operations until the required initial configuration has been completed.

## 5. Branch Definition

A Branch represents a physical or operational location belonging to a Business.

A branch operates within the business's overall configuration but maintains its own operational state.

A branch may have:

* employees;
* branch-specific permissions;
* warehouse;
* inventory;
* cash register;
* cash sessions;
* orders;
* expenses;
* branch reports.

## 6. Branch Ownership

Every branch belongs to exactly one business.

A branch cannot belong simultaneously to multiple businesses.

Moving a branch between businesses is not treated as a normal daily operation and must not be supported as a simple reassignment that could compromise historical data.

If a future business-transfer capability is required, it must be defined separately as a controlled business process.

## 7. Branch Limit

The maximum number of active branches is determined by the business's subscription tariff.

The initial product model supports up to 10 branches depending on the selected tariff.

If the branch limit is reached:

* a new branch cannot be created;
* existing branches continue operating;
* the authorized user is informed that the subscription limit has been reached.

Increasing the tariff limit allows additional branches to be created.

## 8. Branch Creation

Authorized business users may create branches when:

* their role has branch-management permission;
* the subscription permits another branch;
* required business information is provided.

Branch creation must be auditable.

The system should record:

* who created the branch;
* when it was created;
* which business it belongs to;
* initial configuration;
* relevant tariff state.

## 9. Branch Activation

A branch must have an operational status.

At minimum, the business model must distinguish between:

* Active branch;
* Inactive/archived branch.

An inactive or archived branch must not receive new normal operational transactions unless explicitly reactivated.

Historical information belonging to an inactive branch must remain preserved.

## 10. Branch Deactivation

A branch may be deactivated when the business no longer operates it.

Deactivation must not silently delete:

* orders;
* cash sessions;
* inventory history;
* reports;
* employee history;
* audit records;
* other historical business data.

The branch's historical data remains part of the business's records.

## 11. Branch Reuse

An inactive branch should not be reused by simply replacing its identity or historical records.

If a business opens a new physical location, a new branch should normally be created.

This preserves historical separation between different operational periods and locations.

## 12. Branch-Specific Data

The following data may be branch-specific:

* employees;
* permissions;
* warehouses;
* inventory;
* cash registers;
* cash sessions;
* orders;
* expenses;
* operational reports;
* branch-specific pricing;
* branch-specific operational settings.

Global business data may be shared across branches where explicitly defined.

## 13. Global vs Branch Data

The business model distinguishes between business-level and branch-level information.

### Business-Level Examples

* business identity;
* subscription;
* tariff;
* global menu;
* approved recipes;
* employee definitions;
* role definitions;
* business-wide settings.

### Branch-Level Examples

* branch employees;
* branch permissions;
* inventory;
* warehouse;
* cash sessions;
* orders;
* branch expenses;
* branch-specific price overrides.

A later technical data model must preserve this distinction.

## 14. Employee Branch Assignment

An employee may be assigned to:

* one branch;
* multiple branches;
* business-wide scope where explicitly authorized.

Branch assignment determines where the employee may operate.

Branch assignment and permission assignment are separate concepts.

An employee may be assigned to a branch but still lack permission to perform a particular operation there.

## 15. Branch-Specific Permissions

The same employee may have different permissions in different branches.

For example:

* Employee A may have cashier permissions in Branch 1;
* Employee A may have manager permissions in Branch 2;
* Employee A may have no operational access to Branch 3.

The permission system must support this model without requiring separate employee accounts for each branch.

## 16. Role Scope

A role may be configured as:

* single-branch;
* multi-branch;
* business-wide.

The Owner determines the appropriate scope when configuring employee access.

The selected scope must be enforced consistently throughout the application.

## 17. Branch Permission Inheritance

When a new branch is added, existing role configuration may be used as the initial permission configuration for that branch.

The initial configuration is a starting point rather than an immutable rule.

The Owner may subsequently customize the new branch's permissions.

This allows businesses to maintain consistency while still supporting branch-specific differences.

## 18. Branch Selection in the User Interface

When a user has access to multiple branches, the system must clearly identify the currently selected branch.

The selected branch should be visually distinguishable from other available branches.

Branch-specific screens must clearly operate within the selected branch context.

The interface must minimize the risk of accidentally performing an operation in the wrong branch.

## 19. Branch Context

The selected branch context must be consistently applied to branch-scoped operations.

Examples include:

* order creation;
* cash session operations;
* inventory changes;
* warehouse operations;
* branch expenses;
* branch reports;
* employee branch permissions.

A user must not be able to unintentionally perform a branch-specific operation against another branch simply because both branches are accessible.

## 20. Branch Switching

Users with access to multiple branches may switch their active branch context.

Switching branch context must not:

* modify historical data;
* change the user's permissions;
* grant additional access;
* bypass branch restrictions.

The system recalculates the effective branch scope based on the selected branch.

## 21. Branch and Cash Register

Each branch normally has one cash register.

The business model is:

**Business → Branch → Cash Register → Cash Sessions**

The current business workflow does not require multiple cash registers within one branch.

The architecture should not unnecessarily prevent future expansion to multiple registers.

## 22. Branch and Inventory

Inventory is managed within branch/warehouse scope.

A branch may have its own warehouse or warehouse structure.

Stock quantities must be traceable to the relevant branch and warehouse.

Inventory changes in one branch must not silently modify another branch's stock.

Any future inter-branch transfer mechanism must be explicitly defined as a business operation.

## 23. Branch and Menu

The business may maintain a global menu.

A branch may be allowed to use selected products from the global menu according to the business configuration.

Global recipe consistency must be preserved where the product is shared across branches.

Branch-specific pricing may be configured where the responsible user has the required permission.

## 24. Branch and Employees

Employees are business-level identities that may receive branch assignments.

A branch may have:

* cashiers;
* waiters;
* cooks;
* managers;
* other employees.

An employee's effective access is determined by:

**Employee Identity + Role + Permission + Branch Scope**

This prevents branch membership alone from granting unrestricted access.

## 25. Branch and Reports

Reports may be generated for:

* a single branch;
* multiple selected branches;
* the entire business,

depending on the user's permissions and report scope.

A user without access to a branch must not receive that branch's data through a report or export.

Report scope must therefore follow the same branch access rules as normal application screens.

## 26. Branch and Offline Operation

Each branch may operate offline through trusted devices.

Offline transactions must remain associated with the correct:

* business;
* branch;
* employee;
* device;
* relevant operational context.

When synchronization occurs, the server must validate that the transaction belongs to the correct business and branch.

A device trusted for one business or branch must not automatically gain access to another business or unauthorized branch.

## 27. Branch Deletion

Normal branch deletion is not permitted when historical business data exists.

The preferred business operation is deactivation/archive.

Historical records must remain available according to the business's data lifecycle rules.

Permanent deletion, where legally or operationally required, follows the broader business data deletion process rather than ordinary branch management.

## 28. Branch Configuration

Branch configuration may include:

* branch identity;
* operational status;
* employees;
* warehouse;
* menu availability;
* pricing overrides;
* cash register;
* operational settings;
* branch-specific permissions.

Configuration changes must respect:

* user permissions;
* subscription limits;
* business rules;
* audit requirements.

## 29. Branch Management Permissions

Branch management is permission-controlled.

Authorized users may receive permissions for operations such as:

* create branch;
* edit branch;
* deactivate branch;
* configure branch;
* manage branch employees;
* view branch reports.

Having access to one branch does not automatically grant management access to all branches.

## 30. Cross-Branch Management

An Owner or authorized employee may receive cross-branch access.

Cross-branch access must be explicitly granted.

The user must still operate within the permissions assigned to each branch.

Cross-branch access is not equivalent to unrestricted business-wide access.

## 31. Branch-Level Security

Branch scope must be enforced across all relevant layers.

This includes:

* user interface;
* API authorization;
* business logic;
* database access;
* report generation;
* Excel export;
* offline synchronization;
* background processing.

Branch restrictions must not be implemented only as UI filters.

## 32. Business and Branch Lifecycle

The general lifecycle is:

**Business Creation**
→ **Subscription Assignment**
→ **Owner Configuration**
→ **Branch Creation**
→ **Branch Configuration**
→ **Employee Assignment**
→ **Operational Activity**
→ **Branch Deactivation if Required**

Business-level deletion and branch-level deactivation are separate concepts.

## 33. Business Rules Summary

| Rule                         | Requirement                             |
| ---------------------------- | --------------------------------------- |
| Business ownership           | One business owns its operational data  |
| Tenant isolation             | Required                                |
| Business creation            | Super Admin                             |
| Initial branch capacity      | Up to 10 depending on tariff            |
| Branch ownership             | One business per branch                 |
| Branch status                | Active / Inactive or Archived           |
| Historical branch data       | Preserved                               |
| Normal branch deletion       | Not allowed when historical data exists |
| Employee multi-branch access | Supported                               |
| Branch-specific permissions  | Supported                               |
|                              |                                         |

