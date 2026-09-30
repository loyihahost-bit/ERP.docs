# Data Lifecycle and Deletion

**Document ID:** FF-BA-019
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for the lifecycle, retention, archival, deactivation, subscription expiration, read-only operation, and permanent deletion of FastFood ERP business data.

The lifecycle must protect historical business information while ensuring that businesses that remain inactive beyond the defined retention period are eventually removed.

The lifecycle must preserve historical integrity during normal business operation, subscription expiration, corrections, archival, and deletion.

---

## 2. Data Lifecycle Principles

The system follows these principles:

1. Business data must have a defined lifecycle.
2. Historical business information must not be silently destroyed.
3. Normal user actions must not permanently delete important historical records.
4. Deactivation and archival are preferred where historical information is required.
5. Subscription expiration must not immediately destroy business data.
6. An expired business enters a restricted/read-only state.
7. The retention period after subscription expiration is 60 days.
8. A business that reactivates within the retention period keeps its existing data.
9. Permanent deletion occurs after the 60-day period if the subscription has not been reactivated.
10. Permanent deletion must apply consistently to business-owned data.
11. Tenant isolation must be enforced throughout the lifecycle.
12. Lifecycle operations must remain auditable.
13. Offline access and trusted devices must not bypass lifecycle restrictions.

---

## 3. Business Data Ownership

A business owns its ERP application data within the platform.

Business-owned data may include:

* business information;
* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* Sets;
* inventory;
* warehouses;
* orders;
* payments;
* refunds;
* discounts;
* cash registers;
* cash sessions;
* handovers;
* payroll;
* attendance;
* expenses;
* reports;
* report versions;
* notifications;
* audit history;
* synchronization records;
* business configuration.

The exact technical storage model is defined later in Database and Architecture documentation.

---

## 4. Business Lifecycle States

A business may pass through the following lifecycle:

```text
Active
   ↓
Subscription Expired
   ↓
Read-Only Retention
   ↓
Permanent Deletion
```

Reactivation can move the business from the expired/read-only state back to Active:

```text
Subscription Expired
        ↓
Subscription Reactivated
        ↓
Active
```

Not every individual record must pass through every business-level state.

For example, an employee may become inactive while the business remains active.

---

## 5. Entity-Level Lifecycle

Individual entities may have their own lifecycle independent of the business lifecycle.

Examples include:

* employee → Active / Inactive;
* branch → Active / Deactivated;
* product → Active / Inactive / Archived;
* recipe → Active Version / Archived Version;
* cash session → Open / Closed / Corrected;
* report → Current Version / Historical Version.

Entity deactivation or archival does not mean permanent deletion of the business data.

---

## 6. Active Business

An active business has a valid active subscription.

An active business may use functions permitted by:

* subscription tariff;
* employee permissions;
* branch scope;
* role configuration;
* business rules;
* device authorization.

Business data may be created or modified when the employee has the required permissions and the operation is permitted by the subscription.

---

## 7. Entity Deactivation

Deactivation prevents an entity from being actively used while preserving its historical information.

Examples include:

* employee deactivation;
* branch deactivation;
* product deactivation;
* menu item deactivation;
* temporary product unavailability;
* role deactivation where supported.

Deactivation does not mean permanent deletion.

---

## 8. Employee Deactivation

Employees with historical business activity should be deactivated rather than permanently deleted.

A deactivated employee:

* cannot perform new normal operational actions;
* remains identifiable in historical records;
* remains associated with previous orders;
* remains associated with cash sessions;
* remains associated with inventory actions;
* remains associated with payroll and attendance history;
* remains associated with audit history where applicable.

Historical employee identity must remain intact.

---

## 9. Branch Deactivation

A branch with historical data should normally be deactivated or archived rather than permanently deleted.

Historical branch data remains associated with that branch.

A deactivated branch must not accept normal new business operations.

Authorized users may continue to view historical branch information according to permissions and subscription state.

---

## 10. Product and Menu Lifecycle

Products and menu items may become inactive.

An inactive product:

* is not available for normal new order selection;
* remains available in historical transactions;
* retains relevant historical price information;
* retains relevant historical recipe context;
* remains identifiable in inventory and reports where applicable.

A product with historical relationships must not be permanently deleted through normal business operations.

Where archival is required, the product is archived instead.

