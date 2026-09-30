# Business Analysis Documentation

**Document ID:** BA-README
**Status:** Approved
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `agents/AGENTS.md`

---

## 1. Purpose

This directory contains the approved business analysis documentation for the FastFood ERP system.

The purpose of these documents is to define:

* what the system must support;
* how the business operates through the system;
* which business rules must be enforced;
* how businesses, branches, employees, subscriptions, and permissions interact;
* how orders, inventory, payments, cash sessions, payroll, and reports operate;
* how operational data is created, changed, corrected, preserved, reported, and eventually deleted;
* which requirements are intentionally outside the current business scope.

These documents represent the **business-level source of truth** before detailed system, domain, architecture, database, backend, frontend, security, deployment, and implementation decisions are made.

---

# 2. Business Analysis Principles

The Business Analysis documentation follows these principles:

1. Business requirements are defined before implementation details.
2. Business rules must be explicit and traceable.
3. Historical business information must not be silently overwritten.
4. Corrections must preserve the original historical state.
5. User permissions and subscription entitlements are separate control layers.
6. Business and branch data must remain isolated.
7. Offline operation must preserve the same core business rules as online operation.
8. Operational workflows must remain practical and fast for restaurant staff.
9. Security controls must not unnecessarily reduce POS performance.
10. Individual employee identity must be preserved for operational actions.
11. Important transactions must remain auditable.
12. Current configuration changes must not rewrite historical transactions.
13. Requirements that are not explicitly approved must not be treated as implemented requirements.
14. Technical implementation must not silently introduce new business behavior.
15. Business rules must remain consistent across UI, API, offline, synchronization, and background processing.

---

# 3. Document Structure

The Business Analysis documents are organized as follows:

| ID | Document                                                                               | Purpose                                                                       |
| -- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 01 | [Product Overview](./01_Product_Overview.md)                                           | Defines product purpose, scope, users, and major capabilities                 |
| 02 | [Business Model](./02_Business_Model.md)                                               | Defines the SaaS business and tenant model                                    |
| 03 | [Subscription and Tariffs](./03_Subscription_and_Tariffs.md)                           | Defines subscriptions, tariffs, limits, expiration, and reactivation          |
| 04 | [Tenant and Branch Management](./04_Tenant_and_Branch_Management.md)                   | Defines business and branch organization                                      |
| 05 | [Users, Roles and Permissions](./05_Users_Roles_and_Permissions.md)                    | Defines user identity, roles, permissions, overrides, and branch scope        |
| 06 | [Authentication and Trusted Devices](./06_Authentication_and_Trusted_Devices.md)       | Defines authentication and trusted-device rules                               |
| 07 | [Offline Operation and Synchronization](./07_Offline_Operation_and_Synchronization.md) | Defines offline operation and synchronization behavior                        |
| 08 | [POS and Order Management](./08_POS_and_Order_Management.md)                           | Defines order creation, editing, lifecycle, kitchen routing, and POS behavior |
| 09 | [Cash Register and Cash Sessions](./09_Cash_Register_and_Cash_Sessions.md)             | Defines cash register and cash-session lifecycle                              |
| 10 | [Shift Handover](./10_Shift_Handover.md)                                               | Defines cashier responsibility transfer and cash-session transition           |
| 11 | [Inventory and Warehouse](./11_Inventory_and_Warehouse.md)                             | Defines stock, warehouses, purchasing, consumption, and inventory rules       |
| 12 | [Products and Recipes](./12_Products_and_Recipes.md)                                   | Defines products, recipes, preparation, dependencies, and recipe lifecycle    |
| 13 | [Menu and Pricing](./13_Menu_and_Pricing.md)                                           | Defines global menus, branch menus, pricing, Sets, and availability           |
| 14 | [Payments, Discounts and Refunds](./14_Payments_Discounts_and_Refunds.md)              | Defines payments, discounts, refunds, debt, and financial controls            |
| 15 | [Employees, Attendance and Payroll](./15_Employees_Attendance_and_Payroll.md)          | Defines employee lifecycle, attendance, salary configuration, and payroll     |
| 16 | [Reports and Dashboards](./16_Reports_and_Dashboards.md)                               | Defines dashboards, reports, exports, and report versioning                   |
| 17 | [Notifications and Alerts](./17_Notifications_and_Alerts.md)                           | Defines system notifications and operational alerts                           |
| 18 | [Audit and Change History](./18_Audit_and_Change_History.md)                           | Defines auditability and historical change tracking                           |
| 19 | [Data Lifecycle and Deletion](./19_Data_Lifecycle_and_Deletion.md)                     | Defines data states, retention, expiration, and permanent deletion            |
| 20 | [Business Rules](./20_Business_Rules.md)                                               | Consolidates the core enforceable business rules                              |

