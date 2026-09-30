# Data Lifecycle and Deletion

**Document ID:** FF-BA-019
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for the lifecycle, retention, archival, deactivation, expiration, and permanent deletion of FastFood ERP business data.

The lifecycle must protect historical business information while ensuring that expired businesses are eventually removed when the defined retention period ends.

---

## 2. Data Lifecycle Principles

The system follows these principles:

1. Data must have a defined lifecycle.
2. Historical business information must not be silently destroyed.
3. Normal user actions must not permanently delete important historical records.
4. Deactivation and archival must be preferred where historical information is required.
5. Subscription expiration must not immediately destroy business data.
6. Expired businesses receive a defined read-only period.
7. Permanent deletion occurs only after the defined retention period.
8. Deletion must cover the business's related data consistently.
9. The lifecycle must respect business and tenant isolation.
10. Lifecycle processing must remain auditable.

---

## 3. Business Data Ownership

A business owns its ERP data within the platform.

Business data may include:

* business information;
* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* inventory;
* orders;
* payments;
* cash sessions;
* reports;
* payroll;
* expenses;
* notifications;
* audit history;
* related configuration.

The exact technical storage model is defined later in Database and Architecture documentation.

---

## 4. Data Lifecycle States

Business data may pass through several logical states:

```text
Active
  ↓
Deactivated / Archived
  ↓
Subscription Expired
  ↓
Read-Only Retention
  ↓
Permanent Deletion
```

Not every individual record must pass through every state.

For example, an employee may be deactivated while the business itself remains active.

---

## 5. Active Business

An active business has an active subscription and can use the functions permitted by:

* subscription tariff;
* employee permissions;
* branch scope;
* other applicable business rules.

Active business data can be created and modified where the user has permission.

---

## 6. Deactivation

Deactivation prevents an entity from being actively used while preserving its historical information.

Examples include:

* employee deactivation;
* branch deactivation;
* product deactivation;
* menu item deactivation;
* role deactivation where supported.

Deactivation does not mean permanent deletion.

---

## 7. Employee Deactivation

Employees should be deactivated rather than deleted when they have historical business activity.

A deactivated employee:

* cannot perform new authorized operations;
* remains identifiable in historical records;
* remains associated with previous orders, cash sessions, inventory actions, payroll, and audit history where applicable.

Historical identity must remain intact.

---

## 8. Branch Deactivation

A branch with historical data should normally be deactivated or archived rather than permanently deleted.

Historical branch data remains associated with the branch.

A deactivated branch should not accept normal new business operations.

Authorized users may continue to view historical branch information according to permissions and subscription state.

---

## 9. Product and Menu Lifecycle

Products and menu items may become inactive.

An inactive product:

* is not available for new normal order selection;
* remains available in historical transactions;
* retains relevant historical pricing and recipe context.

A product with a recipe cannot be permanently deleted through normal business operations.

It must be archived when no longer actively used.

---

## 10. Recipe Lifecycle

Recipes have their own historical lifecycle.

When a recipe changes:

* the previous recipe version remains historical;
* the new recipe version becomes active after required approval;
* historical transactions continue to reference the appropriate historical state.

Old recipes are archived rather than silently replaced.

---

## 11. Cash Session Lifecycle

A cash session has a controlled lifecycle.

Typical states include:

```text
Open
  ↓
Closed
  ↓
Corrected where permitted
```

A closed cash session must remain closed.

Correction does not reopen the cash session.

It creates a controlled historical correction.

---

## 12. Cash Session Corrections

Corrections preserve:

* original values;
* corrected values;
* correction reason;
* responsible employee;
* timestamp;
* correction history.

The original cash-session information must remain available.

The system must not transform a corrected session into a record that appears as though the original result never existed.

---

## 13. Report Lifecycle

Reports have their own lifecycle.

A report may be:

* generated;
* current;
* superseded by a newer version;
* historical.

Previous report versions remain immutable.

A new version is created when relevant underlying business data changes.

Reports must not be deleted through normal user operations.

