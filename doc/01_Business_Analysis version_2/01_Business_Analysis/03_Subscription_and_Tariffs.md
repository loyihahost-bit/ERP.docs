# Subscription and Tariffs

**Document ID:** BA-03
**Status:** Accepted
**Version:** 2.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for subscriptions and tariff plans in FastFood ERP.

It describes:

* how tariffs are created and managed;
* how subscriptions are assigned to businesses;
* how resource limits are enforced;
* how feature availability is controlled;
* how subscription state interacts with user permissions;
* what happens when a subscription expires;
* how read-only access works;
* how tariff upgrades and downgrades behave;
* how the 60-day reactivation period works;
* how permanent deletion is handled after the retention period;
* how subscription-related actions are audited.

Subscription and tariff rules are business-level controls. Technical implementation details are defined in later system, architecture, database, security, and operations documents.

---

## 2. Subscription Model

FastFood ERP is provided to businesses through a subscription-based SaaS model.

Each Business/Tenant operates under a subscription.

A subscription is associated with:

* Business;
* Tariff;
* activation state;
* start date;
* expiration date;
* configured resource limits;
* enabled functionality;
* applicable subscription configuration.

The subscription determines the business's platform-level entitlement.

A subscription does **not** replace the employee permission system.

An operation may be performed only when both subscription entitlement and user authorization allow it.

---

## 3. Separation of Subscription and Permissions

Subscription and employee permissions are separate control layers.

The effective access model is:

**Subscription Entitlement + User Permission + Branch Scope**

An operation must satisfy all applicable conditions.

For example:

* a tariff may include Payroll;
* an Owner may have Payroll permission;
* a Manager without Payroll permission cannot use Payroll;
* a user with Payroll permission cannot use Payroll if the active tariff does not include it.

Likewise, resource limits are controlled by the subscription even when the user has the required permission.

For example:

* an Owner may have permission to create employees;
* but employee creation is blocked when the subscription employee limit has been reached.

Trusted-device status is also separate from subscription entitlement and employee permissions.

---

## 4. Tariff Ownership

Tariffs are managed by the **Super Admin**.

Super Admin may:

* create tariffs;
* modify tariff configuration;
* define branch limits;
* define Owner limits;
* define employee limits;
* enable or disable platform functions;
* define additional resource limits;
* define additional entitlement rules;
* activate or deactivate tariff availability.

Super Admin operates at the platform level.

Super Admin is not automatically an Owner of a Business and is not automatically responsible for the business's daily operations.

Tariff configuration must be data-driven rather than hard-coded into individual business workflows.

---

## 5. Tariff Structure

A tariff may define multiple categories of configuration.

### 5.1. Resource Limits

Examples include:

* maximum active branches;
* maximum active Owners;
* maximum active employees.

Additional resource limits may be introduced in the future without redesigning the overall subscription model.

### 5.2. Feature Availability

A tariff may control access to specific modules or capabilities.

Examples include:

* selected reports;
* payroll;
* advanced inventory functionality;
* additional management functions;
* future platform modules.

The subscription model must support adding new feature entitlements without redesigning the business model.

### 5.3. Business Configuration Entitlements

A tariff may also control access to configurable business capabilities where such limits are introduced by the product.

Examples may include:

* advanced operational modules;
* additional reporting capabilities;
* future integrations;
* future automation capabilities.

Such capabilities remain subject to the employee permission system.

---

## 6. Initial Product Capacity

The initial product model supports businesses with up to **10 branches**, depending on the selected tariff.

The 10-branch scope is the initial product capacity and is not intended to prevent future expansion.

The architecture must allow higher limits to be introduced later without changing the fundamental Business → Branch model.

---

## 7. Branch Limit

Each tariff may define a maximum number of active branches.

If the configured branch limit has been reached:

* creating another branch is blocked;
* existing branches remain preserved;
* existing branch history remains available;
* the authorized user is informed that the limit has been reached.

Increasing the subscription limit allows additional branches to be created.

A branch limit must not cause existing branches to be silently deleted.

---

## 8. Owner Limit

Each tariff may define the maximum number of active Owners allowed for a Business.

If the Owner limit has been reached:

* another Owner cannot be created;
* existing Owners remain active;
* historical Owner-related records remain preserved;
* the authorized user is informed that the limit has been reached.

Owner limits apply to the subscription-defined active Owner capacity.

---

## 9. Employee Limit

Each tariff may define the maximum number of active employees allowed within a Business.

If the employee limit has been reached:

* creation of another active employee is blocked;
* existing employees remain active;
* employee history remains preserved;
* the authorized user is informed that the limit has been reached.

Employee limits must be enforced consistently across:

* web interfaces;
* APIs;
* administrative workflows;
* background operations;
* other supported entry points.

