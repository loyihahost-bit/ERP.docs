# Menu and Pricing Domain

**Document ID:** DA-10
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Menu and Pricing domain manages the business-facing product catalog and its selling configuration.

It is responsible for:

* products;
* categories;
* recipes;
* recipe versions;
* Sets;
* global menu;
* Branch menu availability;
* standard prices;
* Branch price overrides;
* product activation;
* product configuration;
* configuration versions;
* effective dates/states;
* pricing history;
* menu configuration history;
* product availability configuration.

The domain does not own:

* current stock quantities;
* Orders;
* Payments;
* Cash Sessions;
* Employees;
* Reports;
* Notifications.

Those domains consume Menu and Pricing information through explicit boundaries.

---

# 2. Domain Scope

The logical hierarchy is:

```text id="m7q3v8"
Business
   ↓
Global Catalog
   ├── Categories
   ├── Products
   ├── Recipes
   └── Sets
         ↓
Branch Menu
         ↓
Branch Pricing
         ↓
POS Configuration
```

The Business owns the global product configuration.

Branches determine which globally available products are enabled locally.

---

# 3. Product

A Product is a sellable or recipe-related business item.

A Product has a stable UUID.

A Product may represent:

* a finished product;
* a semi-finished product;
* another inventory-related product;
* a Set/bundle where explicitly configured.

Product identity must remain stable across configuration changes.

---

# 4. Product Category

Every Product belongs to exactly one menu category.

The category relationship is mandatory for menu organization.

A Product must not simultaneously belong to multiple categories under the current model.

Category changes must preserve historical configuration.

---

# 5. Product Identity vs Configuration

Product identity and product configuration are separate concepts.

The Product identity remains stable while configuration may change.

Configuration may include:

* name;
* category;
* image;
* standard price;
* recipe reference;
* availability;
* menu state;
* other approved business configuration.

Historical transactions preserve the configuration relevant at their creation.

---

# 6. Product Image

A Product may have an optional image.

Image presence is not required for the Product to be sellable.

Removing or replacing an image must not change Product identity.

---

# 7. Global Menu

The Global Menu represents the Business-level product catalog.

A global Product may be made available to Branches according to business configuration.

The Global Menu does not automatically mean that every Branch currently sells the Product.

---

# 8. Branch Menu

A Branch Menu determines which global Products are available in a particular Branch.

Conceptually:

```text id="n4r8c2"
Global Product
      ↓
Branch Menu Configuration
      ↓
Enabled / Disabled
```

A Branch may disable a global Product without deleting it.

---

# 9. Product Inactivation

A Product may become inactive.

An inactive Product:

* is hidden from normal selling interfaces;
* cannot be sold as a new product;
* remains in historical Orders;
* remains available for historical reporting;
* does not lose its identity.

Inactive is not equivalent to deleted.

---

# 10. Archive Principle

Products with historical or recipe dependencies must not be destructively deleted.

Where business history or dependencies exist, the domain uses:

```text id="p6v2m9"
Active
   ↓
Inactive / Archived
```

Historical references remain valid.

---

# 11. Recipe Relationship

A Product may reference a Recipe.

The Recipe defines the components required to produce or sell the Product.

The Menu and Pricing domain owns the Product-to-Recipe configuration relationship.

Inventory owns the resulting stock movements.

---

# 12. Recipe Versions

Recipe changes create a new logical version.

Historical recipe versions remain identifiable.

A recipe version must preserve enough information to reconstruct the configuration used by historical transactions.

---

# 13. Recipe Approval

New or changed recipes require approval according to established business rules.

The approval state is part of configuration lifecycle.

An unapproved recipe must not silently become the active selling recipe.

---

# 14. Recipe Effective Time

Approved recipe changes become effective from the next Cash Session.

An already active Cash Session continues using the valid configuration that applied when it started.

This prevents mid-session configuration changes from creating inconsistent Orders.

---

# 15. Price Configuration

Pricing consists of:

```text id="c8m3q7"
Global Standard Price
        ↓
Optional Branch Price Override
        ↓
Effective POS Price
```

The standard price is Business-level.

A Branch may override the standard price when the required permission exists.

---

# 16. Branch Price Override

A Branch price override:

* applies only to that Branch;
* does not modify the global standard price;
* requires appropriate permission;
* is historically recorded;
* becomes effective according to configuration timing rules.

