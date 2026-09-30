# Product Overview

**Document ID:** BA-01
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

FastFood ERP is a SaaS-based ERP system designed for restaurants and fast-food businesses.

The system allows business owners to manage one or multiple branches from a unified platform, including employees, orders, cash operations, inventory, recipes, menu, pricing, payroll, reports, and business operations.

The primary product requirement is that the system may contain many advanced capabilities while keeping daily workflows simple, fast, and practical for users.

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
* business-level settings.

A business may have multiple Owners.

The maximum number of Owners is controlled by the applicable subscription tariff.

### 3.3. Manager

Manager performs management operations within the permissions assigned by the business.

A Manager may:

* be assigned to one or multiple branches;
* receive branch-specific permissions;
* perform selected operations on behalf of the business.

A Manager cannot grant permissions that they do not personally possess.

### 3.4. Cashier

Cashier is a primary POS user.

Depending on assigned permissions, a Cashier can:

* create orders;
* modify orders;
* process payments;
* work with cash sessions;
* close a cash session;
* participate in cash handover;
* participate in correction workflows.

Cashier actions must be associated with the employee identity, branch, cash register, cash session, and trusted device.

### 3.5. Waiter

Waiter capabilities are determined by the assigned role and permissions.

Possible responsibilities include:

* working with halls and tables;
* creating orders;
* viewing orders;
* monitoring order status.

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
* offline operation capability.

An employee may work in multiple branches.

The same employee may have different permissions in different branches.

Branch-specific permissions are therefore part of the core business model rather than an optional extension.

## 5. POS Model

POS is one of the primary operational components of the system.

The initial order types are:

* Hall / Dine-in
* Takeaway
* Phone Delivery

The current system does not maintain a permanent customer database.

For delivery orders, the order may store:

* phone number;
* delivery address.

These values belong to the order record.

Online ordering and a full customer management system may be introduced in later phases.

## 6. Cash Register Model

Each branch normally operates with one cash register.

The architecture should not prevent future support for multiple registers, but the current business process is designed around one register per branch.

The primary relationship is:

**Branch → Cash Register → Cash Sessions**

A cash session:

* is opened manually;
* belongs to one cashier shift;
* is closed manually;
* calculates expected values;
* receives the cashier's actual cash amount;
* records the resulting difference.

A closed cash session is never directly reopened.

Any required correction must use the dedicated correction workflow.

## 7. Offline-First Operation

A branch must be able to continue core operations when the internet connection is temporarily unavailable.

Offline operation is supported through:

* previously trusted devices;
* time-limited offline authorization;
* encrypted local storage;
* locally generated UUIDs;
* queued local transactions;
* synchronization when connectivity returns.

A completely new device cannot start operating offline.

The device must first connect to the server while online, complete registration/verification, and become a trusted device.

## 8. Security Model

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
* Business/Restaurant UUID;
* Branch UUID;
* Cash Register UUID;
* Cash Session UUID;
* Device UUID;
* timestamp.

This allows the system to determine who created a transaction, where it was created, during which cash session, and from which trusted device.

## 9. Inventory and Recipe Model

The inventory system supports two primary product types:

* Finished Product
* Semi-Finished Product

A product that has a recipe cannot be permanently deleted.

Instead, it must be archived.

Recipes are also versioned through historical/archived records rather than silently replacing previous definitions.

Recipe dependencies can represent relationships such as:

**Raw Material → Semi-Finished Product → Finished Product**

Inventory operations must preserve these dependencies.

Negative stock is not allowed.

If the required quantity is unavailable, the affected product cannot be ordered.

Once the relevant inventory requirement is satisfied, ordering may become available again.

## 10. Menu and Pricing

The system maintains a global menu and recipe structure for the business.

Approved recipes may become part of the global menu and may then be enabled for permitted branches.

The same approved recipe is intended to remain consistent across branches.

A branch may override a global product price for its own operation if the responsible user has the required permission.

During order creation, pricing may be affected by:

* recipe components;
* removed components;
* extras/add-ons;
* other supported customizations.

Combos exist as predefined product structures.

Components inside a combo cannot be freely replaced with another product.

## 11. Reports

The system provides operational and management reports covering major business activities.

Important reporting areas include:

* cash sessions;
* cashiers;
* orders;
* payments;
* discrepancies;
* corrections;
* correction requests;
* audit logs;
* change history;
* inventory;
* employees;
* payroll;
* branch performance.

Report access is controlled by permissions and branch scope.

The supported user-facing export format is Excel (`.xlsx`).

## 12. Report Versioning

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

## 13. Subscription Lifecycle

FastFood ERP operates as a subscription-based SaaS product.

When a subscription expires:

* modifying functions are blocked;
* users can continue viewing existing data;
* relevant lists and sections can be exported to Excel.

If the subscription is not reactivated within 60 days, the business data is permanently deleted according to the data lifecycle rules.

Users receive advance notifications about the upcoming deletion deadline.

## 14. Performance Principle

The system follows the principle:

> A feature-rich ERP must not become a complicated or slow POS.

Daily operational workflows should remain fast and simple, especially:

* POS;
* order creation;
* payment;
* cash operations;
* shift handover;
* inventory operations.

The system must operate on ordinary POS and office hardware without requiring unnecessarily powerful hardware.

Security, audit, synchronization, and other infrastructure mechanisms must be designed to minimize impact on normal transactional performance.

## 15. Product Design Principles

### 15.1. Simplicity

Complex internal architecture must not unnecessarily increase the complexity of the user interface.

### 15.2. Auditability

Important business changes must not occur without traceable history.

The system must preserve who performed an action, what changed, when it changed, and why when a reason is required.

### 15.3. Offline Continuity

Temporary internet failure must not unnecessarily stop core branch operations.

### 15.4. Security Without Excessive Friction

Security controls should protect the system without requiring unnecessary verification for every normal operation.

### 15.5. Scalability

The initial subscription model supports up to 10 branches, while the architecture must not prevent future expansion.

### 15.6. Historical Integrity

Original business records must not be silently overwritten.

Corrections and changes must preserve the original value and maintain the relevant change history.

### 15.7. Modular Architecture

Business capabilities should remain logically separated so that the system can evolve without tightly coupling unrelated domains.

### 15.8. Documentation-First Development

Business rules and major architectural decisions must be documented before implementation.

Major changes must be recorded through the project's ADR process.

## 16. Current Out of Scope

The following capabilities are not part of the current core scope:

* online ordering;
* Telegram bot;
* customer mobile application;
* full customer CRM;
* contracts;
* advanced delivery management.

These capabilities may be considered later as separate business requirements.

## 17. Core Product Flow

At a high level, the product operates through the following structure:

**Business → Branch → Employees/Permissions → POS → Orders → Payments → Cash Session → Reports**

Inventory and recipes support the operational flow:

**Recipes → Inventory → Menu → Orders → Stock Deduction → Reports**

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

