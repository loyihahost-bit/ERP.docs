# Products, Recipes and Sets

**Document ID:** SA-17
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for Products, Recipes, Recipe Versions, Semi-Finished Products and Sets.

The system must ensure that product configuration is flexible for business operations while preserving historical integrity.

The system must support:

* Raw Materials;
* Semi-Finished Products;
* Finished Products;
* product categories;
* recipes;
* recipe versions;
* recipe approval;
* recipe visibility;
* product activation;
* Set products;
* Set configuration versions;
* inventory relationships;
* historical snapshots.

---

## 2. Scope

This document covers:

* Product identity;
* Product types;
* Product categories;
* Product lifecycle;
* Product activation;
* Product archival;
* Recipe structure;
* Recipe components;
* Recipe versions;
* Recipe approval;
* Recipe permissions;
* Recipe visibility;
* Recipe effective time;
* Semi-Finished Products;
* production relationship;
* Set products;
* Set components;
* Set pricing;
* Set versions;
* historical snapshots;
* menu relationships;
* inventory relationships;
* offline configuration;
* synchronization;
* audit;
* concurrency;
* subscription restrictions;
* system invariants.

---

## 3. Product Identity

Every Product has a stable Product UUID.

The Product UUID remains unchanged throughout the Product lifecycle.

The UUID must not be reused after archival or deletion.

Products referenced by historical Orders, Recipes, Sets or Inventory Transactions must remain identifiable.

---

## 4. Product Business Context

Every Product belongs to one Business.

The system must enforce Business isolation.

A Product from one Business cannot be used by another Business.

Global product configuration is Business-scoped unless a specific system-level entity is explicitly defined otherwise.

---

## 5. Product Branch Context

Products and Recipes are managed globally at Business level.

Branches may control whether an approved global Product is available in their menu according to their permissions and configuration.

Branch-level availability does not create a new Product identity.

---

## 6. Product Types

The system supports three main Product types:

### 6.1. Raw Material

A raw inventory input such as:

* meat;
* flour;
* oil;
* mayonnaise;
* spices.

### 6.2. Semi-Finished Product

A prepared intermediate product that may be used by other Recipes.

Example:

```text id="m7q4x1"
Meat
+
Mayonnaise
+
Spices
=
Prepared Meat Mixture
```

### 6.3. Finished Product

A sellable final Product such as:

* Lavash;
* Burger;
* Pizza;
* Hotdog.

---

## 7. Product Category

Every Product belongs to exactly one menu category.

The category is part of the Product's current configuration.

A Product cannot simultaneously belong to multiple categories.

Category changes do not create a new Product identity.

Historical Order data must retain the category context required for historical reporting where applicable.

---

## 8. Product Lifecycle

A Product follows a controlled lifecycle.

Conceptually:

```text id="r5c8n2"
Created
  ↓
Active
  ↓
Inactive
  ↓
Archived
```

Not every Product must pass through every state.

A Product that has historical dependencies must not be destructively deleted.

---

## 9. Product Creation

Creating a Product requires:

* Business context;
* valid Product type;
* Product name;
* category where applicable;
* required configuration;
* authorized employee.

The system generates the Product UUID.

---

## 10. Product Activation

A Product becomes operationally sellable only when all required conditions are satisfied.

Depending on Product type and configuration, these conditions may include:

* active Product state;
* approved Recipe where required;
* active menu configuration;
* Branch availability;
* valid price;
* required components;
* sufficient stock at the relevant operation.

---

## 11. Inactive Product

An inactive Product:

* is not shown for normal sale;
* cannot be newly added to a normal Order;
* remains available in historical data;
* remains available for authorized administrative review.

Historical Orders are not changed when a Product becomes inactive.

---

## 12. Archived Product

Archived Products remain historically identifiable.

Archive is used instead of destructive deletion where historical dependencies exist.

An archived Product must not be silently removed from:

* Orders;
* Inventory Transactions;
* Recipes;
* Sets;
* Reports;
* Audit history.

---

## 13. Product Deletion

Destructive Product deletion is prohibited when historical or active dependencies exist.

If deletion is permitted for a Product with no relevant history, the system must still preserve referential integrity.

Products referenced by Recipes, Sets, Orders, Inventory Transactions or reports should be archived rather than deleted.

---

## 14. Product Price

Product price is defined separately from Recipe cost.

The standard Product price may be configured at Business level.

A Branch may have a permitted price override.

Price configuration belongs to the Product/Menu subsystem and must not rewrite historical Orders.

---

## 15. Historical Product Price

When a Product is added to an Order, the applicable price is captured in the Order snapshot.

Later price changes do not change:

* existing Order totals;
* historical Order item prices;
* completed payments;
* historical reports.

---

## 16. Product Image

A Product may have an optional image.

The image is presentation/configuration data and does not affect Product identity or inventory behavior.

Removing or changing an image does not modify historical Order data.

---

## 17. Recipe Purpose

A Recipe defines how a Product is composed from inventory components.

A Recipe may contain:

* Raw Materials;
* Semi-Finished Products;
* other permitted Product components.

The Recipe defines the required quantity and unit for each component.

---

## 18. Recipe Identity

Every Recipe has a stable Recipe UUID.

Recipe identity remains associated with the Product it belongs to.

Recipe versions have separate identities.

The Recipe UUID identifies the logical Recipe, while the Recipe Version UUID identifies a specific composition.

---

## 19. Recipe Version

Every material Recipe configuration change creates a new Recipe Version when the change affects operational composition.

A Recipe Version contains:

* Recipe Version UUID;
* Recipe UUID;
* Product UUID;
* component list;
* quantities;
* units;
* effective state;
* approval state;
* creation timestamp;
* creator;
* approval information where applicable.

Historical Recipe Versions remain immutable.

---

## 20. Recipe Components

A Recipe Component identifies:

* component Product;
* required quantity;
* unit;
* optional processing/configuration information;
* applicable Recipe Version.

Component quantities must be valid and positive.

Invalid or impossible quantities are rejected.

---

## 21. Recipe Approval

New or changed Recipes require approval before becoming normally operational.

The workflow is:

```text id="x8m2q6"
Draft Recipe
    ↓
Submitted
    ↓
Approved
    ↓
Effective
```

Rejected configurations remain historically identifiable where required.

---

## 22. Recipe Approval Permission

Only an authorized user may approve a Recipe.

Approval permission is separate from ordinary Recipe editing permission.

An employee may be allowed to edit a Recipe without being allowed to approve it.

The exact permission is determined by the effective permission model.

---

## 23. Recipe Modification Permission

Recipe modification requires appropriate permission.

The system validates:

* employee status;
* Business scope;
* Branch scope where applicable;
* role/override permission;
* subscription entitlement.

Unauthorized Recipe modifications are rejected.

---

## 24. Recipe Visibility

Recipe visibility may be restricted by permission.

An employee may be able to:

* use a Product;
* sell a Product;
* view a Recipe;
* modify a Recipe;
* approve a Recipe

as separate permission-controlled capabilities.

Access to the Product does not automatically grant access to its complete Recipe.

---

## 25. Recipe Effective Configuration

An approved Recipe Version becomes operational according to the configured effective rule.

For the current system:

**Recipe changes become effective from the next Cash Session.**

The exact transition must be deterministic.

---

## 26. Existing Cash Session

A Product sold during an active Cash Session continues to use the configuration valid for that session.

A newly approved Recipe does not silently change the Recipe used by already-active operational context.

---

## 27. New Cash Session

After a new Cash Session begins, the latest valid approved Recipe Version becomes available for normal operations if all other conditions are satisfied.

This ensures configuration changes are predictable during active POS work.

---

