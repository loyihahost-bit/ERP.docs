# 01 — Business Analysis

## Metadata

* **Document Type:** Business Analysis
* **Status:** Accepted
* **Version:** 1.0
* **Scope:** FastFood ERP
* **Purpose:** Define the approved business requirements, business rules, workflows, roles, permissions, and operational behavior of the FastFood ERP system.
* **Source:** Business requirements interview and approved decisions
* **Last Updated:** 2026-09-18

---

## 1. Purpose

This directory contains the business analysis of the FastFood ERP system.

It defines what the system must do from a business perspective, how users and branches operate, what rules must be enforced, and how important business processes should behave.

This directory is the primary business reference for later architecture, database, API, UI/UX, security, testing, and implementation documentation.

Technical implementation details should not be introduced here unless they are required to explain an approved business rule.

---

## 2. Business Analysis Principles

The following principles apply throughout this directory:

1. Approved business decisions must be treated as authoritative.
2. Business rules must be explicit and unambiguous.
3. Historical business data must not be silently overwritten.
4. Important changes must remain traceable.
5. Permissions must control access to business operations.
6. Branch-level scope must be respected where applicable.
7. Offline operation is a supported business requirement.
8. The system should remain simple for daily restaurant operations despite having advanced capabilities.
9. Reports must be understandable and must not mix unrelated information.
10. Business processes must not depend on unnecessary manual intervention.

---

## 3. Document Map

### 01 — Product Overview

Defines the overall purpose, scope, target users, and major capabilities of the ERP.

**File:** `01_Product_Overview.md`

### 02 — Business Model

Defines the SaaS business model, restaurant/business structure, ownership model, and platform-level relationships.

**File:** `02_Business_Model.md`

### 03 — Subscription and Tariffs

Defines subscriptions, tariffs, limits, expiration behavior, notifications, and post-expiration data lifecycle.

**File:** `03_Subscription_and_Tariffs.md`

### 04 — Tenant and Branch Management

Defines restaurant/business networks, branches, branch separation, branch configuration, and branch-level operation.

**File:** `04_Tenant_and_Branch_Management.md`

### 05 — Users, Roles and Permissions

Defines Super Admin, Owner, employees, role templates, employee overrides, permission inheritance, branch scope, permission changes, and privilege protection.

**File:** `05_Users_Roles_and_Permissions.md`

### 06 — Authentication and Trusted Devices

Defines user authentication, trusted devices, new-device verification, device revocation, and the business requirements surrounding secure device access.

**File:** `06_Authentication_and_Trusted_Devices.md`

### 07 — Offline Operation and Synchronization

Defines branch offline operation, offline authorization, synchronization behavior, device trust requirements, and operational limitations while disconnected.

**File:** `07_Offline_Operation_and_Synchronization.md`

### 08 — POS and Order Management

Defines order creation, dine-in, takeaway, phone delivery, order numbering, order editing, open orders, customization, extras, combos, and cashier workflows.

**File:** `08_POS_and_Order_Management.md`

### 09 — Cash Register and Cash Sessions

Defines the branch cash register, Cash Sessions, opening, closing, expected/actual cash, payment types, discrepancies, and cash-session correction behavior.

**File:** `09_Cash_Register_and_Cash_Sessions.md`

### 10 — Shift Handover

Defines cashier handover, acceptance of physical cash, open-order transfer, confirmation/recalculation, discrepancy handling, and responsibility transfer.

**File:** `10_Shift_Handover.md`

### 11 — Inventory and Warehouse

Defines warehouses, stock entries, purchases, stock calculations, FIFO, stock counts, shortages, shrinkage, shopping lists, and inventory restrictions.

**File:** `11_Inventory_and_Warehouse.md`

### 12 — Products and Recipes

Defines finished products, semi-finished products, recipes, recipe dependencies, recipe approval, archiving, restricted recipe visibility, and recipe changes.

**File:** `12_Products_and_Recipes.md`

### 13 — Menu and Pricing

Defines the global menu, branch menu availability, pricing, branch price overrides, product codes, item availability, and menu configuration.

**File:** `13_Menu_and_Pricing.md`

### 14 — Payments, Discounts and Refunds

Defines payment handling, discounts, refunds, refund permissions, approval, mandatory reasons, and related business rules.

**File:** `14_Payments_Discounts_and_Refunds.md`

### 15 — Employees, Attendance and Payroll

Defines employee management, attendance rules, salary models, daily payments, bonuses, and payroll permissions.

**File:** `15_Employees_Attendance_and_Payroll.md`

### 16 — Reports and Dashboards

Defines dashboards, daily reports, monthly reports, report periods, automatic and manual generation, Excel export, report versions, report history, and report access.

**File:** `16_Reports_and_Dashboards.md`

### 17 — Notifications and Alerts

Defines operational notifications and alerts, including subscription, inventory, payroll, refund, discrepancy, correction, and report notifications.

**File:** `17_Notifications_and_Alerts.md`

### 18 — Audit and Change History

Defines audit requirements, change history, historical values, correction history, permission history, and traceability.

**File:** `18_Audit_and_Change_History.md`

### 19 — Data Lifecycle and Deletion

Defines subscription expiration, restricted access, data retention, the 60-day expiration period, and permanent deletion rules.

**File:** `19_Data_Lifecycle_and_Deletion.md`

### 20 — Business Rules

Contains cross-cutting business rules that affect multiple areas of the system.

This document should act as a concise reference and index rather than duplicating all detailed requirements from the other documents.

**File:** `20_Business_Rules.md`

---

## 4. Requirement Ownership

Each business requirement should have one primary document where its detailed definition is maintained.

Related documents may reference the requirement, but the same rule should not be independently redefined in multiple places.

When a rule affects multiple domains, the primary rule belongs to the domain where the business responsibility originates, while cross-document references should point back to it.

---

## 5. Relationship With Other Documentation

This Business Analysis directory defines **what the business requires**.

Later documentation should translate these requirements into:

* system architecture;
* domain boundaries;
* database models;
* API contracts;
* security architecture;
* synchronization mechanisms;
* UI/UX behavior;
* testing requirements;
* operational procedures.

Technical documents must not silently change an approved business requirement.

If implementation limitations require a business change, the business requirement must first be reviewed and explicitly changed.

---

## 6. Change Management

Approved business requirements should not be silently rewritten.

If a previously approved business decision changes:

1. The affected requirement is identified.
2. The reason for change is documented.
3. Related documents are identified.
4. The affected requirement is updated through the project's documented change process.
5. Related ADRs are created or superseded where the change represents an architectural decision.

Historical decisions remain traceable.

---

## Related Documents

* `../../agents/AGENTS.md`
* `../../adr/ADR-001-Documentation-First.md`
* `../README.md`
* `../02_Architecture/`
* `../03_Domain_Model/`
* `../04_Database/`
* `../05_API/`
* `../06_Security/`
* `../07_UI_UX/`
* `../08_Offline_Sync/`
* `../09_Testing/`
* `../10_Operations/`
* `../11_Reports/`
* `../12_Deployment/`
* `../13_Integrations/`
* `../14_Compliance/`
* `../15_Future/`

