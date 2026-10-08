# Menu, Pricing and Configuration

**Document ID:** SA-18
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for Business-level menu configuration, Branch menu availability, Product pricing, Branch price overrides and related configuration changes.

The system must provide centralized Business configuration while allowing Branch-specific operational differences.

The system must preserve historical price and configuration integrity.

---

## 2. Scope

This document covers:

* Business-level menu;
* Branch menu;
* Product availability;
* Product categories;
* Product pricing;
* Branch price overrides;
* price snapshots;
* configuration versions;
* effective configuration;
* Cash Session boundaries;
* discounts;
* custom markup;
* Sets;
* Recipe dependency;
* offline configuration;
* synchronization;
* audit;
* concurrency;
* subscription entitlement;
* historical integrity.

---

## 3. Menu Context

Menu configuration exists within the following hierarchy:

```text id="mnu482"
Business
   ↓
Global Menu
   ↓
Branch Menu Configuration
   ↓
POS Availability
```

The Business owns the global Product/menu definition.

Branches control permitted local availability according to their scope and permissions.

---

## 4. Global Menu

The Global Menu represents the Business-level collection of Products that may be offered by the Business.

It defines the common commercial catalog.

Global menu configuration may include:

* Product;
* category;
* active state;
* standard price;
* image;
* relevant Product configuration.

Global configuration does not automatically mean that every Branch sells the Product.

---

## 5. Branch Menu

Each Branch has a local menu configuration based on the Business Global Menu.

Branch configuration may determine:

* Product available at Branch;
* Product inactive at Branch;
* Branch-specific price;
* operational availability.

A Branch must not create a separate Product identity merely to customize local availability.

---

## 6. Branch Menu Isolation

A Branch configuration change affects only that Branch unless the operation explicitly changes Business-level configuration.

For example:

```text id="brch91"
Business Product: Burger

Branch A → Active
Branch B → Inactive
Branch C → Active
```

Disabling Burger in Branch B must not disable it in Branch A or C.

---

## 7. Product Category

Every Product belongs to exactly one menu category.

Category assignment is part of Product configuration.

Changing a Product's category does not create a new Product identity.

Historical Orders remain associated with the original Product and historical information required for reporting.

---

## 8. Menu Availability vs Inventory

Menu availability and inventory availability are separate concepts.

A Product may be:

* enabled in the menu but out of stock;
* enabled in the menu but equipment unavailable;
* disabled in the menu while stock exists;
* active and available in both menu and inventory.

The POS must validate actual operational availability when required.

---

## 9. Product Activation

A Product may be active at Business level but unavailable at a specific Branch.

Product activation and Branch menu availability are separate states.

A Product must not become sellable at a Branch solely because it was created globally.

---

## 10. Menu Configuration Permissions

Menu configuration operations require appropriate permissions.

Permissions may include:

* Product activation/deactivation;
* Branch menu configuration;
* category management;
* price configuration;
* Branch price override;
* Set configuration;
* Recipe configuration.

The exact permission assignment follows the general permission model.

---

## 11. Global Standard Price

A Product may have a Business-level standard selling price.

This price is the default price for Branches without a Branch-specific override.

The standard price is separate from:

* inventory cost;
* Last Purchase Cost;
* FIFO cost;
* Average Cost;
* discount amount.

---

## 12. Branch Price Override

A Branch may override the Business-level standard price if the employee has the required permission.

The override:

* applies only to the selected Branch;
* does not change the global standard price;
* does not affect other Branches;
* is stored as Branch-specific configuration.

---

## 13. Branch Price Override Example

Example:

```text id="prc814"
Global Product Price: 30,000

Branch A: 30,000
Branch B: 32,000
Branch C: 28,000
```

Changing Branch B to 32,000 does not modify Branch A or Branch C.

---

## 14. Price Effective Configuration

Price changes must have a deterministic effective point.

For the current system:

**New menu and pricing configuration becomes operational from the next Cash Session.**