One Branch's override must not affect another Branch.

---

# 17. Price Effective Time

Price changes become effective from the next Cash Session.

The active Cash Session continues using its valid configuration.

This avoids changing selling prices unexpectedly in the middle of a cashier session.

---

# 18. Order Price Snapshot

When a Product is added to an Order, the applicable selling price is captured in the Order context.

Later price changes do not rewrite existing Order prices.

Conceptually:

```text id="v2p8n4"
Price Configuration
       ↓
Order Creation
       ↓
Price Snapshot
```

---

# 19. Historical Price Integrity

Historical Orders must remain reconstructable using their original price information.

Changing the current Product price must not alter:

* completed Orders;
* unpaid existing Order items;
* historical reports;
* historical refunds.

---

# 20. Discounts

Discounts are separate from base pricing.

A discount modifies the transaction amount without rewriting the Product's configured price.

The domain may expose discount configuration to the Order/Payment domains.

Discount authorization remains permission-controlled.

---

# 21. Custom Markup

The system supports custom Order-level markup where authorized.

The markup range is:

```text id="j5r9q3"
0% ≤ Markup ≤ 100%
```

The calculation uses Last Purchase Cost.

Conceptually:

```text id="u7m2k6"
Final Price
=
Last Purchase Cost
×
(1 + Markup / 100)
```

The resulting custom price is an Order-level value and does not silently modify the standard Product price.

---

# 22. Set

A Set is a bundle of Products sold under its own configuration.

A Set has:

* stable UUID;
* own selling price;
* component configuration;
* active/inactive state;
* configuration version.

Set components are not freely swappable at sale time under the current business rules.

---

# 23. Set Component Integrity

Mandatory Set components cannot be replaced by another Product during normal sale.

If a required component is unavailable:

* the Set sale is blocked;
* the system does not silently substitute another Product.

---

# 24. Set and Inventory

A Set sale causes inventory consumption according to its configured component Products.

The Menu and Pricing domain defines the Set composition.

Inventory determines the resulting stock consumption.

---

# 25. Set Configuration Versioning

Changes to Set composition create a new configuration/version.

The new Set configuration becomes effective from the next Cash Session.

An active Cash Session continues using the previous valid configuration.

---

# 26. Recipe vs Set

Recipe and Set are different concepts.

### Recipe

Defines how a Product is produced/consumes ingredients.

### Set

Defines a bundle of sellable Products.

Therefore:

```text id="a6w9p3"
Set
 ├── Product A
 ├── Product B
 └── Product C

Product A
 └── Recipe
      └── Ingredients
```

The two relationships must not be collapsed into one concept.

---

# 27. Configuration State

Menu/Pricing configuration may conceptually have states such as:

```text id="x3q7m8"
Draft
Pending Approval
Approved
Active
Inactive
Archived
```

Not every configuration type must use every state.

The exact state machine is finalized during Architecture/Database analysis.

---

# 28. Configuration Priority

When determining an effective Branch selling configuration, the logical priority is:

```text id="r8m4v2"
Approved Global Configuration
        ↓
Branch Override
        ↓
Effective Branch Configuration
```

Invalid or unauthorized overrides must not become effective.

---

# 29. Configuration Snapshot

Operational transactions must use a valid configuration snapshot.

The snapshot may reference:

* Product version;
* Recipe version;
* Set version;
* price version;
* Branch configuration;
* effective Cash Session.

This allows historical reconstruction.

---

# 30. Configuration Concurrency

Configuration updates must be concurrency-safe.

If two authorized users modify the same configuration concurrently, the system must prevent silent lost updates.

Possible implementation mechanisms include:

* version checks;
* optimistic concurrency;
* serialized configuration updates.

The exact mechanism belongs to Architecture/Database analysis.

---

# 31. Latest Command Wins

Where business rules explicitly allow sequential permissioned configuration changes, the latest successfully committed command becomes the current configuration.

However, concurrent stale writes must not silently overwrite newer state.

The server remains authoritative.

---

# 32. Offline Menu Configuration

Trusted devices may retain the latest valid configuration for offline operation.

Offline devices continue using their last valid synchronized configuration.

They must not invent a newer configuration locally without authorization.

---

# 33. Offline Price Configuration

Offline POS operation may continue using the last valid price configuration available to the trusted device.

