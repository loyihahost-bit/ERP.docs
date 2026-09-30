# Business Analysis Documentation

**Document ID:** BA-README
**Status:** Approved
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `agents/AGENTS.md`

---

## 1. Purpose

This directory contains the approved business analysis documentation for the FastFood ERP system.

The purpose of these documents is to define:

* what the system must support;
* how the business operates through the system;
* what business rules must be enforced;
* how users, branches, subscriptions, and permissions interact;
* how operational data is created, changed, preserved, reported, and eventually deleted;
* which requirements are intentionally outside the current business scope.

These documents represent the business-level source of truth before detailed system, domain, architecture, database, backend, frontend, security, and deployment decisions are made.

---

## 2. Business Analysis Principles

The Business Analysis documentation follows these principles:

1. Business requirements are defined before implementation details.
2. Business rules must be explicit and traceable.
3. Historical business information must not be silently overwritten.
4. User permissions and subscription entitlements are separate control layers.
5. Business and branch data must remain isolated.
6. Offline operation must preserve the same business rules as online operation.
7. Operational workflows must remain practical for restaurant staff.
8. Security controls must not unnecessarily reduce POS performance.
9. Historical records must remain understandable after corrections.
10. Requirements that are not explicitly approved must not be treated as implemented requirements.

---

## 3. Document Structure

The Business Analysis documents are organized as follows:

| ID | Document                                                                               | Purpose                                                              |
| -- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 01 | [Product Overview](./01_Product_Overview.md)                                           | Defines the product purpose, scope, users, and major capabilities    |
| 02 | [Business Model](./02_Business_Model.md)                                               | Defines the SaaS business and tenant model                           |
| 03 | [Subscription and Tariffs](./03_Subscription_and_Tariffs.md)                           | Defines subscriptions, tariffs, limits, expiration, and reactivation |
| 04 | [Tenant and Branch Management](./04_Tenant_and_Branch_Management.md)                   | Defines business and branch organization                             |
| 05 | [Users, Roles and Permissions](./05_Users_Roles_and_Permissions.md)                    | Defines user identity, roles, permissions, and branch scope          |
| 06 | [Authentication and Trusted Devices](./06_Authentication_and_Trusted_Devices.md)       | Defines authentication and trusted-device rules                      |
| 07 | [Offline Operation and Synchronization](./07_Offline_Operation_and_Synchronization.md) | Defines offline operation and synchronization behavior               |
| 08 | [POS and Order Management](./08_POS_and_Order_Management.md)                           | Defines order creation, editing, kitchen routing, and POS behavior   |
| 09 | [Cash Register and Cash Sessions](./09_Cash_Register_and_Cash_Sessions.md)             | Defines cash register and cash-session lifecycle                     |
| 10 | [Shift Handover](./10_Shift_Handover.md)                                               | Defines cashier responsibility transfer                              |
| 11 | [Inventory and Warehouse](./11_Inventory_and_Warehouse.md)                             | Defines stock, warehouse, purchasing, and inventory rules            |
| 12 | [Products and Recipes](./12_Products_and_Recipes.md)                                   | Defines products, recipes, preparation, and recipe lifecycle         |
| 13 | [Menu and Pricing](./13_Menu_and_Pricing.md)                                           | Defines global menus, branch menus, pricing, and availability        |
| 14 | [Payments, Discounts and Refunds](./14_Payments_Discounts_and_Refunds.md)              | Defines payments, discounts, refunds, and related controls           |
| 15 | [Employees, Attendance and Payroll](./15_Employees_Attendance_and_Payroll.md)          | Defines employee lifecycle, attendance, salaries, and payroll        |
| 16 | [Reports and Dashboards](./16_Reports_and_Dashboards.md)                               | Defines dashboards, reports, exports, and report versioning          |
| 17 | [Notifications and Alerts](./17_Notifications_and_Alerts.md)                           | Defines system notifications and operational alerts                  |
| 18 | [Audit and Change History](./18_Audit_and_Change_History.md)                           | Defines auditability and historical change tracking                  |
| 19 | [Data Lifecycle and Deletion](./19_Data_Lifecycle_and_Deletion.md)                     | Defines data states, retention, expiration, and deletion             |
| 20 | [Business Rules](./20_Business_Rules.md)                                               | Consolidates the core enforceable business rules                     |