---

## 14. Audit Data Lifecycle

Audit records remain available throughout the business data lifecycle.

During the active and read-only periods, authorized users may access audit history according to permissions.

Audit records cannot be selectively deleted through the normal business interface.

When the business is permanently deleted, its audit history is also removed according to the permanent deletion process.

---

## 15. Subscription Expiration

Subscription expiration does not immediately delete business data.

When the subscription expires, the business enters the defined expired/read-only state.

The business retains its data during the retention period.

---

## 16. Expired Read-Only State

After subscription expiration:

* users may log in according to the applicable access rules;
* historical data remains viewable;
* modifying functions are blocked;
* relevant lists and sections can be exported to Excel;
* normal new business operations are unavailable.

The exact access is still subject to employee permissions.

---

## 17. Read-Only Retention Period

The expired business receives a **60-day retention/reactivation period**.

During this period, the business data remains available.

The purpose of this period is to allow the business to reactivate its subscription without losing historical information.

---

## 18. Reactivation

If the business reactivates its subscription within the 60-day period:

```text
Expired
   ↓
Subscription Reactivated
   ↓
Active
```

Existing business data remains available.

The system must not require the business to recreate:

* branches;
* employees;
* products;
* recipes;
* orders;
* inventory;
* reports;
* historical records.

Normal access resumes according to the renewed subscription and permissions.

---

## 19. Tariff Upgrade

A tariff upgrade does not require destructive data changes.

If the new tariff allows additional:

* branches;
* Owners;
* employees;
* functions;

the newly available capacity becomes usable according to the subscription rules.

Existing data remains unchanged.

---

## 20. Tariff Downgrade

A tariff downgrade must not automatically delete existing data.

If existing resources exceed the new tariff limit:

* existing historical data remains;
* creation of additional resources may be blocked;
* users may need to reduce active resources before creating new ones;
* the system must not silently delete data to satisfy the lower limit.

---

## 21. Permanent Deletion

If the business does not reactivate within the 60-day retention period, the business data becomes eligible for permanent deletion.

Permanent deletion means the business's stored application data is removed according to the defined deletion process.

The deleted data cannot be restored through normal business operations.

---

## 22. Deletion Deadline

The deletion process must be based on the subscription expiration date and the defined 60-day retention period.

The system must preserve sufficient lifecycle information to determine when permanent deletion becomes eligible.

The deletion process must not depend solely on a user's local device time.

---

## 23. Deletion Warning

The system must notify authorized users before permanent deletion.

Warnings should clearly communicate:

* subscription expiration;
* remaining retention period;
* permanent deletion consequence;
* available reactivation action.

The purpose is to prevent unexpected loss of business data.

---

## 24. Deletion Eligibility

A business becomes eligible for permanent deletion only when:

1. its subscription has expired;
2. the defined 60-day retention period has ended;
3. the subscription has not been reactivated.

A business that reactivates before the deadline must not be permanently deleted.

---

## 25. Deletion Scope

Permanent deletion applies to the business's related data, including where applicable:

* business configuration;
* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* inventory;
* orders;
* payments;
* cash sessions;
* handovers;
* refunds;
* discounts;
* payroll;
* expenses;
* reports;
* report versions;
* notifications;
* audit history;
* synchronization records;
* other business-owned application data.

The exact technical deletion order is defined later in Database and Architecture documentation.

---

## 26. Tenant Isolation During Deletion

Permanent deletion must affect only the target business.

Deletion must not affect:

* another business;
* another branch belonging to another business;
* platform-level tariff definitions;
* platform configuration;
* unrelated system records.

Tenant isolation must be enforced throughout the deletion process.

---

## 27. Cross-Reference Handling

Business records may reference other business records.

Permanent deletion must handle these relationships consistently.

For example:

```text
Business
   ├── Branch
   │    ├── Orders
   │    ├── Inventory
   │    └── Cash Sessions
   └── Employees
        └── Audit History
```

The final technical implementation must ensure that deletion does not leave inconsistent business-owned data.