## 28. Historical Recipe Snapshot

When a Recipe is used in an operational transaction, the system must retain enough information to reconstruct:

* Recipe Version;
* component identities;
* quantities;
* applicable configuration;
* relevant Product context.

Historical inventory and Order calculations must not depend on mutable current Recipe configuration.

---

## 29. Recipe and Inventory

When a Finished Product is accepted for sale:

1. Applicable Recipe Version is resolved.
2. Required components are determined.
3. Current authoritative stock is checked.
4. Required stock is deducted atomically with Order acceptance.

If any required component is insufficient:

* sale is rejected;
* no partial deduction occurs.

---

## 30. Recipe and Semi-Finished Products

A Finished Product may depend on a Semi-Finished Product.

Example:

```text id="v4m7p2"
Raw Materials
      ↓
Semi-Finished Product
      ↓
Finished Product
```

The system must preserve the dependency relationship.

---

## 31. Recursive Recipe Dependencies

Recipe dependency depth must be controlled by system configuration to avoid unsafe or unbounded recursive composition.

A Recipe must not create an invalid circular dependency.

For example:

```text id="z2k5r8"
Product A
  ↓
Product B
  ↓
Product A
```

must be rejected.

The system must validate dependency graphs before a Recipe becomes effective.

---

## 32. Semi-Finished Production

A Semi-Finished Product may be produced separately.

Production:

* consumes configured input components;
* creates the Semi-Finished Product quantity;
* records actual output;
* references the applicable Recipe Version;
* creates an atomic Inventory Transaction.

The operation must not leave inputs consumed without the corresponding output.

---

## 33. Production Quantity

The system records actual produced quantity.

Theoretical Recipe quantity and actual output are separate values.

Production loss/yield is preserved as part of the production context.

---

## 34. Semi-Finished Product Sale

A Semi-Finished Product may be used as a Recipe component without necessarily being directly sellable.

Whether a Product can be sold is controlled by Product/menu configuration.

Inventory availability and Product sellability remain separate concepts.

---

## 35. Set Product

A Set is a sellable bundle consisting of predefined Products.

A Set has its own:

* Product/Set identity;
* selling price;
* active/inactive state;
* component configuration.

The Set is treated as a distinct commercial configuration.

---

## 36. Set Components

Each Set Component identifies:

* component Product;
* quantity;
* applicable Set Configuration Version.

Component substitution is not allowed during normal sale.

A customer cannot replace one Set component with another Product.

---

## 37. Set Configuration

Set composition is stored independently from the underlying current Recipe.

For example:

```text id="b6t3w9"
Set A
 ├── Burger
 ├── Fries
 └── Drink
```

Changing the Burger Recipe does not automatically change the Set composition.

---

## 38. Set Configuration Version

Changes to Set composition create a new Set Configuration Version.

The new configuration becomes effective according to the configured Cash Session effective rule.

Historical Set sales retain the configuration used at the time of sale.

---

## 39. Set Availability

A Set can be sold only when:

* Set is active;
* Set configuration is valid;
* required component Products are available;
* required inventory is sufficient;
* applicable Branch menu configuration permits the sale.

If a mandatory component is unavailable, the Set sale is blocked.

---

## 40. Set Inventory Deduction

When a Set is accepted:

* component inventory requirements are resolved;
* required inventory is validated;
* component stock is deducted atomically.

A Set sale must not partially deduct components.

---

## 41. Set Price

A Set has its own selling price.

The Set price is independent from the sum of component prices unless the business configuration explicitly calculates it that way.

Historical Set Orders retain the applicable Set price snapshot.

---

## 42. Set Price Changes

Changing a Set price does not change historical Orders.

New Orders use the latest valid price configuration for the active Cash Session.

Open Orders retain their original price snapshot.

---

## 43. Product and Set Activation

Product activation and Set activation are separate configuration states.

A Product being active does not automatically activate every Set that uses it.