A newly synchronized price does not retroactively modify existing Orders.

New configuration becomes available according to synchronization and Cash Session activation rules.

---

# 34. Configuration Synchronization Order

When synchronization occurs:

```text id="k9v3m7"
Transaction Sync
      ↓
Configuration Sync
```

Pending operational transactions must be processed before newer configuration changes where required by dependency rules.

This prevents a configuration update from incorrectly rewriting an older offline transaction.

---

# 35. Configuration Conflict

If an offline configuration operation conflicts with a newer server configuration:

* the server remains authoritative;
* the conflicting operation is preserved;
* a conflict may be created;
* authorized resolution is required;
* no silent overwrite is allowed.

---

# 36. Branch Switching

When a user switches Branch context, the effective configuration must be recalculated using:

* selected Business;
* selected Branch;
* employee permissions;
* role/override permissions;
* subscription entitlement;
* Branch menu state;
* current valid configuration.

A configuration from one Branch must not leak into another Branch.

---

# 37. Permission Boundary

Menu and pricing operations require explicit permissions where applicable.

Examples include:

* creating Product;
* editing Product;
* changing price;
* changing Branch price;
* modifying Recipe;
* approving Recipe;
* modifying Set;
* activating/inactivating Product.

Possessing access to the menu screen alone does not grant modification authority.

---

# 38. Subscription Boundary

Menu and Pricing operations are subject to subscription entitlements.

When subscription restrictions apply:

* existing configuration remains preserved;
* read-only access may remain available;
* modifying operations are blocked.

Subscription expiry must not delete Product history.

---

# 39. Product Availability

Product availability may depend on:

* Product active state;
* Branch menu state;
* approved configuration;
* equipment availability;
* subscription entitlement;
* employee permission.

These conditions must be evaluated without rewriting Product identity.

---

# 40. Equipment Availability

If equipment required for a Product becomes unavailable, the Product may be manually marked unavailable.

This does not:

* delete the Product;
* modify historical Orders;
* modify historical prices;
* modify inventory quantities.

---

# 41. Menu and Order Boundary

The Menu and Pricing domain supplies the configuration required to create an Order.

Once an Order item is created, the relevant selling configuration is captured by the Order domain.

Later menu changes do not rewrite the existing Order.

---

# 42. Menu and Inventory Boundary

Menu/Pricing defines:

* Product;
* Recipe;
* Set;
* component relationships.

Inventory defines:

* stock quantity;
* stock movements;
* availability from actual stock.

A Product can exist before stock exists.

Creating a Product does not require immediate inventory.

---

# 43. Menu and Payment Boundary

Payment uses the final Order amount.

Payment does not independently determine:

* Product price;
* Recipe price;
* Branch override.

Those values originate from Order configuration and snapshots.

---

# 44. Menu and Reports

Reports may use:

* current Product configuration;
* historical Product snapshots;
* price history;
* menu availability;
* recipe versions;
* Set versions.

The Report domain determines reporting representation.

Menu/Pricing remains authoritative for configuration history.

---

# 45. Menu and Notifications

Menu/Pricing may generate conditions requiring notification, such as:

* approval pending;
* important configuration changes;
* product availability changes.

Notification lifecycle remains owned by the Notification domain.

---

# 46. Aggregate Boundaries

The Menu and Pricing domain should conceptually contain:

* Product;
* Category;
* Recipe Configuration;
* Recipe Version;
* Set;
* Global Menu Configuration;
* Branch Menu Configuration;
* Price Configuration;
* Branch Price Override;
* Configuration Version.

It should not contain:

* Inventory quantity;
* Order;
* Payment;
* Cash Session;
* Employee;
* Report;
* Notification.

---

# 47. Domain Services

Potential domain services include:

```text id="w5q8n2"
Product Configuration Service
Menu Activation Service
Branch Menu Service
Recipe Approval Service
Set Configuration Service
Price Configuration Service
Branch Price Override Service
Effective Configuration Resolver
Configuration Version Service
Configuration Conflict Resolver
```

These are logical domain services, not necessarily separate applications.

---

# 48. Domain Events

Potential events include:

```text id="p3m7x1"
ProductCreated
ProductActivated
ProductDeactivated
ProductArchived
RecipeCreated
RecipeApproved
RecipeConfigurationChanged
SetCreated
SetConfigurationChanged
MenuConfigurationChanged
BranchProductEnabled
BranchProductDisabled
PriceChanged
BranchPriceOverrideChanged
ConfigurationConflictDetected
```

Events represent facts that have already occurred.

---

# 49. Menu and Pricing Invariants

### Product Identity

1. Every Product has a stable UUID.
2. Product identity does not change when configuration changes.
3. Every Product belongs to exactly one Category.
4. Product history remains identifiable.
5. Product deletion must not destroy required historical references.

### Categories

6. A Product cannot belong to multiple categories simultaneously.
7. Category changes preserve historical configuration.
8. Category configuration is Business-scoped.

### Global Menu

9. Global Menu configuration belongs to a Business.
10. A global Product may be enabled or disabled per Branch.
11. Branch menu state does not modify the global Product itself.
12. Branch A configuration cannot modify Branch B configuration.

### Products

13. Inactive Products cannot be sold as new Products.
14. Inactive Products remain available for historical records.
15. Product image is optional.
16. Product configuration changes preserve historical state.

### Recipes

17. Recipe configuration belongs to the Product/Recipe model.
18. Recipe versions are historically identifiable.
19. Recipe changes require required approval.
20. Unapproved Recipe configuration cannot silently become active.
21. Recipe changes become effective according to Cash Session configuration rules.
22. Historical Orders are not rewritten by Recipe changes.

### Sets

23. Every Set has a stable identity.
24. Set composition is versioned.
25. Mandatory Set components cannot be silently substituted.
26. Set sale uses the active Set configuration.
27. Set configuration changes become effective according to Cash Session rules.
28. Historical Orders retain the applicable Set configuration.

### Pricing

29. Global standard price is Business-scoped.
30. Branch price override affects only its Branch.
31. Branch price override requires applicable permission.
32. Price changes become effective according to Cash Session rules.
33. Existing Order prices are not rewritten by later price changes.
34. Historical prices remain reconstructable.
35. Discounts do not rewrite base Product price.
36. Custom markup does not silently change the standard Product price.
37. Custom markup is limited to 0–100%.

### Configuration

38. Approved configuration is required before becoming active where approval is required.
39. Effective configuration is resolved from valid Business/Branch context.
40. Configuration versions remain historically identifiable.
41. Concurrent stale configuration updates must not silently overwrite newer state.
42. Latest successfully committed valid command determines current state where sequential changes are allowed.
43. Invalid configuration cannot become active.

### Offline

44. Offline devices use the latest valid synchronized configuration.
45. Offline devices cannot bypass permission requirements.
46. Offline price changes remain subject to authorization.
47. Offline configuration retains stable identity.
48. Configuration synchronization is idempotent.
49. Configuration conflicts are explicitly represented.
50. Server configuration remains authoritative.

### Operational Sessions

51. Active Cash Sessions use their valid configuration snapshot.
52. New configuration does not retroactively change existing Orders.
53. Price changes do not rewrite existing Order items.
54. Recipe changes do not rewrite existing Order configuration.
55. Set changes do not rewrite existing Order configuration.

### Security and Scope

56. Menu modifications require authentication.
57. Menu modifications require applicable permission.
58. Business scope is validated.
59. Branch scope is validated.
60. Subscription entitlement is validated for modifying operations.
61. Trusted-device authorization is validated for offline changes.

### History

62. Price history is preserved.
63. Recipe history is preserved.
64. Set configuration history is preserved.
65. Branch menu history is preserved.
66. Product activation history is preserved.
67. Configuration changes remain auditable.
68. Historical Orders remain reconstructable.

---

# 50. Completion Criteria

The Menu and Pricing domain is considered complete when:

* Product identity is defined;
* Category ownership is defined;
* Global Menu is defined;
* Branch Menu is defined;
* Product activation/inactivation is defined;
* Recipe relationship is defined;
* Recipe versioning is defined;
* Set composition is defined;
* Set versioning is defined;
* global pricing is defined;
* Branch price overrides are defined;
* price snapshots are defined;
* discount boundary is defined;
* custom markup is defined;
* Cash Session configuration timing is defined;
* offline configuration is defined;
* synchronization/conflict boundaries are defined;
* permission and subscription boundaries are defined;
* historical integrity is defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous Domain Documents

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