This prevents an active POS session from silently switching prices during ongoing work.

---

## 15. Existing Cash Session

A Cash Session continues using the valid configuration applicable to that session.

A price change made during an active session does not silently change the operational price configuration already in use.

The exact active configuration version remains identifiable.

---

## 16. New Cash Session

After a new Cash Session starts, the latest valid approved/active menu and pricing configuration becomes available.

The new configuration is used for new Orders subject to all other validations.

---

## 17. Open Order Price Snapshot

When a Product is added to an Order, its applicable selling price is captured in the Order Item snapshot.

Later price changes do not change that existing Order Item price.

This applies even when the Order remains open across Cash Session transitions.

---

## 18. Historical Price Integrity

Historical Orders retain their original price.

The system must never recalculate historical Order totals from the current Product price.

Historical financial reports must use the applicable historical Order/payment snapshots.

---

## 19. Price Change History

Important price changes must preserve:

* previous price;
* new price;
* Product;
* Business;
* Branch where applicable;
* actor;
* timestamp;
* effective configuration/version;
* reason where required.

The historical change must remain immutable.

---

## 20. Price Change Audit

Price changes are auditable operations.

Audit context should include:

* Event UUID;
* Business UUID;
* Branch UUID where applicable;
* Employee UUID;
* Device UUID;
* Product UUID;
* configuration version;
* old value;
* new value;
* reason;
* timestamp;
* result.

---

## 21. Discounts

Discounts are separate from Product pricing.

A discount:

* changes the final Order amount;
* does not change the Product base price;
* does not modify the Global Menu price;
* does not create a new Product price;
* is stored in the Order financial snapshot.

Historical discounts remain associated with the original transaction.

---

## 22. Discount and Price Separation

Example:

```text id="dsc930"
Product Price = 30,000

Discount = 5,000

Final Order Amount = 25,000
```

The Product's configured price remains 30,000.

The discount is a separate transaction-level financial adjustment.

---

## 23. Discount Permission

Discount application requires explicit permission.

The system must validate:

* Employee status;
* Branch scope;
* permission;
* subscription entitlement;
* Order state.

Unauthorized discounts are rejected.

---

## 24. Custom Order Markup

The system supports a custom markup operation for authorized Order configuration.

The allowed markup range is:

**0%–100%.**

The final value is calculated from Last Purchase Cost:

```text id="mkp217"
Final Price = Last Purchase Cost × (1 + Markup / 100)
```

The operation must use the applicable Last Purchase Cost for the relevant Product/Branch context.

---

## 25. Markup vs Standard Price

Custom markup does not modify the Business-level standard Product price.

It is a transaction-specific pricing operation.

The resulting transaction price is captured in the Order snapshot.

---

## 26. Markup Validation

The system must reject:

* markup below 0%;
* markup above 100%;
* invalid Product;
* missing applicable cost;
* unauthorized operation.

The calculated result must be deterministic.

---

## 27. Price and Inventory Cost

Selling price and inventory cost are separate concepts.

Changing the selling price does not change:

* stock quantity;
* purchase cost;
* FIFO layers;
* Average Cost;
* Last Purchase Cost.

Likewise, purchasing inventory does not automatically change the historical selling price of existing Orders.

---

## 28. Recipe Dependency

Products that require Recipes must have a valid applicable Recipe Version before normal sale.

Menu availability does not bypass Recipe requirements.

A Product may be configured in the menu before a Recipe is approved, but it cannot be normally sold when required Recipe conditions are not satisfied.

---

## 29. Recipe Change

Recipe changes affect inventory composition, not historical selling price.

When a Recipe changes:

* historical Orders retain their price;
* historical inventory deductions retain their Recipe Version;
* new effective operations use the new Recipe Version.

Recipe changes do not automatically change the Product price.

---

## 30. Set Pricing

A Set has its own selling price.

Its price is independent from current component Product prices unless the Business explicitly defines a calculation rule.

Historical Set Orders retain the applicable Set price snapshot.

---

