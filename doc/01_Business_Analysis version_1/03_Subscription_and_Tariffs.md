# Subscription and Tariffs

**Document ID:** BA-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for subscriptions and tariff plans in FastFood ERP.

It describes how subscription plans are configured, how limits are enforced, what happens when a subscription expires, and how the system handles the 60-day reactivation period before permanent data deletion.

## 2. Subscription Model

FastFood ERP is provided to businesses through a subscription-based SaaS model.

Each business must have an active subscription to use the system's modifying and operational functions.

A subscription is associated with:

* Business;
* Tariff;
* activation state;
* start date;
* expiration date;
* configured limits;
* enabled functionality.

The subscription state determines what the business can currently do.

## 3. Tariff Ownership

Tariffs are managed by the **Super Admin**.

Super Admin can:

* create tariffs;
* modify tariff configuration;
* define resource limits;
* enable or disable functions;
* define Owner limits;
* define employee limits;
* define branch limits;
* introduce additional tariff rules in the future.

Tariff configuration must be data-driven rather than hard-coded into individual business workflows.

## 4. Tariff Structure

A tariff may define two major categories of configuration:

### 4.1. Resource Limits

Examples include:

* maximum number of branches;
* maximum number of Owners;
* maximum number of employees.

Additional resource limits may be introduced later.

### 4.2. Feature Availability

A tariff may control whether specific system capabilities are available.

Examples include:

* selected reports;
* payroll functionality;
* advanced inventory functionality;
* additional management modules;
* other future platform features.

The system must support adding new feature flags without redesigning the subscription model.

## 5. Branch Limit

Each tariff may define the maximum number of active branches available to a business.

The initial product model supports businesses with up to **10 branches**, depending on the selected tariff.

If the configured branch limit has been reached:

* creating another branch is blocked;
* existing branches remain operational;
* the user is informed that the configured limit has been reached.

Increasing the subscription limit allows additional branches to be created without changing the existing branch data model.

## 6. Owner Limit

Each tariff may define the maximum number of Owners allowed for a business.

If the Owner limit has been reached:

* another Owner cannot be created;
* existing Owners remain active;
* the user is informed that the Owner limit has been reached.

Owner limits apply to active Owners according to the business's subscription configuration.

## 7. Employee Limit

Each tariff may define the maximum number of employees that can be active within a business.

If the employee limit is reached:

* creation of another active employee is blocked;
* existing employees remain active;
* the system informs the authorized user that the employee limit has been reached.

Employee limits must be enforced consistently across all interfaces.

## 8. Feature Limits

A tariff may enable or disable specific functions.

If a function is not included in the active tariff:

* the corresponding modifying capability must not be available;
* the user should receive a clear explanation when access is attempted;
* existing data related to the function must not be unnecessarily deleted.

Feature availability is separate from employee permissions.

A user must satisfy both:

**Subscription Feature Availability + User Permission**

before performing a restricted operation.

## 9. Subscription State

The subscription lifecycle must distinguish between active and expired states.

At minimum, the business lifecycle includes:

1. Active
2. Expired / Read-Only
3. Permanently Deleted

The system may internally maintain additional technical states where necessary, but these states must not change the defined business behavior.

## 10. Active Subscription

When the subscription is active:

* permitted users can perform normal operations;
* tariff limits are enforced;
* enabled modules are available;
* employee permissions are applied;
* branches can operate normally;
* offline operation is available according to trusted-device authorization rules.

Normal business workflows continue while the subscription remains active.

## 11. Subscription Expiration

When the subscription reaches its expiration date, the business enters the expired/read-only state.

The system must immediately enforce the expired subscription rules.

### Allowed

Users may:

* log in;
* view existing data;
* review historical records;
* access permitted read-only reports;
* export relevant lists and sections to Excel.

### Blocked

Operations that modify business data are blocked.

Examples include:

* creating new orders;
* modifying existing operational data;
* creating employees;
* changing recipes;
* changing inventory;
* modifying business configuration;
* other operations that alter protected business data.

## 12. Read-Only Access

Expired businesses retain read-only access during the reactivation period.

Read-only access exists to allow the business to:

* review historical information;
* verify existing records;
* export data;
* make an informed decision about reactivation.

Read-only access must not be treated as an active subscription.

## 13. Excel Export After Expiration

Expired businesses may export relevant data to Excel.

The export capability is intended to provide access to business information during the read-only period.

Export availability remains subject to the relevant permission and system access rules.

The user-facing report format is:

**`.xlsx`**

PDF and CSV are not part of the current report export requirement.

## 14. Reactivation Period

After subscription expiration, the business receives a **60-day reactivation period**.

During this period:

* business data remains stored;
* read-only access remains available;
* Excel export remains available;
* the subscription can be reactivated.

The 60-day period begins from the subscription expiration point according to the platform's official subscription timestamp.

## 15. Permanent Deletion

If the business does not reactivate the subscription within 60 days, its business data is permanently deleted.

The deletion process applies to the business's stored operational data according to the Data Lifecycle rules.

There is no additional user-accessible archive period after the 60-day retention period.

The deletion process must not be treated as a temporary deactivation.