Deactivating an employee may release active employee capacity without deleting historical records.

---

## 10. Feature Availability

A tariff may enable or disable specific functions.

If a function is not included in the active tariff:

* the corresponding modifying capability is unavailable;
* the user receives a clear explanation when access is attempted;
* existing data related to the function is preserved;
* historical records remain accessible according to subscription state and permissions.

Feature availability must not silently delete historical business data.

Feature availability and employee permission remain separate.

---

## 11. Subscription State

The business subscription lifecycle is:

**Active → Expired → Read-Only Retention → Permanent Deletion**

The platform may use additional internal technical states when necessary, but they must not change the defined business behavior.

### 11.1. Active

The business has a valid active subscription.

### 11.2. Expired

The subscription has passed its expiration point.

Modifying business operations are blocked.

Read-only access remains available during the retention period.

### 11.3. Read-Only Retention

The business remains in a protected read-only state during the 60-day reactivation period.

### 11.4. Permanent Deletion

If the subscription is not reactivated within the defined retention period, the business data is permanently deleted according to the Data Lifecycle rules.

---

## 12. Active Subscription

While the subscription is active:

* permitted users can perform normal operations;
* tariff limits are enforced;
* enabled modules are available;
* employee permissions are applied;
* branch scope is applied;
* business rules remain enforced;
* trusted-device rules remain enforced;
* offline operation is available according to valid offline authorization.

Normal business workflows may continue while the subscription remains active.

---

## 13. Subscription Expiration

When the subscription reaches its expiration point, the Business enters the expired/read-only state.

The system must enforce expiration rules based on the authoritative subscription state.

### 13.1. Allowed After Expiration

Users may:

* log in;
* view existing business data;
* view historical records;
* review operational history;
* access permitted read-only reports;
* export relevant lists and reports to Excel;
* review information required for reactivation or business data preservation.

### 13.2. Blocked After Expiration

Operations that modify protected business data are blocked.

Examples include:

* creating new orders;
* modifying operational orders;
* accepting new operational transactions;
* creating employees;
* creating branches;
* changing recipes;
* changing menu configuration;
* changing inventory;
* creating production records;
* modifying business configuration;
* changing protected operational records;
* other modifying operations defined by the system.

The exact technical enforcement is defined in later system and authorization documents.

---

## 14. Read-Only Access

Expired businesses retain read-only access during the reactivation period.

Read-only access exists to allow the business to:

* review historical information;
* verify existing records;
* inspect operational history;
* review reports;
* export data;
* prepare for subscription reactivation.

Read-only access must not be treated as an active subscription.

Read-only access also does not grant permission to bypass normal employee access restrictions.

---

## 15. Excel Export After Expiration

Expired businesses may export relevant business data to Excel during the read-only period.

The required export format is:

**`.xlsx`**

Current reporting/export scope does not require PDF or CSV as the standard report export format.

Export access remains subject to:

* subscription state;
* user permissions;
* branch scope;
* data-access rules.

Exports must not alter or delete the source business data.

---

## 16. Reactivation Period

After subscription expiration, the Business receives a **60-day reactivation period**.

During this period:

* business data remains stored;
* read-only access remains available;
* Excel export remains available;
* the subscription may be reactivated;
* historical records remain preserved.

The 60-day period begins from the authoritative subscription expiration timestamp.

The retention period is a business rule and must not depend on a local device clock.

---

## 17. Subscription Reactivation

A Business may reactivate its subscription during the 60-day retention period.

After successful reactivation:

* modifying functions become available again;
* the active tariff becomes effective;
* tariff limits are enforced again;
* enabled features become available;
* existing business data remains preserved;
* existing historical records remain unchanged.

Reactivation does not:

* create a new Business;
* replace the existing Business;
* reset historical data;
* recreate branches;
* recreate employees;
* rewrite reports;
* remove audit history.

The existing Business continues operating with its preserved history.

---

## 18. Permanent Data Deletion

If the Business does not reactivate its subscription within 60 days after expiration, the Business enters permanent deletion.

Permanent deletion applies according to the Data Lifecycle and Deletion rules.

The deletion process may include the Business's:

* operational data;
* branch data;
* employee data;
* orders;
* payments;
* inventory records;
* recipes;
* reports;
* audit history;
* configuration;
* other Business-owned data.

The exact deletion sequence and technical implementation are defined in the Data Lifecycle, Database, Security, and Operations documents.

There is no additional user-accessible archive period after the defined 60-day retention period.

Permanent deletion must be treated as irreversible.

---

## 19. Deletion Warning Notifications

The system must provide advance notifications before permanent deletion.

Notifications must clearly communicate:

* subscription expiration;
* current read-only state;
* remaining retention period;
* permanent deletion deadline;
* required action;
* reactivation availability.

