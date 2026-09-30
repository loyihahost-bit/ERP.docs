# Business Model

**Document ID:** BA-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business model of FastFood ERP.

It describes how the platform is provided to businesses, how businesses are represented in the system, how users interact with the platform, and how subscription-based access controls the available resources and functionality.

This document focuses on business-level rules rather than technical implementation details.

## 2. Business Model Overview

FastFood ERP is a **Software as a Service (SaaS)** product.

The platform is operated centrally and provided to restaurant and fast-food businesses through subscription plans.

The general structure is:

**FastFood ERP Platform → Business/Tenant → Branches → Employees → Operations**

A business subscribes to the platform and receives access according to its configured subscription tariff.

The tariff determines the allowed capacity and enabled functionality.

## 3. Business/Tenant

A business is the primary customer entity within the platform.

A business represents a restaurant company or fast-food organization that uses FastFood ERP.

A business may contain:

* one or more branches;
* one or more Owners;
* employees;
* roles;
* menus;
* recipes;
* warehouses;
* inventory;
* cash registers;
* orders;
* reports;
* expenses;
* payroll records;
* other operational data.

Business data must remain logically isolated from other businesses.

One business must not be able to access another business's operational data.

## 4. Multi-Branch Business

A business may operate multiple branches.

The initial subscription model supports up to **10 branches**, depending on the selected tariff.

The platform must be designed so that the initial limit does not create an architectural restriction against future expansion.

Each branch represents a separate operational unit within the same business.

Branch-specific data may include:

* employees;
* permissions;
* warehouse;
* inventory;
* cash sessions;
* orders;
* expenses;
* operational reports.

## 5. Business Ownership

A business may have multiple Owners.

The number of Owners is controlled by the subscription tariff configured by the Super Admin.

Owner is a protected business-level role.

Other employees cannot:

* promote themselves to Owner;
* reduce Owner permissions;
* remove an Owner;
* modify the protected Owner role without the required authority.

The existence of multiple Owners allows a business to distribute administrative responsibility without creating an unrestricted privilege escalation path.

## 6. Subscription-Based Access

Access to the platform is controlled through subscription.

A subscription determines which resources and capabilities are available to the business.

The subscription model may control:

* number of branches;
* number of Owners;
* number of employees;
* enabled modules;
* enabled functions;
* other platform-defined limits.

The Super Admin can create and configure tariff plans according to the platform's commercial requirements.

A tariff is therefore a configurable business policy rather than a permanently hard-coded set of limits.

## 7. Tariff Structure

A tariff may contain multiple categories of restrictions.

### 7.1. Capacity Limits

Examples include:

* maximum number of branches;
* maximum number of Owners;
* maximum number of employees.

### 7.2. Feature Availability

A tariff may enable or disable specific functionality.

Examples may include:

* advanced reporting;
* payroll functionality;
* selected inventory features;
* additional management capabilities.

### 7.3. Future Limits

The architecture should allow additional tariff limits to be introduced later without requiring a redesign of the entire subscription model.

## 8. Tariff Enforcement

When a business reaches a tariff limit, the system must prevent operations that would exceed the configured limit.

For example:

If a tariff allows 10 branches and the business already has 10 active branches, creating an additional branch must be blocked until the subscription configuration permits it.

The system should clearly communicate:

* which limit was reached;
* the current value;
* the allowed value;
* what action is required to continue.

The system must not silently create resources beyond the configured tariff limit.

## 9. Subscription Expiration

Subscription expiration changes the business's access state.

After expiration:

### Allowed

Users may:

* log in;
* view existing business data;
* review historical information;
* access permitted read-only sections;
* export relevant data to Excel.

### Blocked

Operations that modify business data are blocked.

Examples include:

* creating new orders;
* modifying operational data;
* creating employees;
* changing recipes;
* changing inventory;
* creating new business records.

The exact set of blocked operations is controlled by the subscription lifecycle rules.

## 10. Expired Data Retention Period

After subscription expiration, the business receives a **60-day reactivation period**.

During this period:

* business data remains available in read-only mode;
* users can review existing information;
* relevant data can be exported;
* subscription reactivation can restore normal operation.

If the subscription is not reactivated within 60 days, the business data is permanently deleted according to the platform's data lifecycle policy.

There is no additional user-accessible archive period after the 60-day expiration period.

## 11. Subscription Notifications

The system must notify relevant users before important subscription deadlines.

Notifications should provide enough information for the user to understand:

* subscription status;
* expiration date;
* remaining reactivation period;
* upcoming data deletion deadline when applicable;
* required action.