---

## 28. Historical Data Protection

During the active and read-only lifecycle, historical data must remain protected.

Examples include:

* completed orders;
* closed cash sessions;
* previous recipes;
* previous prices;
* payroll history;
* inventory history;
* correction history;
* audit history;
* report versions.

Historical records must not be silently removed simply because they are old.

---

## 29. Normal User Deletion

Normal users must not have unrestricted permanent deletion capabilities.

Where historical information is important, the system should use:

* deactivation;
* archive;
* correction;
* cancellation;
* controlled lifecycle transitions.

Permanent business deletion is a lifecycle operation, not an ordinary user action.

---

## 30. Order Deletion

Completed or historical orders should not be permanently deleted through normal user operations.

Where an order must no longer be treated as active, the appropriate business state should be used, such as cancellation or another defined status.

The historical order identity remains available.

---

## 31. Payment and Refund Data

Payment and refund history must remain associated with the relevant order during the active and retention lifecycle.

A refund does not delete the original payment history.

The system must preserve the relationship between:

* original payment;
* refund;
* reason;
* responsible employee;
* relevant order.

---

## 32. Inventory Data

Inventory history must remain available during the business lifecycle.

Historical:

* purchases;
* stock counts;
* adjustments;
* variances;
* prepared quantities;
* inventory deductions;

must not be silently removed.

After permanent business deletion, business-owned inventory history is deleted as part of the business deletion process.

---

## 33. Employee and Payroll Data

Employee and payroll history remains available during the business lifecycle.

Deactivating an employee does not remove:

* salary history;
* payroll history;
* attendance history;
* order history;
* cash history;
* inventory actions;
* audit history.

These records remain attributable to the original employee.

---

## 34. Offline Data During Expiration

A device that was previously trusted must not use offline access to bypass an expired subscription.

Subscription restrictions remain authoritative.

Offline authorization must therefore respect the subscription state when the device reconnects.

The system must not use offline operation to extend the business's subscription beyond its allowed lifecycle.

---

## 35. Offline Data During Deletion

After permanent business deletion, devices belonging to that business must no longer be able to synchronize business data with the deleted business.

Any remaining local business data must not be treated as an independent active copy of the business.

The final technical handling of residual local data is defined in Security and Offline Synchronization documentation.

---

## 36. Backup and Deletion

Permanent deletion must also consider system-managed copies of business data.

The technical implementation must define how deletion applies to:

* primary database;
* stored reports;
* files;
* backups;
* replicas;
* caches;
* temporary processing data.

The business requirement is that permanent deletion must not leave an indefinitely accessible active business copy through normal platform operations.

---

## 37. Deletion Audit

The system must preserve sufficient platform-level information to demonstrate that a permanent deletion process occurred.

The deletion record may include:

* business identity;
* deletion eligibility date;
* deletion execution time;
* deletion status;
* system process;
* result;
* failure information where applicable.

Business-level audit history is deleted with the business data according to the lifecycle rules.

---

## 38. Deletion Failure

If permanent deletion fails partially or completely, the system must not report successful deletion until the required deletion process has completed successfully.

The system should:

* record the failure;
* retry where appropriate;
* prevent inconsistent lifecycle state;
* notify authorized platform personnel when intervention is required.

Deletion processing must be designed to avoid partial business states.

---

## 39. Data Export Before Deletion

During the expired read-only period, users may export relevant lists and sections to Excel.

The export capability exists to allow the business to retrieve useful information before permanent deletion.

The system does not provide an additional user-accessible archive period after the 60-day retention period.

---

## 40. No Additional Archive Period

Once the 60-day retention period ends without reactivation, the business proceeds to permanent deletion.

There is no additional user-accessible archive period after the defined deadline.

The business must reactivate within the allowed period to retain its platform data.

---

## 41. Lifecycle Notifications

The lifecycle may generate notifications for:

* upcoming subscription expiration;
* subscription expiration;
* read-only state;
* approaching deletion deadline;
* successful reactivation;
* deletion eligibility;
* permanent deletion completion or failure where applicable.