Multiple reminders should be provided rather than relying on a single final notification.

Exact notification timing belongs to:

* `17_Notifications_and_Alerts.md`;
* `20_Business_Rules.md`;
* relevant operational specifications.

---

## 20. Tariff Change

A Business may change its tariff according to platform and commercial rules.

A tariff change may affect:

* branch limits;
* Owner limits;
* employee limits;
* enabled features;
* other subscription-controlled resources.

A tariff change must not silently destroy existing business data.

Tariff changes must preserve historical integrity.

---

## 21. Tariff Downgrade

A downgrade must not cause immediate destructive data loss.

For example, if a Business currently has:

* 8 active branches;

and changes to a tariff allowing:

* 5 active branches;

the system must **not automatically delete 3 branches**.

Instead:

* existing branches remain preserved;
* existing branch history remains preserved;
* creation of additional branches is blocked while the Business exceeds the new limit;
* the user is informed about the limit conflict;
* the Business may upgrade again or otherwise resolve the conflict.

The same principle applies to:

* Owners;
* employees;
* other subscription-controlled resources.

A downgrade changes future entitlement. It does not silently rewrite historical ownership or operational data.

---

## 22. Feature Downgrade

If a downgrade removes access to a previously enabled feature:

* existing feature-related data remains preserved;
* new modifying operations using that feature are blocked;
* read access remains available where allowed by subscription state and permissions;
* historical records remain traceable.

The system must not delete historical data solely because the new tariff no longer includes the feature.

---

## 23. Tariff Upgrade

When a Business upgrades its tariff:

* newly available resource limits become effective;
* newly enabled features become available;
* existing data remains unchanged;
* the Business may use newly available capacity once the upgrade is active.

Examples include:

* increasing branch capacity;
* increasing employee capacity;
* increasing Owner capacity;
* enabling additional reports;
* enabling additional modules.

An upgrade must not require recreation of existing Business data.

---

## 24. Limit Enforcement

Subscription limits must be enforced consistently.

The system must validate limits before creating or activating a resource controlled by the tariff.

Examples:

* branch creation checks branch capacity;
* Owner creation checks Owner capacity;
* employee activation checks employee capacity;
* feature-dependent operations check feature entitlement.

Limit enforcement must apply regardless of whether the request originates from:

* the normal UI;
* an API;
* an offline synchronization process;
* a background process;
* another supported system entry point.

Server-side validation is authoritative.

---

## 25. Subscription and Branch Scope

Subscription entitlement applies at the Business level.

Branch-level access is controlled separately through employee permissions and branch scope.

A subscription does not automatically give a user access to every branch.

For example:

* a Business may have 5 branches;
* a Manager may be authorized for only 2 branches;
* the Manager must not access the other 3 branches merely because the Business subscription allows them.

Subscription controls **Business capacity and feature entitlement**.

Permissions control **who may perform an operation and where**.

---

## 26. Subscription and Offline Operation

Offline operation must respect subscription state and offline authorization.

A trusted device may continue offline operation only while its offline authorization remains valid.

Offline authorization does not create a new subscription entitlement.

Offline operation must not be used to bypass:

* subscription limits;
* subscription expiration;
* employee permissions;
* branch scope;
* business isolation;
* operational business rules.

When synchronization resumes, the server becomes authoritative for the current subscription state.

If the subscription expired while a device was offline, synchronization must validate the transaction against the authoritative server state and the applicable offline rules.

Technical offline behavior is defined in:

`06_Authentication_and_Trusted_Devices.md`

and

`07_Offline_Operation_and_Synchronization.md`.

---

## 27. Subscription and Trusted Devices

Trusted-device status is a security mechanism, not a subscription entitlement.

A trusted device does not grant permission to:

* bypass tariff limits;
* bypass subscription expiration;
* access another Business;
* access another Branch without scope;
* bypass employee permissions;
* bypass server-side validation.

A trusted device only provides the device-level authorization required for supported offline operation and related workflows.

---

## 28. Subscription and Business Data Isolation

Subscription enforcement must operate within the Business/Tenant boundary.

A Business must never gain access to another Business's:

* data;
* branches;
* employees;
* orders;
* inventory;
* reports;
* exports;
* subscription information;
* audit history.

Subscription state does not weaken tenant isolation.

Tenant isolation must remain enforced across:

* API requests;
* database access;
* reports;
* exports;
* background jobs;
* notifications;
* offline synchronization.

---

## 29. Subscription Auditability

Important subscription and tariff actions must be recorded in audit history.

Examples include:

* tariff creation;
* tariff modification;
* tariff assignment;
* subscription activation;
* subscription renewal;
* subscription expiration;
* subscription reactivation;
* tariff upgrade;
* tariff downgrade;
* limit changes;
* feature entitlement changes;
* deletion scheduling;
* deletion warning;
* permanent deletion;
* other significant subscription-state changes.