The exact notification schedule is defined in the subscription and notification business rules.

## 12. Super Admin Business Role

Super Admin operates at the platform level.

Super Admin responsibilities include:

* creating business accounts;
* managing tariff plans;
* configuring subscription limits;
* controlling platform-level feature availability;
* managing platform-level administrative settings.

Super Admin does not automatically become an operational Owner of every business.

Business-level operations remain under the business's own ownership and permission model.

## 13. Business Administration

The Owner is responsible for business-level administration.

Owner responsibilities may include:

* branch management;
* employee management;
* role management;
* permission management;
* menu management;
* recipe management;
* inventory management;
* pricing;
* expenses;
* payroll;
* reports;
* dashboard configuration.

Owner actions remain subject to the platform's permission and subscription limits.

## 14. Employee Model

Employees belong to a business and may be assigned to one or more branches.

An employee's effective access is determined by:

**Role Permission + Employee Override + Branch Scope**

This allows:

* different employees with the same role to have different permissions;
* the same employee to have different permissions in different branches;
* business owners to customize operational responsibilities.

Employee limits are enforced according to the active subscription tariff.

## 15. Branch Scope

Permissions may be configured at different scopes.

An employee may have:

* access to one branch;
* access to multiple selected branches;
* business-wide access where explicitly authorized.

The Owner determines whether a role is intended to operate across branches or within a single branch.

Branch scope must always be considered when determining whether an employee is allowed to perform an operation.

## 16. Business Data Ownership

Operational data belongs to the business that generated it.

Examples include:

* orders;
* cash sessions;
* inventory records;
* recipes;
* reports;
* employee records;
* payroll records;
* audit records.

Data must remain associated with its originating business and relevant branch.

The platform must maintain tenant isolation when processing, storing, synchronizing, and reporting business data.

## 17. Business Isolation

The system must prevent cross-business access.

A user authenticated for Business A must not be able to access Business B's data unless the user has an explicitly authorized platform-level role that permits such access.

Business isolation applies to:

* API requests;
* database queries;
* reports;
* exports;
* offline data;
* synchronization;
* background processing;
* notifications.

## 18. Business Operational Flow

The general business lifecycle is:

**Business Registration**
→ **Tariff Selection**
→ **Subscription Activation**
→ **Branch Configuration**
→ **Owner Configuration**
→ **Employee and Permission Setup**
→ **Menu and Recipe Setup**
→ **Inventory Setup**
→ **Daily Operations**
→ **Reports and Monitoring**

The business then continues normal operations while its subscription remains active.

## 19. Commercial Model Principle

The platform should support a configurable subscription model rather than embedding commercial rules directly into individual application features.

Business limits should be determined from subscription configuration.

This allows the Super Admin to introduce new tariffs or modify existing commercial offerings without requiring major application changes.

## 20. Resource Expansion

When a business needs more capacity than its current tariff allows, the system should not require manual data migration simply to increase the configured limits.

For example, increasing the branch limit should allow the business to create additional branches without changing the existing branch data structure.

The same principle applies to:

* employees;
* Owners;
* enabled modules;
* other configurable tariff resources.

## 21. Business Model Principles

### 21.1. Tenant Isolation

Each business must have isolated operational data.

### 21.2. Configurable Commercial Rules

Subscription limits should be configurable by Super Admin.

### 21.3. Permission-Based Administration

Business users should only perform actions allowed by their permissions and branch scope.

### 21.4. Subscription Enforcement

The platform must enforce tariff limits consistently across all relevant interfaces and operations.

### 21.5. Read-Only Expiration Mode

Subscription expiration should preserve data visibility during the defined retention period while blocking modifications.

### 21.6. Historical Preservation

Subscription restrictions must not destroy business history immediately.

The defined 60-day retention period provides the business with an opportunity to reactivate or export its data.

## 22. Business Model Boundaries

This document defines the overall business model.

Detailed rules for specific domains are defined in separate Business Analysis documents.

Examples:

* subscription configuration → `03_Subscription_and_Tariffs.md`
* branch structure → `04_Tenant_and_Branch_Management.md`
* permissions → `05_Users_Roles_and_Permissions.md`
* authentication → `06_Authentication_and_Trusted_Devices.md`
* POS → `08_POS_and_Order_Management.md`
* cash → `09_Cash_Register_and_Cash_Sessions.md`
* reports → `16_Reports_and_Dashboards.md`
* data deletion → `19_Data_Lifecycle_and_Deletion.md`

This separation prevents one document from becoming the single source for every detailed business rule.

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