---

## 4. Requirement Dependency Flow

The documents should be interpreted in the following general dependency order:

```text
Product Overview
      ↓
Business Model
      ↓
Subscription and Tariffs
      ↓
Tenant and Branch Management
      ↓
Users, Roles and Permissions
      ↓
Authentication and Trusted Devices
      ↓
Offline Operation and Synchronization
      ↓
Operational Modules
      ├── POS and Orders
      ├── Cash Register
      ├── Shift Handover
      ├── Inventory
      ├── Products and Recipes
      ├── Menu and Pricing
      ├── Payments, Discounts and Refunds
      └── Employees, Attendance and Payroll
      ↓
Reports and Dashboards
      ↓
Notifications and Alerts
      ↓
Audit and Change History
      ↓
Data Lifecycle and Deletion
      ↓
Business Rules
```

This flow represents logical dependency, not implementation order.

---

## 5. Cross-Document Relationships

### 5.1 Subscription and Permissions

Subscription determines whether a business is entitled to use a feature or resource.

Permissions determine whether a specific user is authorized to perform an action.

Both conditions must be satisfied.

```text
Subscription Entitlement
        +
User Permission
        ↓
Effective Business Access
```

---

### 5.2 Business and Branch

A business is the primary tenant.

A branch is an operational unit belonging to exactly one business.

Branch-level data must remain associated with its business and must not become accessible across unrelated tenants.

---

### 5.3 POS, Cash and Payments

Orders, payments, cash sessions, and cashier responsibility are connected.

```text
Order
  ↓
Payment
  ↓
Cash Session
  ↓
Cashier Responsibility
  ↓
Cash Session Report
```

Card payments and cash payments may affect different financial calculations, but both remain part of the order and reporting history.

---

### 5.4 Orders, Recipes and Inventory

Order processing can cause inventory consumption through product recipes.

```text
Order
  ↓
Product
  ↓
Recipe
  ↓
Recipe Components
  ↓
Inventory Consumption
```

Nested recipes may create dependencies such as:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
      ↓
Customer Order
```

---

### 5.5 Cash Sessions and Handover

A shift handover does not create a new cash session.

```text
Cash Session
      │
      ├── Cashier A
      │
      ├── Handover
      │
      └── Cashier B
```

The same cash session remains active while responsibility changes.

---

### 5.6 Corrections and Audit

Corrections must preserve historical information.

```text
Original Value
      ↓
Correction
      ↓
New Value
      ↓
Audit History
```

The original value must remain available for historical analysis.

---

### 5.7 Reports and Change History

Reports are derived from operational data.

When relevant source data changes through an approved correction, the affected report may receive a new version.

Previous report versions remain immutable.

---

## 6. Core Business States

The system uses several important business states.

### Business / Subscription

```text
Active
  ↓
Expired
  ↓
Read-Only Retention
  ↓
Permanent Deletion
```

Reactivation during the retention period returns the business to active operation.

---

### Employees

```text
Active
  ↓
Deactivated
```

Deactivation preserves historical identity.

---

### Branches

```text
Active
  ↓
Deactivated / Archived
```

Historical branch data remains protected.

---

### Products

```text
Active
  ↓
Inactive / Archived
```

Products referenced by historical transactions must remain historically understandable.

---

### Recipes

```text
Draft / Changed
      ↓
Approval
      ↓
Active
      ↓
Archived
```

Approved historical recipes must remain traceable.

---

### Cash Sessions

```text
Not Opened
      ↓
Open
      ↓
Closed
```

A closed cash session does not return to the open state.

Corrections modify historical information without reopening the session.

---

### Reports

```text
Generated
    ↓
Versioned
    ↓