Similarly, a Set being inactive does not deactivate its component Products.

---

## 44. Component Availability

Inventory availability is checked at the relevant operational transaction.

Menu availability alone does not guarantee stock availability.

A Product may be visible in the menu but unavailable for sale because required stock is insufficient.

---

## 45. Product Equipment State

Equipment failure is separate from Product activation and inventory.

A Product may be temporarily unavailable because required equipment is broken.

This state must not be interpreted as:

* Product deletion;
* Recipe deletion;
* stock depletion.

---

## 46. Product Configuration and Branches

Global Product configuration is Business-level.

Branches may configure:

* availability;
* price override;
* menu inclusion;

according to their permissions.

One Branch's price or availability configuration must not silently change another Branch's configuration.

---

## 47. Branch Price Override

A Branch price override:

* applies only to that Branch;
* requires appropriate permission;
* does not change the Business-level standard price;
* does not affect other Branches;
* does not rewrite historical Orders.

---

## 48. Menu Relationship

Products become available for sale through menu configuration.

The menu determines whether the Product is offered at a Branch.

The Product remains a Business-level entity.

---

## 49. Recipe and Menu Relationship

A Product with a required Recipe must have an approved valid Recipe before normal sale.

An approved Recipe does not automatically make the Product available at every Branch.

Menu availability remains separately controlled.

---

## 50. Recipe Change and Menu

Changing a Recipe does not automatically:

* activate the Product;
* activate the Product in every Branch;
* change Product price;
* change Set composition.

The Recipe configuration affects inventory consumption when its effective version becomes operational.

---

## 51. Recipe Change and Historical Orders

Historical Orders retain their original:

* Product;
* selling price;
* Recipe context where required;
* quantity;
* inventory transaction context.

A current Recipe change must not rewrite historical Orders.

---

## 52. Recipe Change and Historical Inventory

Historical inventory deductions retain the Recipe Version used for the transaction.

Current Recipe configuration is not used to reinterpret old inventory movements.

---

## 53. Product Archive

When a Product has historical or configuration dependencies, it should be archived instead of deleted.

Archive preserves:

* Product identity;
* historical Orders;
* inventory movements;
* Recipes;
* Sets;
* reports;
* audit history.

---

## 54. Archived Recipe

Old Recipe Versions are retained.

An obsolete Recipe Version may no longer be operational but remains available for historical reconstruction.

A historical Recipe Version must not be modified.

---

## 55. Recipe Approval History

Recipe approval history must record:

* Recipe Version;
* creator;
* approver;
* approval timestamp;
* approval result;
* relevant reason/comment;
* Business;
* applicable scope.

The approval record is immutable.

---

## 56. Set Approval and Configuration

Set configuration changes follow the same historical integrity principles.

A configuration change must preserve:

* previous configuration;
* new configuration;
* creator;
* effective configuration;
* relevant approval or authorization;
* timestamp.

Where approval is required by configured permissions, the new configuration remains non-effective until approved.

---

## 57. Offline Product Configuration

Trusted devices may continue operating with the latest valid configuration available locally.

If a new Product, Recipe or Set configuration is created while the device is offline:

* the device does not invent a new authoritative configuration;
* synchronization reconciles the configuration with server state.

---

## 58. Configuration Synchronization

Configuration synchronization follows the system-wide synchronization rules.

The system must preserve:

* configuration UUID;
* version;
* effective state;
* creation time;
* approval state.

Transaction synchronization has priority over configuration synchronization.

This prevents a configuration update from being applied before dependent transaction events are safely synchronized.

---

## 59. Offline Configuration Version

An offline device may continue using the last valid configuration available to it within its authorization bounds.

It must not use:

* expired configuration authority;
* unauthorized Recipe;
* unapproved Recipe;
* unauthorized Branch configuration.

---

## 60. Product Configuration Conflicts

A configuration conflict may occur when offline and server changes affect the same configuration.