---

## 11. Recipe Lifecycle

Recipes have their own historical lifecycle.

When a recipe changes:

1. the previous recipe version remains historical;
2. the new version requires the applicable approval;
3. the new version becomes effective according to the business rules;
4. historical transactions continue to reference the appropriate historical state.

Old recipes are archived rather than silently replaced.

Recipe changes must not rewrite historical orders or historical inventory operations.

---

## 12. Set Lifecycle

Sets have versioned composition.

When a Set composition changes:

* the previous configuration remains historical;
* the new configuration becomes effective according to the business rules;
* historical transactions retain the configuration applicable at the time of sale.

Underlying recipe changes must not silently rewrite historical Set composition.

---

## 13. Cash Session Lifecycle

Cash sessions have a controlled lifecycle.

Typical lifecycle:

```text
Open
  ↓
Closed
  ↓
Correction History Where Permitted
```

A closed cash session remains closed.

A correction does not reopen the session as an active session.

Corrections are recorded as separate controlled historical operations.

---

## 14. Cash Session Handover Lifecycle

Cashier handover creates a new cash session.

The lifecycle is:

```text
Previous Cashier
      ↓
Previous Cash Session Closed
      ↓
New Cashier Authenticates
      ↓
Physical Cash Count
      ↓
New Cash Session Opened
```

The physical Cash Register remains the same.

The new cashier receives a new Cash Session UUID.

The previous session remains historically associated with the previous cashier.

The handover does not merge two cashier sessions into one lifecycle record.

---

## 15. Cash Session Corrections

Corrections preserve:

* original values;
* corrected values;
* correction number;
* correction reason;
* responsible employee;
* authorization where applicable;
* timestamp;
* resulting difference.

The original cash-session information remains available.

The system must not transform a corrected session into a record that appears as though the original result never existed.

---

## 16. Report Lifecycle

Reports have their own historical lifecycle.

A report may be:

* generated;
* current;
* superseded by a newer version;
* historical.

Previous report versions remain immutable.

A new report version is created when relevant underlying business data changes.

A correction that does not change relevant report data must not create an unnecessary new report version.

Reports must not be deleted through normal user operations.

---

## 17. Audit Data Lifecycle

Audit records remain available throughout the business lifecycle.

During active and read-only periods, authorized users may access audit history according to:

* permissions;
* branch scope;
* business scope;
* subscription state.

Audit records cannot be selectively deleted through the normal business interface.

When the business is permanently deleted, its business-owned audit history is removed as part of the permanent deletion process.

---

## 18. Subscription Expiration

Subscription expiration does not immediately delete business data.

When the subscription expires, the business enters a restricted/read-only lifecycle state.

Existing business data remains preserved during the 60-day retention period.

Subscription expiration must affect all relevant operation paths, including:

* web/application access;
* POS;
* offline authorization;
* synchronization;
* trusted devices;
* background business operations.

Offline operation must not extend the subscription.

---

## 19. Expired Read-Only State

After subscription expiration:

* authorized users may continue to log in according to access rules;
* historical and existing data remains viewable;
* modifying business operations are blocked;
* relevant lists and sections may be exported to Excel;
* normal new business operations are unavailable;
* audit/history remains available according to permissions;
* offline operation cannot bypass the restriction.

The exact visibility remains subject to employee permissions and business scope.

---

## 20. Read-Only Retention Period

The business receives a **60-day retention/reactivation period** beginning from subscription expiration.

During this period:

* business data remains preserved;
* historical information remains accessible according to permissions;
* Excel export remains available where permitted;
* modifying functions remain blocked;
* subscription reactivation remains possible.

The retention period exists to allow the business to restore active operation without losing existing platform data.

---

## 21. Reactivation

If the business reactivates its subscription within the 60-day retention period:

```text
Expired / Read-Only
        ↓
Subscription Reactivated
        ↓
Active
```

Existing data remains available.

The system must not require the business to recreate:

* branches;
* employees;
* roles;
* permissions;
* products;
* recipes;
* menu;
* orders;
* inventory;
* cash history;
* payroll;
* reports;
* audit history.

Normal operation resumes according to the renewed subscription and current permissions.

---

## 22. Reactivation and Historical Data

Reactivation must not rewrite historical data.

Historical:

* orders;
* payments;
* refunds;
* cash sessions;
* inventory operations;
* payroll;
* report versions;
* audit history;

remain unchanged.

Reactivation affects the business's current subscription and operational capability.

---

## 23. Tariff Upgrade

A tariff upgrade does not require destructive data changes.

If the new tariff allows additional:

* branches;
* Owners;
* employees;
* functions;
* other subscription-controlled resources;

the additional capacity becomes available according to the new tariff.

Existing data remains unchanged.

---

## 24. Tariff Downgrade

A tariff downgrade must not automatically delete existing data.

If existing active resources exceed the new tariff limit:

* historical data remains;
* existing records are not silently deleted;
* creation of additional resources may be blocked;
* users may need to reduce active resources before creating additional resources;
* the system must clearly communicate the restriction.

The platform must not destructively delete data solely to satisfy a lower tariff limit.

---

## 25. Permanent Deletion

If the business does not reactivate within the 60-day retention period, the business becomes eligible for permanent deletion.

Permanent deletion means business-owned application data is removed according to the defined deletion process.

After permanent deletion, the business cannot be restored through normal business operations.

The exact technical deletion implementation is defined later in Architecture, Database, Security, and Operations documentation.

---

## 26. Deletion Deadline

Deletion eligibility is calculated from the subscription expiration date plus the defined 60-day retention period.

The system must preserve sufficient lifecycle information to determine:

* subscription expiration time/date;
* retention deadline;
* reactivation status;
* deletion eligibility.

Deletion eligibility must not depend solely on a user's local device clock.

The server/platform lifecycle state is authoritative.

---

## 27. Deletion Eligibility

A business becomes eligible for permanent deletion only when all of the following are true:

1. the subscription has expired;
2. the 60-day retention period has ended;
3. the subscription has not been reactivated.

If the business reactivates before deletion is executed, permanent deletion must not proceed.

---

## 28. Deletion Warning

The system must notify authorized users before permanent deletion.

Warnings should communicate:

* subscription expiration;
* current lifecycle state;
* remaining retention period where applicable;
* permanent deletion consequence;
* available reactivation action.

Warnings must be generated sufficiently early to provide meaningful notice within the defined lifecycle.

---

## 29. Deletion Scope

Permanent deletion applies to business-owned application data, including where applicable:

* business configuration;
* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* Sets;
* inventory;
* warehouses;
* orders;
* payments;
* refunds;
* discounts;
* cash registers;
* cash sessions;
* handovers;
* payroll;
* attendance;
* expenses;
* reports;
* report versions;
* notifications;
* audit history;
* synchronization records;
* business-owned files;
* other business-owned application data.

The exact technical deletion order and dependency handling are defined later.

---

## 30. Tenant Isolation During Deletion

Permanent deletion must affect only the target business.

Deletion must never affect:

* another business;
* another business's branches;
* another business's employees;
* platform-level tariff definitions;
* platform configuration;
* unrelated system records.

Tenant isolation must be enforced throughout the deletion process.

---

## 31. Cross-Reference Handling

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
        ├── Payroll
        └── Audit History