Updated Version
```

Previous versions remain immutable.

---

## 7. Business Rule Authority

`20_Business_Rules.md` is the consolidated reference for core enforceable business rules.

Individual module documents provide detailed context and workflows.

When a business rule is changed:

1. The relevant module document must be updated.
2. The corresponding rule in `20_Business_Rules.md` must be updated.
3. Related documents must be reviewed for consistency.
4. Architectural or technical consequences must be evaluated in later documentation stages.
5. The change must be recorded according to the project's documentation and ADR process.

---

## 8. Scope Boundary

The Business Analysis section intentionally does not define detailed technical implementation.

The following areas belong to later documentation stages:

* system architecture;
* service boundaries;
* domain model implementation;
* database schema;
* API contracts;
* frontend architecture;
* backend implementation;
* AI architecture;
* security implementation;
* deployment infrastructure;
* automated testing architecture;
* operational infrastructure.

Business requirements defined here must guide those later decisions.

---

## 9. Out-of-Scope Areas

The following areas are intentionally outside the current Business Analysis scope unless explicitly added later:

* online customer ordering;
* customer mobile applications;
* full CRM;
* loyalty programs;
* advanced promotion engines;
* supplier management;
* complex accounting;
* tax calculation engine;
* multi-currency accounting;
* government payroll integration;
* biometric attendance;
* GPS employee tracking;
* advanced procurement automation;
* automatic demand forecasting;
* AI-based recipe generation;
* customer-specific recipe profiles;
* advanced delivery-management systems;
* complex financial settlement integrations.

Being out of scope does not prevent future expansion.

---

## 10. Change Management

Business requirements are expected to evolve during development.

A requirement change should:

1. Identify the affected business area.
2. Identify dependent documents.
3. Update the relevant business analysis document.
4. Update the consolidated business rules when necessary.
5. Record architectural consequences separately when applicable.
6. Preserve historical decisions where required.
7. Avoid silently changing an already approved requirement.

Major architectural consequences should be documented through an ADR.

---

## 11. Traceability

Each significant business requirement should eventually be traceable through the documentation hierarchy:

```text
Business Requirement
        ↓
Business Rule
        ↓
System Requirement
        ↓
Domain Model
        ↓
Architecture Decision
        ↓
Implementation
        ↓
Test
```

This traceability allows the development team and coding agents to determine why a behavior exists and what requirement it satisfies.

---

## 12. Guidance for Coding Agents

Coding agents must treat this directory as the business-level source of truth.

Before implementing a feature, an agent should:

1. Identify the relevant Business Analysis document.
2. Check the corresponding business rules.
3. Check related documents for dependencies.
4. Avoid inventing missing business behavior.
5. Preserve tenant and branch isolation.
6. Preserve auditability and historical information.
7. Respect subscription and permission boundaries.
8. Respect offline behavior where applicable.
9. Escalate ambiguous requirements instead of silently choosing business behavior.
10. Record significant architectural consequences through the appropriate ADR.

Technical implementation must not contradict an approved business rule without an explicit documented change.

---

## 13. Completion Status

The core Business Analysis documentation set currently contains:

* Product definition;
* Business and SaaS model;
* Subscription and tariffs;
* Tenant and branch management;
* Users, roles, and permissions;
* Authentication and trusted devices;
* Offline operation and synchronization;
* POS and order management;
* Cash register and cash sessions;
* Shift handover;
* Inventory and warehouse;
* Products and recipes;
* Menu and pricing;
* Payments, discounts, and refunds;
* Employees, attendance, and payroll;
* Reports and dashboards;
* Notifications and alerts;
* Audit and change history;
* Data lifecycle and deletion;
* Consolidated business rules.

This completes the core Business Analysis documentation baseline.

---

## 14. Next Documentation Stage

The next major documentation stage is:

```text
02_System_Analysis
```

The System Analysis stage should translate the approved business requirements into system-level requirements, workflows, actors, use cases, system boundaries, functional requirements, non-functional requirements, and cross-module interactions.

Business Analysis should remain the reference point for determining **what the business needs**.

System Analysis will define **what the system must do to satisfy those needs**.

---

## Related Documents

* [`../README.md`](../README.md)
* [`../20_Business_Rules.md`](./20_Business_Rules.md)
* [`../../agents/AGENTS.md`](../../agents/AGENTS.md)
* [`../../adr/ADR-001-Documentation-First.md`](../../adr/ADR-001-Documentation-First.md)
* `../02_System_Analysis/`
* `../03_Domain_Analysis/`
* `../04_Architecture/`
* `../05_Database/`
* `../06_Backend/`
* `../07_Frontend/`
* `../08_AI/`
* `../09_API/`
* `../10_Deployment/`
* `../11_Security/`
* `../12_Testing/`
* `../13_Development/`
* `../14_Operations/`
* `../15_Future/`