## 16. Deletion Warning Notifications

The system must provide advance notifications before permanent deletion.

Notifications should clearly communicate:

* subscription expiration;
* current read-only status;
* remaining reactivation period;
* permanent deletion deadline;
* required action.

The notification schedule should provide multiple reminders rather than relying on a single final notification.

The exact notification timing is defined by the notification and business-rule documents.

## 17. Subscription Renewal

A business may reactivate its subscription during the reactivation period.

After successful reactivation:

* normal modifying functions become available again;
* tariff limits are re-applied;
* enabled features become available according to the active tariff;
* existing business data remains available.

Reactivation does not create a new business or replace existing operational history.

## 18. Tariff Change

A business may change its tariff according to the platform's commercial rules.

A tariff change may affect:

* branch limits;
* Owner limits;
* employee limits;
* enabled features;
* other configurable resources.

Existing data must not be silently deleted solely because a lower tariff no longer permits the current quantity.

For example, if a business has 8 branches and changes to a tariff allowing only 5 branches, the system must not automatically delete 3 existing branches.

Instead, the business should be prevented from creating additional resources that exceed the new limit until the subscription configuration permits them again.

## 19. Downgrade Protection

A tariff downgrade must not cause immediate destructive data loss.

If current resource usage exceeds the new tariff limit:

* existing records remain preserved;
* creation of additional resources is blocked where necessary;
* the user is informed about the exceeded limit;
* the business may upgrade again or otherwise resolve the limit conflict.

This rule protects historical and operational data.

## 20. Tariff Upgrade

When a business upgrades its tariff:

* newly available limits become effective according to the subscription change;
* newly enabled features become available;
* existing business data remains unchanged;
* the business can use the additional capacity immediately once the upgrade is active.

Examples include:

* increasing branch capacity;
* increasing employee capacity;
* increasing Owner capacity;
* enabling additional modules.

## 21. Permission and Tariff Interaction

Subscription limits and user permissions are separate control layers.

An operation is permitted only when both conditions are satisfied:

**Tariff Allows the Function/Resource**

and

**User Has the Required Permission**

For example:

* a tariff may allow payroll;
* but a cashier may still not have payroll permission.

Likewise:

* an Owner may have permission to create employees;
* but cannot create another employee if the business has already reached its tariff employee limit.

## 22. Offline Operation and Subscription State

Offline operation must respect the subscription state and offline authorization rules.

A device may continue offline operation only while it has valid offline authorization.

If the subscription becomes expired while a device is offline, the system must apply the defined offline authorization and synchronization rules rather than allowing unlimited offline operation beyond the authorized period.

When synchronization resumes, the server becomes authoritative for the current subscription state.

## 23. Subscription and Trusted Devices

Trusted-device status does not override subscription restrictions.

A trusted device provides device authorization for offline/operational access.

It does not provide permission to:

* bypass tariff limits;
* bypass subscription expiration;
* access another business;
* bypass employee permissions.

## 24. Subscription Auditability

Important subscription actions must be recorded in audit history.

Examples include:

* tariff creation;
* tariff modification;
* tariff assignment;
* subscription activation;
* subscription renewal;
* subscription expiration;
* tariff upgrade;
* tariff downgrade;
* limit changes;
* feature availability changes;
* deletion scheduling;
* permanent deletion.

Audit records should identify:

* actor or system process;
* affected business;
* previous state;
* new state;
* timestamp;
* relevant reason or source where applicable.

## 25. Data Preservation Principle

Subscription state changes must not silently alter historical business records.

The following must remain historically traceable:

* orders;
* cash sessions;
* reports;
* corrections;
* inventory history;
* employee history;
* audit history;
* other protected operational records.

Subscription expiration controls access; it does not immediately rewrite or remove historical information.

## 26. Subscription Business Rules Summary

| Rule                           | Requirement                                 |
| ------------------------------ | ------------------------------------------- |
| Subscription model             | SaaS                                        |
| Tariff management              | Super Admin                                 |
| Initial branch capacity        | Up to 10 branches depending on tariff       |
| Owner limit                    | Configurable by tariff                      |
| Employee limit                 | Configurable by tariff                      |
| Feature availability           | Configurable by tariff                      |
| Expired state                  | Read-only                                   |
| Modification after expiration  | Blocked                                     |
| Excel export after expiration  | Allowed                                     |
| Reactivation period            | 60 days                                     |
| Data deletion after period     | Permanent                                   |
| Downgrade destructive deletion | Not allowed                                 |
| Tariff limits                  | Enforced consistently                       |
| Permissions                    | Separate from tariff                        |
| Trusted device                 | Does not bypass subscription                |
| Audit                          | Required for important subscription changes |

## 27. Business Model Boundary

This document defines subscription and tariff behavior at the business level.

Detailed implementation decisions belong to later documents, including:

* subscription data model;
* tariff database structure;
* entitlement architecture;
* API authorization;
* offline subscription validation;
* deletion implementation;
* background jobs;
* notification delivery.

These technical decisions must not change the business rules defined here without an explicit business requirement change and, where applicable, an ADR.

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_B_