## 31. Set Configuration

Set composition and Set price are configuration concepts.

Changing Set composition must create a new configuration/version where the change affects operational behavior.

The new configuration becomes effective from the next Cash Session.

Historical Set sales remain associated with their previous configuration.

---

## 32. Set Component Availability

A Set can be sold only when all mandatory components are operationally available.

Availability requires:

* active Set;
* valid Set configuration;
* Branch menu availability;
* valid component configuration;
* sufficient inventory.

Component substitution is not allowed during normal sale.

---

## 33. Equipment Availability

Equipment failure is separate from pricing and menu configuration.

A Product may be temporarily unavailable because required equipment is broken.

This state must not:

* change the Product price;
* delete the Product;
* alter the Recipe;
* alter historical Orders.

---

## 34. Product Inactive State

An inactive Product cannot be newly sold.

However:

* historical Orders remain;
* historical prices remain;
* Inventory Transactions remain;
* Recipe history remains;
* Set history remains.

The system must preserve the Product identity.

---

## 35. Branch Configuration Priority

When determining the effective selling configuration for a Branch, the system evaluates:

1. Business-level Product configuration;
2. Branch-specific configuration;
3. effective configuration version;
4. Product active state;
5. Recipe/Set requirements;
6. applicable operational availability.

A Branch-specific price override takes precedence over the standard price for that Branch.

---

## 36. Configuration Version

Configuration changes that affect operational behavior must be versioned.

A configuration version should identify:

* version UUID;
* Business;
* Branch where applicable;
* affected Product/Set;
* previous version;
* creation timestamp;
* effective timestamp or session boundary;
* creator;
* status.

---

## 37. Configuration State

A configuration may exist in states such as:

```text id="cfg531"
Draft
  ↓
Approved
  ↓
Scheduled / Pending Effective
  ↓
Effective
  ↓
Superseded
```

Exact states may be simplified by implementation, but historical configuration identity must remain available.

---

## 38. Configuration Approval

Where an operation requires approval, the configuration must not become effective until required approval is completed.

Approval must be performed by an authorized employee.

The approval itself is auditable.

---

## 39. Configuration Concurrency

If two employees modify the same Product or Branch pricing configuration concurrently:

* the server validates the configuration version;
* stale updates are rejected as conflicts;
* the system must not silently overwrite a newer version.

The user must refresh and continue from current state.

---

## 40. Configuration Idempotency

Configuration-changing requests must be protected by operation UUIDs where retries are possible.

Repeated requests must not create duplicate:

* configuration versions;
* price changes;
* approvals;
* Branch overrides.

---

## 41. Offline Menu Configuration

Trusted devices may operate using the latest valid local menu configuration within their offline authorization bounds.

The device must not assume that an unavailable server configuration is current.

Offline POS operations use the last valid configuration known to the trusted device.

---

## 42. Offline Price Configuration

If a new price is created while a POS device is offline:

* the device continues using its latest valid price configuration;
* the new server price is not assumed locally;
* synchronization later updates the device configuration.

The system must not retroactively change offline-created Order prices.

---

## 43. Transaction Synchronization Priority

Transaction synchronization has priority over configuration synchronization.

For example:

```text id="syn619"
Offline Order created with Price Version A
        ↓
Order transaction synchronizes
        ↓
New Price Version B synchronizes
```

The system must preserve the original transaction price snapshot.

---

## 44. Configuration Conflict

A configuration conflict may occur if:

* two users modify the same configuration;
* an offline device has stale configuration;
* a Branch override conflicts with a newer server configuration.

The system must preserve both relevant states and explicitly resolve the conflict where required.

---

## 45. Configuration Conflict Resolution

Conflict resolution must:

* identify the conflicting versions;
* identify the resolving actor;
* record the decision;
* preserve historical values;
* create a new effective configuration if necessary;
* create an audit event.

Silent last-write-wins behavior is prohibited for important business configuration.

---

## 46. Branch Switching

When an employee changes Branch context:

* the system recalculates effective permissions;
* Branch-specific menu configuration is reloaded;
* Branch-specific price overrides are recalculated;
* previous Branch configuration is not carried over incorrectly.

A Product may therefore have different effective prices in different Branches.

---

## 47. Cross-Branch Configuration

An employee with all-Branch authority may manage configurations across multiple Branches.

The system must still identify the specific Branch affected by every Branch-scoped change.

A change intended for Branch A must never accidentally modify Branch B.

---

## 48. Product Category Changes

Changing a Product category affects current menu configuration.

The system must preserve sufficient historical context for reports that require historical categorization.

Historical Order identity remains tied to the same Product UUID.

---

## 49. Menu Change During Active Operations

A menu change must not unexpectedly invalidate an already-created Order.

For example, if a Product is disabled after being added to an open Order:

* the existing Order Item remains valid under its snapshot;
* the Product cannot be newly added to new Orders after the effective configuration applies;
* existing Order history remains unchanged.

---

## 50. Price Change During Active Operations

If the Product price changes after an Order Item is created:

* existing Order Item retains its original price;
* new Order Items use the applicable current price;
* the system must not silently recalculate the existing Order total.

---

## 51. Price Change and Payment

Payment uses the Order's authoritative current financial amount.

Changing the Product price after Order creation does not change the amount already captured in the Order snapshot.

---

## 52. Price Change and Refund

Refund calculations use the historical transaction price and financial snapshot.

Current Product price must not be used to reinterpret the original refund amount.

---

## 53. Price Change and Cancellation

Cancellation uses the historical Order state and price snapshot.

Current Product price does not modify the historical cancelled transaction.

---

## 54. Menu Configuration and Reports

Reports may need both:

* current configuration;
* historical configuration.

Historical reports must use the appropriate report snapshot and transaction snapshots.

A current menu change must not rewrite historical sales reports.

---

## 55. Menu Configuration and Audit

Important menu operations must be audited, including:

* Product activation/deactivation;
* Branch menu changes;
* category changes;
* standard price changes;
* Branch price overrides;
* Set configuration changes;
* relevant Recipe-linked configuration changes.

---

## 56. Subscription Entitlement

Menu and pricing operations are subject to subscription entitlements.

When a Business becomes read-only:

* current menu remains viewable;
* historical prices remain viewable;
* historical configurations remain available;
* modifying configuration operations are blocked;
* allowed Excel/report operations remain available.

Offline devices cannot bypass the restriction.

---

## 57. Employee Deactivation

Inactive employees cannot perform new valid menu or pricing modifications.

Historical configuration changes remain attributed to the original employee.

---

## 58. Audit Context

Audit records for menu and pricing changes should contain:

* Event UUID;
* Business UUID;
* Branch UUID where applicable;
* Product UUID;
* Set UUID where applicable;
* Employee UUID;
* Device UUID;
* old configuration;
* new configuration;
* configuration version;
* reason;
* timestamp;
* result;
* source.

Audit records are immutable.

---

## 59. Error Handling

Menu and pricing errors are classified as:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

Examples:

```text id="err811"
Invalid Price → Validation Error

Unauthorized Branch Override → Authorization Error

Stale Price Version → Conflict

Inactive Product → Business Rule Violation
```

---

## 60. Recovery

Configuration recovery uses:

* transaction rollback;
* version checks;
* idempotency;
* conflict resolution;
* immutable history;
* audit.

The system must not restore a previous configuration by deleting or overwriting historical versions.

---

## 61. Performance

Menu and pricing operations must remain fast for POS usage.

The POS must not depend on expensive historical configuration queries for normal Order creation.

Current effective configuration should be efficiently available.

Heavy historical configuration analysis should run asynchronously when required.

Configuration synchronization must not block normal POS operation.

---

## 62. System Invariants

The following invariants apply to Menu, Pricing and Configuration:

1. Global Menu is Business-scoped.
2. Branch Menu configuration is Branch-scoped.
3. Branch configuration cannot cross Business boundaries.
4. A Branch menu change does not affect another Branch unless explicitly configured.
5. Product identity remains unchanged by menu configuration changes.
6. Every Product belongs to exactly one menu category.
7. Menu availability and inventory availability are separate states.
8. Menu availability does not guarantee sufficient stock.
9. Product activation is separate from Branch menu availability.
10. Global Product configuration does not automatically make a Product sellable at every Branch.
11. Standard Product price is separate from inventory cost.
12. Branch price override affects only the selected Branch.
13. Branch price override does not change the global standard price.
14. Branch price override does not affect other Branches.
15. Historical Order prices are immutable snapshots.
16. Price changes do not rewrite existing Order Item prices.
17. Existing Open Orders retain their price snapshots.
18. Price changes do not rewrite historical payments.
19. Price changes do not rewrite historical refunds.
20. Price changes do not rewrite historical cancellations.
21. Discounts do not modify the configured Product base price.
22. Discounts are separate Order-level financial adjustments.
23. Discount application requires explicit permission.
24. Custom markup is limited to 0–100%.
25. Custom markup uses the applicable Last Purchase Cost.
26. Custom markup does not modify the standard Product price.
27. Recipe cost and selling price are separate concepts.
28. Required approved Recipe conditions must be satisfied before normal sale.
29. Recipe changes do not automatically change Product price.
30. Historical inventory deductions retain their Recipe Version.
31. Set Products have their own selling price.
32. Set composition is separate from component Recipe composition.
33. Set component substitution is prohibited during normal sale.
34. Mandatory unavailable Set components block Set sale.
35. Set price changes do not rewrite historical Set Orders.
36. Set configuration changes are versioned where operational behavior changes.
37. Configuration changes become effective according to the configured Cash Session boundary.
38. Active Cash Sessions do not silently switch operational configuration.
39. New Cash Sessions use the latest valid effective configuration.
40. Open Orders are not invalidated merely because a Product becomes inactive later.
41. Existing Order Items retain valid historical snapshots.
42. New Order Items use the applicable effective configuration.
43. Configuration changes require appropriate permission.
44. Approval is separate from editing where approval is required.
45. Stale configuration updates are rejected as conflicts.
46. Important configuration changes are protected by idempotency.
47. Offline devices use the latest valid authorized configuration available locally.
48. Offline transactions retain their original price snapshots.
49. Transaction synchronization takes priority over configuration synchronization.
50. Configuration conflicts are explicit.
51. Important configuration conflicts cannot be resolved by silent last-write-wins.
52. Conflict resolution is authorized and audited.
53. Branch switching recalculates effective menu and pricing configuration.
54. Cross-Branch changes identify the exact affected Branch.
55. Inactive employees cannot create new valid configuration changes.
56. Subscription expiry blocks modifying menu and pricing configuration.
57. Offline authorization cannot bypass subscription restrictions.
58. Historical configuration remains available after subscription expiry.
59. Important menu and pricing changes are audited.
60. Audit records are immutable.
61. Historical configuration cannot be silently overwritten.
62. Configuration correction creates a new state/version.
63. Product image changes do not alter Product identity.
64. Equipment availability does not alter Product price or Recipe history.
65. Current menu configuration cannot reinterpret historical Orders.
66. Current price cannot reinterpret historical financial transactions.
67. Current Recipe configuration cannot reinterpret historical inventory deductions.
68. Core configuration changes are atomic.
69. Secondary notification/report operations do not roll back committed configuration.
70. Menu and pricing configuration must remain attributable to the responsible actor.
71. Device context is retained for important configuration changes.
72. Server state remains authoritative after synchronization.
73. Configuration history must remain reconstructable.
74. Configuration synchronization must not block normal POS operation.
75. The system must preserve historical integrity over UI convenience.

---

## 63. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 64. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `18_Menu_Pricing_and_Configuration.md`

**Next Document:** `19_Attendance_and_Payroll.md`