---

# 4. Requirement Dependency Flow

The documents should be interpreted in the following logical dependency order:

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

This represents **logical business dependency**, not implementation order.

---

# 5. Cross-Document Relationships

## 5.1 Subscription and Permissions

Subscription entitlement and employee authorization are separate control layers.

```text
Subscription Entitlement
        +
Employee Permission
        ↓
Effective Business Access
```

A user cannot perform an operation when either the subscription or the employee's authorization does not permit it.

---

## 5.2 Business and Branch

A business is the primary tenant.

A branch is an operational unit belonging to exactly one business.

Branch-level data remains associated with both its business and branch context.

An employee may have access to multiple branches, but branch access does not automatically imply identical permissions in every branch.

---

## 5.3 POS, Cash Sessions and Payments

Orders, payments, cash sessions, registers, devices, and employee responsibility are connected.

```text
Order
  ↓
Payment
  ↓
Cash Session
  ↓
Cashier / Employee
  ↓
Cash Session Reporting
```

Cash and non-cash payment methods may affect different financial calculations, but all payment activity remains part of the historical order and financial record.

---

## 5.4 Cash Register and Shift Handover

The physical cash register and cash session are separate concepts.

A cashier handover **closes the previous cash session and creates a new cash session**.

```text
Physical Cash Register
        │
        ├── Cash Session A
        │      └── Previous Cashier
        │
        └── Cash Session B
               └── New Cashier
```

The physical register remains the same.

The Cash Session UUID changes.

The previous cashier's actions remain associated with the previous session.

The new cashier's actions are associated with the new session.

---

## 5.5 Orders, Recipes and Inventory

Order processing can cause inventory consumption through product recipes.

```text
Order
  ↓
Product / Set
  ↓
Recipe / Components
  ↓
Inventory Consumption
```

Nested dependencies may create:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
      ↓
Customer Order
```

Inventory deduction occurs when the applicable order reaches the Accepted state.

---

## 5.6 Menu, Pricing and Historical Transactions

Current menu and pricing configuration controls new transactions.

Historical transactions retain the values applicable at the time they occurred.

```text
Current Configuration
        ↓
New Transaction

Historical Transaction
        ↓
Historical Snapshot
```

Later product, price, recipe, or configuration changes must not rewrite historical transaction values.

---

## 5.7 Corrections and Audit

Corrections preserve the original historical state.

```text
Original State
      ↓
Correction
      ↓
New State
      ↓
Audit History
```

The original state remains available for historical analysis.

---

## 5.8 Reports and Source Data

Reports are derived from business data.

When relevant source data changes through an approved correction, the affected report may receive a new version.

```text
Business Data
      ↓
Report Version
      ↓
Relevant Correction
      ↓
New Report Version
```

Previous report versions remain immutable.

A correction that does not change report-relevant results does not require a new report version.

---

## 5.9 Offline and Server Authority

Offline operations are supported only within authorized boundaries.

```text
Trusted Device
      ↓
Offline Operation
      ↓
Local Business Rules
      ↓
Synchronization
      ↓
Server Validation
      ↓
Authoritative Business State
```

Offline mode must not bypass:

* subscription restrictions;
* employee permissions;
* branch scope;
* inventory rules;
* cash-session rules;
* audit requirements.

---

# 6. Core Business States

The system uses several important business states.

## 6.1 Business Subscription Lifecycle

```text
Active
  ↓
Expired
  ↓
Read-Only Retention
  ↓
Permanent Deletion Eligibility
  ↓
Permanent Deletion
```

If the business is reactivated during the 60-day retention period, it returns to active operation according to the new subscription.

---

## 6.2 Employees

```text
Created
  ↓