Notifications must respect the business's access and permission rules.

---

## 42. Data Lifecycle and Permissions

Data lifecycle state and employee permissions are separate controls.

For example:

```text
Subscription Active
+
Permission Granted
=
Operation Allowed
```

If the subscription is expired:

```text
Subscription Expired
+
Permission Granted
=
Read-Only Restrictions Still Apply
```

An employee's permission cannot override the subscription lifecycle.

---

## 43. Data Lifecycle and Trusted Devices

A trusted device provides authorized offline access within its valid scope.

It does not provide:

* permanent data ownership;
* subscription extension;
* deletion protection;
* permission escalation.

Lifecycle restrictions remain authoritative.

---

## 44. Data Lifecycle and Reporting

Reports and report versions remain available during the active and read-only lifecycle according to permissions.

After permanent deletion, business-owned reports and report versions are removed as part of the business data deletion process.

---

## 45. Data Lifecycle and Audit

Audit records remain available during the active and read-only lifecycle.

They are protected from normal user deletion.

When permanent business deletion occurs, the business's audit history is deleted with the business data according to the deletion process.

---

## 46. Data Lifecycle and Performance

Lifecycle processing must not significantly affect normal restaurant operations.

Tasks such as:

* expiration processing;
* deletion eligibility checks;
* report cleanup;
* large-scale deletion;

should be handled without blocking normal POS operations.

---

## 47. Lifecycle State Summary

| State                | Data      | Modification           | Export                | Reactivation             |
| -------------------- | --------- | ---------------------- | --------------------- | ------------------------ |
| Active               | Available | Allowed by permissions | Allowed               | Not applicable           |
| Deactivated Entity   | Preserved | Restricted             | Allowed by permission | Entity-specific          |
| Subscription Expired | Preserved | Blocked                | Allowed               | Available                |
| Read-Only Retention  | Preserved | Blocked                | Allowed               | Available within 60 days |
| Permanent Deletion   | Removed   | Not available          | Not available         | Not available            |

---

## 48. Business Rules Summary

| Area                      | Rule                                                        |
| ------------------------- | ----------------------------------------------------------- |
| Active business           | Normal operations according to subscription and permissions |
| Deactivation              | Preserves historical data                                   |
| Employee deletion         | Use deactivation when historical activity exists            |
| Branch deletion           | Deactivate/archive when historical data exists              |
| Product with recipe       | Archive instead of normal deletion                          |
| Closed cash session       | Remains closed                                              |
| Cash correction           | Preserves original result                                   |
| Report versions           | Previous versions remain immutable                          |
| Subscription expiration   | Does not immediately delete data                            |
| Expired state             | Read-only                                                   |
| Retention                 | 60 days                                                     |
| Reactivation              | Restores active operation and existing data                 |
| Tariff downgrade          | Must not destructively delete data                          |
| Permanent deletion        | Occurs after 60 days without reactivation                   |
| Deletion warning          | Required before permanent deletion                          |
| Normal user deletion      | Must not provide unrestricted permanent deletion            |
| Export before deletion    | Relevant Excel export remains available                     |
| Additional archive period | Not provided                                                |
| Tenant isolation          | Required during all lifecycle operations                    |
| Audit                     | Lifecycle actions must remain traceable                     |
| Trusted device            | Cannot bypass lifecycle restrictions                        |

---

## 49. Business Boundaries

The current Data Lifecycle and Deletion scope does **not** define:

* exact database cascade rules;
* physical storage deletion algorithms;
* backup retention periods;
* cloud provider deletion mechanisms;
* cryptographic erasure;
* legal retention requirements;
* jurisdiction-specific regulatory retention;
* disaster-recovery retention;
* forensic recovery procedures;
* external data export services.

These topics must be defined later in Architecture, Database, Security, Deployment, and Operations documentation where required.

---

## 50. Related Documents

* `01_Product_Overview.md`
* `02_Business_Model.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