The system must not silently overwrite one configuration with another.

The conflict must preserve:

* local version;
* server version;
* conflict reason;
* actor;
* timestamp;
* resolution.

---

## 61. Configuration Conflict Resolution

Only an authorized user may resolve a configuration conflict.

Resolution creates a separate auditable event.

Historical configurations remain available.

---

## 62. Product and Recipe Permissions

The system must distinguish permissions for:

* Product creation;
* Product editing;
* Product activation/deactivation;
* Product archival;
* Recipe viewing;
* Recipe editing;
* Recipe submission;
* Recipe approval;
* Set creation;
* Set editing;
* Set activation;
* Set archival.

The exact permission assignment is controlled by the general permission model.

---

## 63. Employee Status

Inactive employees cannot create new valid Product, Recipe or Set configuration changes.

Previously approved configurations remain valid.

Historical configuration changes remain attributable to the original employee.

---

## 64. Subscription Entitlement

Product, Recipe and Set operations are subject to subscription entitlement.

If the Business loses access to a feature:

* historical configuration remains;
* historical transactions remain;
* new modifying operations using the unavailable feature are blocked.

Read-only access follows subscription lifecycle rules.

---

## 65. Configuration Concurrency

Two authorized employees may attempt to modify the same Product, Recipe or Set configuration.

The system must use appropriate concurrency protection.

A stale configuration update must not silently overwrite a newer version.

The operation must either:

* apply to the current version; or
* be rejected as a version conflict.

---

## 66. Configuration Idempotency

Configuration-changing operations that may be retried must use stable operation UUIDs.

Duplicate requests must not create:

* duplicate Products;
* duplicate Recipe Versions;
* duplicate Set Configurations;
* duplicate approvals.

---

## 67. Product and Recipe Audit

Important configuration operations must be audited.

Audit events include:

* Product creation;
* Product edit;
* Product activation/deactivation;
* Product archive;
* Recipe creation;
* Recipe modification;
* Recipe submission;
* Recipe approval/rejection;
* Set creation;
* Set modification;
* Set activation/deactivation;
* configuration conflict resolution.

---

## 68. Historical Integrity

The following objects are treated as immutable historical records once operationally effective:

* historical Product price snapshots;
* Recipe Versions;
* Set Configuration Versions;
* Inventory Transactions;
* relevant Order snapshots;
* approval records.

Corrections create new records instead of modifying historical records.

---

## 69. Error Handling

Product, Recipe and Set errors are classified as:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

Examples:

```text id="a2n7m4"
Missing Recipe → Validation / Business Rule Violation

Unauthorized Recipe Approval → Authorization Error

Circular Recipe Dependency → Business Rule Violation

Stale Configuration Version → Conflict
```

---

## 70. Recovery

Configuration recovery relies on:

* immutable versions;
* transaction rollback;
* idempotency;
* version checks;
* conflict resolution;
* audit history.

The system must not repair configuration by silently rewriting historical versions.

---

## 71. Performance

Product and Recipe configuration must remain practical for normal restaurant operations.

Operational POS flows must not depend on expensive historical Recipe queries.

Frequently used configuration should be available through efficient current-state access while historical versions remain separately retrievable.

Heavy configuration reports or dependency analysis should run asynchronously where necessary.

---

## 72. System Invariants

The following invariants apply to Products, Recipes and Sets:

1. Every Product has a stable Product UUID.
2. Product identity is Business-scoped.
3. Cross-Business Product access is prohibited.
4. Branch configuration does not create a new Product identity.
5. A Product belongs to exactly one menu category.
6. Product type is explicitly defined.
7. Supported Product types are Raw Material, Semi-Finished Product and Finished Product.
8. Product activation is separate from menu availability.
9. Product inactivity does not delete historical data.
10. Products with historical dependencies are archived rather than destructively deleted.
11. Historical Product identity remains reconstructable.
12. Product price is separate from Recipe cost.
13. Historical Order prices are immutable snapshots.
14. Price changes do not rewrite existing Orders.
15. Every logical Recipe has a stable Recipe UUID.
16. Every operational Recipe composition has a Recipe Version.
17. Recipe Versions are immutable once used operationally.
18. Recipe component quantities must be valid.
19. Recipe modifications require appropriate permission.
20. Recipe approval requires separate authorization where configured.
21. Editing permission does not automatically imply approval permission.
22. Recipe visibility may be restricted independently from Product visibility.
23. Unapproved Recipe configurations are not used for normal sale.
24. Recipe changes become effective from the next Cash Session.
25. Existing operational context is not silently rewritten by configuration changes.
26. Historical transactions retain their applicable Recipe Version.
27. Current Recipe configuration cannot reinterpret historical inventory movements.
28. Recipe dependencies must not contain circular references.
29. Semi-Finished Products may be used as Recipe components.
30. Semi-Finished production consumes inputs and creates output atomically.
31. Actual production output is recorded separately from theoretical output.
32. Production loss/yield remains traceable.
33. A Semi-Finished Product is not automatically sellable merely because it exists.
34. A Set is a distinct sellable configuration.
35. A Set has its own identity and selling price.
36. Set component substitution is not allowed during normal sale.
37. Set composition is independent from current component Recipe composition.
38. Set configuration changes create new versions.
39. Set configuration changes become effective according to the configured Cash Session rule.
40. Historical Set sales retain their applicable configuration.
41. Mandatory unavailable Set components block the sale.
42. Set inventory deduction is atomic.
43. Set price changes do not rewrite historical Orders.
44. Open Orders retain their price snapshots.
45. Product activation does not automatically activate Sets.
46. Set inactivity does not deactivate component Products.
47. Menu availability does not guarantee inventory availability.
48. Equipment failure is separate from Product activation and stock state.
49. Branch price overrides affect only the configured Branch.
50. Branch price overrides do not change Business-level standard price.
51. Branch configuration changes do not silently affect other Branches.
52. Required approved Recipe must exist before normal sale where applicable.
53. Recipe changes do not automatically change Product price.
54. Recipe changes do not automatically change Set composition.
55. Historical Products, Recipes and Sets remain identifiable.
56. Historical Recipe Versions are immutable.
57. Approval history is immutable.
58. Offline devices use the latest valid authorized configuration available locally.
59. Offline devices cannot invent authoritative configuration.
60. Transaction synchronization takes priority over configuration synchronization.
61. Configuration conflicts are explicit.
62. Configuration conflicts cannot silently overwrite server state.
63. Configuration conflict resolution is authorized and audited.
64. Inactive employees cannot create new valid configuration changes.
65. Subscription entitlement controls modifying configuration operations.
66. Historical configuration remains available after entitlement loss.
67. Concurrent configuration changes are protected by version/concurrency control.
68. Duplicate configuration requests cannot create duplicate versions.
69. Important Product, Recipe and Set changes are audited.
70. Historical configuration cannot be silently overwritten.
71. Corrections create new records rather than rewriting historical records.
72. Product, Recipe and Set configuration must remain Business and Branch scoped where applicable.
73. Product configuration must remain attributable to the responsible employee.
74. Device context is retained for important configuration changes.
75. System-generated changes use SYSTEM actor where applicable.
76. Configuration failures must not leave partially committed versions.
77. Operational Product sale must use one valid effective configuration.
78. Inventory deduction must use the same applicable Recipe/Set configuration that was resolved for the transaction.
79. Historical configuration must remain sufficient to reconstruct the original business operation.
80. Configuration changes must not silently alter previously committed financial or inventory results.

---

## 73. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
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

## 74. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `17_Products_Recipes_and_Sets.md`

**Next Document:** `18_Menu_Pricing_and_Configuration.md`