```

The technical implementation must ensure that business-owned relationships do not leave inconsistent application state after deletion.

Cross-business references must not cause deletion of unrelated business data.

---

## 32. Historical Data Protection

During the active and read-only lifecycle, historical data must remain protected.

Examples include:

* completed orders;
* historical payments;
* refunds;
* closed cash sessions;
* previous recipes;
* previous prices;
* Set configurations;
* payroll history;
* inventory history;
* correction history;
* audit history;
* report versions.

Historical records must not be silently removed simply because they are old.

---

## 33. Normal User Deletion

Normal business users must not have unrestricted permanent deletion capabilities.

Where historical information is important, the system should use:

* deactivation;
* archive;
* cancellation;
* correction;
* controlled lifecycle transitions.

Permanent business deletion is a lifecycle operation, not an ordinary business-user action.

---

## 34. Order Deletion

Completed or historical orders must not be permanently deleted through normal user operations.

Where an order must no longer be treated as active, the appropriate business state must be used, such as cancellation or another defined lifecycle state.

The historical order UUID remains available during the business lifecycle.

---

## 35. Payment and Refund Data

Payment and refund history must remain associated with the relevant order during the active and retention lifecycle.

A refund does not delete the original payment history.

The system must preserve the relationship between:

* original payment;
* refund;
* refund reason;
* responsible employee;
* order;
* relevant cash session where applicable.

---

## 36. Inventory Data

Inventory history remains available during the business lifecycle.

Historical:

* purchases;
* stock receipts;
* stock counts;
* adjustments;
* variances;
* prepared quantities;
* inventory deductions;
* costing context where required;

must not be silently removed.

After permanent business deletion, business-owned inventory history is deleted as part of the business deletion process.

---

## 37. Employee and Payroll Data

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

## 38. Offline Data During Subscription Expiration

A previously trusted device must not use offline authorization to bypass an expired subscription.

Offline authorization must remain bound to:

* employee;
* business;
* branch;
* device;
* permissions;
* subscription validity.

Once the subscription is expired, offline operation must not be used to continue modifying business data beyond the permitted lifecycle.

---

## 39. Offline Data During Permanent Deletion

After permanent business deletion, devices belonging to that business must no longer be able to synchronize business data with the deleted business.

Remaining local business data must not be treated as an independent active copy of the deleted business.

The technical handling of residual local data is defined in Security and Offline Synchronization documentation.

---

## 40. Backup and Deletion

Permanent deletion must consider system-managed copies of business data.

The technical implementation must define how deletion applies to:

* primary database;
* stored reports;
* uploaded files;
* replicas;
* caches;
* temporary processing data;
* backups.

The business requirement is that permanently deleted business data must not remain indefinitely accessible through normal platform operations.

Backup-specific retention and physical deletion mechanisms are defined in Deployment and Operations documentation.

---

## 41. Deletion Audit

The platform must preserve sufficient platform-level information to demonstrate that a permanent deletion process occurred.

The deletion record may include:

* business identity;
* deletion eligibility date;
* deletion execution time;
* deletion status;
* system process;
* result;
* failure information where applicable.

Business-level audit history is deleted with the business data according to the lifecycle rules.

The platform-level deletion event may remain separately identifiable where required for operational traceability.

---

## 42. Deletion Failure

If permanent deletion fails partially or completely, the system must not report successful deletion until the required deletion process has completed successfully.

The system should:

* record the failure;
* retry where appropriate;
* prevent an incorrect final lifecycle state;
* identify incomplete deletion;
* notify authorized platform personnel when intervention is required.

Deletion processing must be designed to avoid leaving an incorrectly reported deleted business.

---

## 43. Data Export Before Deletion

During the 60-day expired/read-only period, authorized users may export relevant lists and sections to Excel.

The purpose is to allow the business to retrieve useful information before permanent deletion.

Export availability remains subject to:

* business scope;
* employee permissions;
* read-only lifecycle rules.

---

## 44. No Additional Archive Period

Once the 60-day retention period ends without reactivation, the business proceeds to permanent deletion according to the lifecycle process.

There is no additional user-accessible archive period after the defined deadline.

The business must reactivate within the allowed period to retain its platform data.

---

## 45. Lifecycle Notifications

The lifecycle may generate notifications for:

* approaching subscription expiration;
* subscription expiration;
* read-only transition;
* approaching deletion deadline;
* successful reactivation;
* deletion eligibility;
* permanent deletion completion;
* permanent deletion failure.

Notifications must respect business scope, branch scope, employee permissions, and lifecycle state.

Notification delivery must not determine whether the underlying lifecycle transition is valid.

---

## 46. Data Lifecycle and Permissions

Data lifecycle state and employee permissions are separate controls.

For an active business:

```text
Subscription Active
+
Permission Granted
=
Operation Allowed
```

For an expired business:

```text
Subscription Expired
+
Permission Granted
=
Read-Only Restrictions Still Apply
```

An employee permission cannot override the subscription lifecycle.

---

## 47. Data Lifecycle and Trusted Devices

A trusted device provides authorized offline capability within its valid scope.

It does not provide:

* subscription extension;
* deletion protection;
* permission escalation;
* permanent data ownership;
* authorization to continue after business deletion.

Lifecycle restrictions remain authoritative.

---

## 48. Data Lifecycle and Reporting

Reports and report versions remain available during the active and read-only lifecycle according to permissions.

During the 60-day retention period:

* existing reports remain viewable;
* report history remains available where permitted;
* Excel export remains available where permitted;
* new modifying business activity is blocked.

After permanent deletion, business-owned reports and report versions are removed as part of the business deletion process.

---

## 49. Data Lifecycle and Audit

Audit records remain available during the active and read-only lifecycle.

They are protected from normal user deletion.

When permanent business deletion occurs, business-owned audit history is deleted with the business data according to the deletion process.

The platform-level deletion event may remain separately recorded where required.

---

## 50. Data Lifecycle and Synchronization

Lifecycle state must be synchronized across trusted devices.

The server/platform state is authoritative.

If a device has stale local lifecycle information, synchronization must enforce the current server state.

A device must not use stale offline authorization to continue operations after:

* subscription expiration;
* business deactivation where applicable;
* permanent deletion.

---

## 51. Data Lifecycle and Performance

Lifecycle processing must not significantly affect normal restaurant operations.

Tasks such as:

* subscription expiration processing;
* retention deadline calculation;
* deletion eligibility checks;
* report lifecycle processing;
* large-scale deletion;

should be performed without blocking normal POS operations.

Large lifecycle operations should be handled as controlled background processing where appropriate.

---

## 52. Lifecycle State Summary

| State                | Data      | Modification           | Export                | Reactivation             |
| -------------------- | --------- | ---------------------- | --------------------- | ------------------------ |
| Active               | Available | Allowed by permissions | Allowed               | Not applicable           |
| Deactivated Entity   | Preserved | Restricted for entity  | Allowed by permission | Entity-specific          |
| Subscription Expired | Preserved | Blocked                | Allowed               | Available                |
| Read-Only Retention  | Preserved | Blocked                | Allowed               | Available within 60 days |
| Permanent Deletion   | Removed   | Not available          | Not available         | Not available            |

---

## 53. Business Rules Summary

| Area                                  | Rule                                                        |
| ------------------------------------- | ----------------------------------------------------------- |
| Active business                       | Normal operations according to subscription and permissions |
| Entity deactivation                   | Preserves historical data                                   |
| Employee deactivation                 | Preserves historical employee identity                      |
| Branch deactivation                   | Preserves historical branch data                            |
| Product with historical relationships | Archive rather than normal deletion                         |
| Recipe lifecycle                      | Previous versions remain historical                         |
| Set lifecycle                         | Previous configurations remain historical                   |
| Closed cash session                   | Remains closed                                              |
| Cash correction                       | Preserves original result                                   |
| Cash handover                         | Previous and new cashier sessions remain distinct           |
| Report versions                       | Previous versions remain immutable                          |
| Subscription expiration               | Does not immediately delete data                            |
| Expired state                         | Read-only/restricted                                        |
| Retention period                      | 60 days from subscription expiration                        |
| Reactivation                          | Restores active operation using existing data               |
| Tariff upgrade                        | Does not require destructive data changes                   |
| Tariff downgrade                      | Must not destructively delete existing data                 |
| Permanent deletion                    | Eligible after 60 days without reactivation                 |
| Deletion deadline                     | Determined by server/platform lifecycle state               |
| Deletion warning                      | Required before permanent deletion                          |
| Normal user deletion                  | No unrestricted permanent deletion                          |
| Export before deletion                | Relevant Excel export remains available                     |
| Additional archive period             | Not provided                                                |
| Tenant isolation                      | Required during all lifecycle operations                    |
| Offline access                        | Cannot bypass lifecycle restrictions                        |
| Trusted device                        | Cannot extend subscription or prevent deletion              |
| Audit                                 | Lifecycle actions remain traceable                          |
| Deletion                              | Must cover business-owned application data consistently     |
| Deletion failure                      | Must not be reported as successful                          |
| Performance                           | Lifecycle processing must not block normal POS              |

---

## 54. Business Boundaries

The current Data Lifecycle and Deletion scope does not define:

* exact database cascade rules;
* exact physical deletion order;
* backup retention periods;
* cloud provider deletion mechanisms;
* cryptographic erasure;
* jurisdiction-specific legal retention requirements;
* disaster-recovery retention;
* forensic recovery procedures;
* external data export services;
* exact deletion scheduling implementation.

These topics must be defined later in Architecture, Database, Security, Deployment, and Operations documentation where required.

---

## 55. Related Documents

* `01_Product_Overview.md`
* `02_Business_Model.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

---