Active
  ↓
Inactive
```

Deactivation preserves historical identity and activity.

---

## 6.3 Branches

```text
Active
  ↓
Inactive / Archived
```

Historical branch data remains protected.

---

## 6.4 Products

```text
Active
  ↓
Inactive / Archived
```

Products referenced by historical transactions remain historically understandable.

---

## 6.5 Recipes

```text
Draft / Changed
      ↓
Approval
      ↓
Active
      ↓
Archived
```

Previous approved recipe versions remain historically traceable.

---

## 6.6 Orders

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

Payment is a separate financial operation.

---

## 6.7 Cash Sessions

```text
Not Opened
      ↓
Open
      ↓
Closed
```

A closed cash session does not return to the Open state.

Corrections are separate operations against the historical session.

A cashier handover closes the previous session and creates a new session.

---

## 6.8 Payments

Payments are financial records associated with an order.

Supported methods include:

```text
Cash
Card
Debt
Mixed
```

Completed payment history is preserved and is not silently overwritten.

---

## 6.9 Refunds

Refunds are separate financial operations.

```text
Original Payment
      ↓
Refund
```

A refund does not rewrite the original payment.

---

## 6.10 Reports

```text
Generated
    ↓
Versioned
    ↓
New Version When Relevant Data Changes
```

Previous versions remain immutable.

---

# 7. Business Rule Authority

`20_Business_Rules.md` is the consolidated reference for the core enforceable business rules.

Individual module documents provide more detailed business context and workflows.

When a business rule changes:

1. The relevant module document must be updated.
2. The corresponding rule in `20_Business_Rules.md` must be updated.
3. Related documents must be reviewed for consistency.
4. Dependencies and cross-module effects must be identified.
5. Architectural or technical consequences must be evaluated during later documentation stages.
6. The change must be recorded according to the project's documentation and ADR process where applicable.

A module document must not silently contradict an approved consolidated business rule.

---

# 8. Business Analysis Scope Boundary

The Business Analysis section defines **what the business requires**.

It intentionally does not define detailed technical implementation.

The following areas belong to later documentation stages:

* system architecture;
* service boundaries;
* domain implementation;
* database schema;
* API contracts;
* frontend architecture;
* backend implementation;
* AI architecture;
* security implementation;
* deployment infrastructure;
* automated testing architecture;
* operational infrastructure;
* infrastructure topology;
* exact synchronization mechanisms.

Business requirements defined here must guide those later decisions.

---

# 9. Current Business Scope

The current Business Analysis scope includes:

* multi-tenant SaaS business management;
* branch management;
* employee and role management;
* permission and branch-scope management;
* authentication and trusted devices;
* offline-first branch operation;
* synchronization;
* POS and order management;
* Hall/Dine-in and Takeaway orders;
* cash registers and cash sessions;
* cashier handover;
* inventory and warehouses;
* raw, semi-finished, and finished products;
* recipes and nested recipe dependencies;
* global and branch menus;
* branch pricing overrides;
* Sets;
* payments;
* debt;
* mixed payments;
* discounts;
* refunds;
* employee attendance;
* payroll;
* expenses;
* reports;
* dashboards;
* notifications;
* audit history;
* data lifecycle;
* subscription lifecycle;
* historical data preservation.

---

# 10. Current Business Boundaries

The following capabilities are intentionally outside the current primary business scope unless explicitly added later:

* online customer ordering;
* customer mobile applications;
* full customer CRM;
* loyalty programs;
* advanced promotion engines;
* customer-specific pricing;
* dynamic pricing;
* competitor price matching;
* complex price books;
* multi-currency;
* tax calculation engine;
* complex accounting;
* automated government accounting/reporting;
* advanced procurement automation;
* inter-branch inventory transfer;
* advanced delivery management;
* Telegram bot;
* WhatsApp/SMS customer workflows;
* external payment automation;
* automatic physical refund processing;
* biometric attendance;
* GPS employee tracking;
* AI-based demand forecasting;
* AI-based recipe generation;
* AI-based pricing recommendations;
* customer-specific recipe profiles;
* advanced financial settlement integrations;
* BI platforms and external analytics;
* arbitrary report builders;
* arbitrary SQL reporting;
* predictive analytics.

Being outside the current scope does not prevent future expansion.

---

# 11. Change Management

Business requirements are expected to evolve during development.

A requirement change should:

1. Identify the affected business area.
2. Identify the current approved behavior.
3. Identify the new proposed behavior.
4. Identify dependent documents.
5. Update the relevant Business Analysis document.
6. Update `20_Business_Rules.md` when the change affects a consolidated rule.
7. Review related documents for contradictions.
8. Preserve historical decisions where required.
9. Evaluate architectural and technical consequences.
10. Record significant architectural consequences through an ADR.

An approved requirement must not be silently changed by implementation.

---

# 12. Traceability

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

This traceability allows developers and coding agents to determine:

* why a behavior exists;
* which business requirement it satisfies;
* which rule governs it;
* which system behavior implements it;
* how it should be tested.

---

# 13. Guidance for Coding Agents

Coding agents must treat this directory as the business-level source of truth.

Before implementing a feature, an agent should:

1. Identify the relevant Business Analysis document.
2. Check the corresponding business rules.
3. Check related documents for dependencies.
4. Verify subscription requirements.
5. Verify employee permission and branch scope.
6. Check whether the operation must work offline.
7. Check historical-data requirements.
8. Check audit requirements.
9. Avoid inventing missing business behavior.
10. Preserve tenant and branch isolation.
11. Preserve transaction and historical integrity.
12. Escalate ambiguous business requirements instead of silently choosing business behavior.
13. Record significant architectural consequences through the appropriate ADR.

Technical implementation must not contradict an approved business rule without an explicit documented requirement change.

---

# 14. Documentation Consistency Rules

The Business Analysis documents must remain internally consistent.

When a requirement appears in multiple documents:

* the same business meaning must be preserved;
* terminology must remain consistent;
* lifecycle states must not contradict one another;
* historical behavior must remain consistent;
* cross-module dependencies must remain consistent.

Particular attention must be paid to shared concepts such as:

* Business;
* Branch;
* Employee;
* Role;
* Permission;
* Subscription;
* Device;
* Cash Register;
* Cash Session;
* Order;
* Payment;
* Inventory;
* Product;
* Recipe;
* Set;
* Report;
* Audit Event.

---

# 15. Important Cross-Module Invariants

The following invariants are fundamental to the current business model.

## 15.1 Tenant Invariant

A business-scoped record must never become accessible to another unrelated business.

---

## 15.2 Permission Invariant

Permission cannot override subscription restrictions.

Subscription entitlement cannot replace employee authorization.

---

## 15.3 Historical Invariant

Historical transactions must preserve the business values that applied when the transaction occurred.

---

## 15.4 Correction Invariant

A correction must preserve the original historical state.

---

## 15.5 Offline Invariant

Offline operation must not provide broader business authority than online operation.

---

## 15.6 Inventory Invariant

Inventory cannot become negative.

---

## 15.7 Cash Session Invariant

A closed cash session cannot become an active session again.

Corrections operate against the historical session.

---

## 15.8 Handover Invariant

A cashier handover closes the previous cash session and creates a new cash session.

The physical register remains the same, but the Cash Session UUID changes.

---

## 15.9 Payment Invariant

A completed payment cannot be silently duplicated or overwritten.

---

## 15.10 Report Invariant

Previous report versions remain immutable.

---

## 15.11 Audit Invariant

Important historical actions cannot disappear through normal correction or editing workflows.

---

## 15.12 Deletion Invariant

Permanent deletion must affect only the target business and must not expose or delete unrelated tenant data.

---

# 16. Completion Status

The core Business Analysis documentation baseline contains:

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

The Business Analysis documentation establishes the approved business baseline for the next documentation stages.

---

# 17. Next Documentation Stage

The next major documentation stage is:

```text
02_System_Analysis
```

The System Analysis stage will translate approved business requirements into system-level requirements, including:

* actors;
* system boundaries;
* use cases;
* functional requirements;
* non-functional requirements;
* system workflows;
* state transitions;
* cross-module interactions;
* system-level constraints;
* external system boundaries.

Business Analysis remains the reference for determining:

> **What the business needs.**

System Analysis will define:

> **What the system must do to satisfy those needs.**

---

# 18. Related Documents

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