Audit records should identify:

* actor or system process;
* Business;
* affected entity;
* previous state;
* new state;
* timestamp;
* reason or source where applicable.

System-generated actions must identify the relevant background/system process.

---

## 30. Historical Data Preservation

Subscription state changes must not silently rewrite historical Business records.

The following must remain historically traceable while the Business data is retained:

* orders;
* order modifications;
* payments;
* cash sessions;
* refunds;
* cancellations;
* inventory history;
* production history;
* recipe history;
* reports;
* report versions;
* corrections;
* employee history;
* payroll history;
* audit history;
* other protected operational records.

Subscription expiration controls access.

It does not immediately rewrite or remove historical information.

---

## 31. Subscription Changes and Existing Orders

Subscription changes must not recalculate or modify historical orders.

Existing orders retain their original:

* amounts;
* products;
* customization;
* payment information;
* inventory impact;
* timestamps;
* business and branch context.

Subscription changes affect future access and operations, not historical transaction meaning.

---

## 32. Subscription Changes and Reports

Subscription changes must not silently modify already generated report versions.

Existing report versions remain immutable according to the report-versioning rules.

If a new report version is required because of a valid underlying data change, the new version must be created according to:

`16_Reports_and_Dashboards.md`

and the previous version must remain unchanged.

---

## 33. Subscription Changes and Configuration

Subscription changes may affect which configuration options are available.

However:

* historical configuration must remain traceable;
* existing operational records must retain their original meaning;
* configuration changes must not silently rewrite old orders or reports;
* newly enabled functionality becomes available according to the active subscription;
* newly disabled functionality must not cause destructive historical changes.

---

## 34. Expired Business Operational Boundary

When a Business is expired:

### The Business may

* authenticate;
* view permitted data;
* inspect history;
* view permitted reports;
* export permitted data;
* review subscription status;
* reactivate the subscription.

### The Business may not

* create new operational orders;
* accept new operational transactions;
* modify protected operational records;
* create new branches;
* create new employees;
* modify inventory;
* modify recipes;
* modify menu configuration;
* perform other protected modifying operations.

The detailed list of modifying operations is maintained by the relevant domain documents.

---

## 35. Subscription Lifecycle Summary

| State                         | Data Access            | Modifying Operations                        | Excel Export   | Reactivation  |
| ----------------------------- | ---------------------- | ------------------------------------------- | -------------- | ------------- |
| Active                        | Allowed by permissions | Allowed according to tariff and permissions | Allowed        | N/A           |
| Expired / Read-Only Retention | Read-only              | Blocked                                     | Allowed        | Allowed       |
| Permanent Deletion            | No business access     | Not applicable                              | Not applicable | Not available |

---

## 36. Subscription Business Rules Summary

| Rule                                          | Requirement                                 |
| --------------------------------------------- | ------------------------------------------- |
| Subscription model                            | SaaS                                        |
| Subscription owner                            | Business/Tenant                             |
| Tariff management                             | Super Admin                                 |
| Initial branch capacity                       | Up to 10 branches depending on tariff       |
| Owner limit                                   | Configurable by tariff                      |
| Employee limit                                | Configurable by tariff                      |
| Feature availability                          | Configurable by tariff                      |
| Subscription and permissions                  | Separate control layers                     |
| Branch scope                                  | Separate from subscription entitlement      |
| Active state                                  | Normal permitted operation                  |
| Expired state                                 | Read-only retention                         |
| Modification after expiration                 | Blocked                                     |
| Excel export after expiration                 | Allowed                                     |
| Reactivation period                           | 60 days                                     |
| Data retention during period                  | Preserved                                   |
| Data deletion after period                    | Permanent                                   |
| Downgrade destructive deletion                | Not allowed                                 |
| Existing over-limit resources after downgrade | Preserved                                   |
| New over-limit resource creation              | Blocked                                     |
| Upgrade                                       | New entitlement becomes available           |
| Trusted device                                | Does not bypass subscription                |
| Offline operation                             | Must respect valid authorization            |
| Tenant isolation                              | Always enforced                             |
| Historical data                               | Preserved while retained                    |
| Audit                                         | Required for important subscription changes |

---

## 37. Business Model Boundary

This document defines subscription and tariff behavior at the business level.

The following are intentionally defined in later documents:

* subscription database structure;
* tariff database structure;
* entitlement implementation;
* API authorization;
* permission enforcement;
* offline authorization;
* synchronization behavior;
* deletion implementation;
* background jobs;
* notification delivery;
* payment processing for subscriptions;
* infrastructure-level retention and deletion.

Technical implementation must not change these business rules without an explicit business requirement change and, where applicable, an ADR.

---

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

