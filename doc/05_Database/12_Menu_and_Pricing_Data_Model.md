# Menu and Pricing Data Model

**Document ID:** DB-12
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Business-level menu;
* Product menu availability;
* Branch-specific menu configuration;
* Standard product pricing;
* Branch price overrides;
* Set pricing;
* price versions;
* effective configuration boundaries;
* historical price integrity;
* order price snapshots.

The database model must preserve historical transaction data and prevent current pricing changes from silently modifying previously created orders.

---

## 2. Design Principles

The database model follows these principles:

1. Menu configuration belongs to the Business.
2. Branches decide which Business products are available.
3. Pricing and menu availability are separate concerns.
4. Historical prices must never be overwritten.
5. Price changes create new effective versions.
6. Existing orders retain their original price snapshots.
7. Price changes become operationally effective from the next Cash Session.
8. Cashiers cannot directly modify standard product prices.
9. Discounts are separate from base prices.
10. Branch price overrides require permission.
11. Configuration changes must be auditable.
12. Offline devices use the latest valid synchronized configuration.
13. Database constraints must prevent invalid price states.
14. Historical versions remain available while referenced by transactions.
15. Current configuration must be efficiently queryable.

---

## 3. Business Ownership

All menu and pricing records are Business-scoped.

Conceptually:

```text
Business
 ├── Categories
 ├── Products
 ├── Menu Products
 ├── Price Definitions
 ├── Price Versions
 ├── Branch Menu Configuration
 └── Branch Price Overrides
```

A menu or price record from one Business must never be usable by another Business.

Business identity is established through authenticated server-side context.

Client-provided Business IDs must not be trusted as authorization.

---

## 4. Menu Product Model

The Product entity is defined by:

`08_Product_and_Category_Data_Model.md`

The menu model determines whether a Product is currently available for sale.

A Product may exist in the catalog without being active in the menu.

Example:

```text
Product
    ↓
Catalog Product
    ↓
Menu Availability
    ↓
Branch Availability
    ↓
Sellable Product
```

A Product being active in the catalog does not automatically mean it is sellable in every Branch.

---

## 5. Business Menu

The Business Menu represents the Business-level menu configuration.

A Business Menu entry may reference:

* Product;
* category;
* active state;
* display order;
* effective configuration version.

Conceptual fields:

```text
BusinessMenuItem
----------------
id
business_id
product_id
display_order
status
configuration_version
created_at
updated_at
```

The exact implementation may use a dedicated configuration/version table rather than storing mutable configuration directly on the menu item.

---

## 6. Product Uniqueness

A Product should not appear more than once as an active Business Menu item unless the system explicitly supports multiple menu presentations.

Default invariant:

```text
Business + Product = one logical menu entry
```

Historical configuration versions may contain multiple records over time, but only one configuration version is active for a given Product at a given effective boundary.

---

## 7. Branch Menu Availability

Branches may independently enable or disable Business-level products.

Conceptual model:

```text
Business Product
       ↓
Branch Menu Configuration
       ↓
Enabled / Disabled
```

Suggested fields:

```text
BranchMenuItem
--------------
id
business_id
branch_id
product_id
enabled
configuration_version
effective_from_session_id
created_at
updated_at
```

The exact schema may represent this through immutable configuration versions.

---

## 8. Branch Isolation

A Branch Menu Item must satisfy:

```text
branch.business_id = menu_item.business_id
product.business_id = menu_item.business_id
```

A Branch must never enable a Product belonging to another Business.

Cross-tenant menu references are forbidden.

---

## 9. Product Availability

A Product is sellable only when all required conditions are satisfied.

Conceptually:

```text
Product Active
        AND
Business Menu Active
        AND
Branch Menu Enabled
        AND
Valid Price Exists
        AND
Required Recipe/Stock Conditions Satisfied
```

Inventory availability is validated separately during Order acceptance.

Menu availability must not be treated as proof that stock is sufficient.

---

## 10. Price Model

The system distinguishes between:

* standard Business price;
* Branch-specific price override;
* Set price;
* discount;
* order-level price snapshot.

These must not be stored as one mutable price field.

---

## 11. Standard Product Price

A Product may have a Business-level standard selling price.

Conceptual model:

```text
Product
   ↓
Standard Price
   ↓
Price Version
```

Suggested fields:

```text
ProductPrice
------------
id
business_id
product_id
currency
created_at
```

```text
ProductPriceVersion
-------------------
id
product_price_id
version
amount
status
effective_from_session_id
created_by
created_at
```

Historical price versions are immutable.

---

## 12. Monetary Representation

All monetary values must use an exact fixed-precision database type.

Floating-point types must not be used for financial values.

The database must define a consistent precision and scale appropriate for the Business currency.

Example conceptual type:

```text
NUMERIC(precision, scale)
```

The exact precision/scale is defined centrally by the database architecture and migration standards.

---

## 13. Price Validation

Price values must satisfy:

```text
amount >= 0
```

Negative standard selling prices are not allowed.

A zero price may be allowed for explicitly configured products or controlled promotional scenarios.

Such use must not bypass permission and audit requirements.

---

## 14. Branch Price Override

A Branch may have a price different from the Business standard price.

Conceptual model:

```text
Business Standard Price
          ↓
Branch Price Override
          ↓
Effective Branch Price
```

Suggested fields:

```text
BranchPriceOverride
-------------------
id
business_id
branch_id
product_id
price_version_id
amount
effective_from_session_id
created_by
created_at
```

Branch overrides are Business- and Branch-scoped.

---

## 15. Branch Override Permission

Creating or changing a Branch Price Override requires an appropriate permission.

A Cashier must not directly modify the standard price or branch override unless explicitly granted the relevant permission.

Price changes must pass through the normal authorization model:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

---

## 16. Effective Price

The effective price for a Branch is resolved deterministically.

Default priority:

```text
Branch Price Override
        ↓
Business Standard Price
```

If no valid Branch override exists, the Business standard price is used.

An inactive or expired price version must not be selected as the current price.

---

## 17. Price Versioning

Price changes must not overwrite the previous price.

Example:

```text
Product A

Version 1 → 25,000
Version 2 → 27,000
Version 3 → 29,000
```

Each version is immutable.

The active version is selected using its effective configuration boundary.

---

## 18. Cash Session Activation Boundary

Price changes become operationally effective from the next Cash Session.

Example:

```text
Cash Session #101
Price = 25,000

Price changed
        ↓

Cash Session #101 continues with 25,000

Cash Session #102
Price = 27,000
```

This prevents a price change from unexpectedly changing the operating configuration during an active session.

---

## 19. Existing Orders

An existing Order must retain its original selling price.

Changing the current Product price must not modify:

* existing Order Item price;
* existing Order total;
* paid amount;
* historical reports.

The Order Item stores a historical price snapshot.

---

## 20. Order Price Snapshot

The Order database model must preserve at least:

```text
unit_price
quantity
discount_amount
line_total
```

It should also retain enough configuration identity to reconstruct the pricing source.

Conceptual references may include:

```text
product_id
price_version_id
branch_price_override_id
```

References to current configuration must never be required to reconstruct historical transaction values.

---

## 21. Price Snapshot Rule

Historical Order pricing is authoritative from the Order Item snapshot.

The current Product price is not used to recalculate historical orders.

Therefore:

```text
Current Product Price != Historical Order Item Price
```

is valid and expected.

---

## 22. Set Pricing

Sets have their own selling price.

A Set price is independent from the sum of its component Product prices.

Example:

```text
Component Products
        ↓
Set Composition

Component total = 70,000
Set selling price = 60,000
```

The Set may intentionally have a different selling price.

---

## 23. Set Price Versioning

Set prices follow the same historical versioning principles.

Conceptually:

```text
Set
 ↓
Set Price
 ↓
Set Price Version
```

Set price changes become effective according to the same Cash Session boundary.

Existing Set orders retain their historical Set price.

---

## 24. Recipe and Pricing Relationship

Recipes determine production/consumption relationships.

Recipes do not directly define the final selling price.

Therefore:

```text
Recipe
    ↓
Production / Consumption

Price
    ↓
Selling Value
```

A recipe change must not silently rewrite the selling price.

A Business may intentionally change the selling price through the pricing configuration.

---

## 25. Last Purchase Cost

The Product's Last Purchase Cost is derived from inventory purchasing activity.

It is not the same as:

* selling price;
* branch selling price;
* discount;
* Set price.

Conceptually:

```text
Purchase
   ↓
Last Purchase Cost

Product Price
   ↓
Selling Price
```

The exact Last Purchase Cost storage/derivation is governed by the Inventory Data Model.

---

## 26. Custom Order Markup

The system may support a controlled custom markup for authorized order operations.

Default rule:

```text
Final Price =
Last Purchase Cost × (1 + Markup / 100)
```

Markup must satisfy:

```text
0 <= markup <= 100
```

The markup is an order-time pricing adjustment and must not silently modify the standard Product price.

The applied markup and resulting price must be stored in the Order Item snapshot.

---

## 27. Discounts

Discounts are separate from Product Price.

Conceptually:

```text
Base Price
   ↓
Discount
   ↓
Final Line Amount
```

A discount must not rewrite the Product Price Version.

Historical orders store the applied discount information.

Discount authorization and limits are defined by the Payment/Discount business and system models.

---

## 28. Price Change History

Every price change must preserve:

* previous version;
* new version;
* actor;
* Business;
* Branch if applicable;
* effective Cash Session;
* timestamp;
* reason when required.

The original version must remain immutable.

Audit events reference the price/configuration change but do not replace the price history itself.

---

## 29. Configuration Version

Menu and pricing configuration may share a broader configuration version mechanism.

Conceptually:

```text
Configuration Version
        ↓
Menu
Pricing
Branch Availability
Recipe
Set
Printer
Notification Thresholds
```

The exact implementation must preserve domain-specific historical identity while allowing consistent activation boundaries.

---

## 30. Configuration Lifecycle

Menu and pricing configurations may use the common configuration lifecycle:

```text
Draft
  ↓
Pending Approval
  ↓
Approved
  ↓
Active
  ↓
Inactive
  ↓
Archived
```

Not every configuration change requires every intermediate state.

The applicable workflow depends on the operation and permission model.

---

## 31. Configuration Approval

Changes requiring approval must not become operational before approval.

An unapproved price or menu configuration must not be used by:

* POS;
* offline transactions;
* order acceptance;
* reports as current configuration.

Historical records may reference previously approved versions.

---

## 32. Offline Pricing

Trusted offline devices use the latest valid synchronized menu/pricing configuration.

Offline devices must not invent or modify standard pricing.

If a new configuration is unavailable offline:

```text
Latest Valid Local Configuration
```

continues to be used until synchronization.

---

## 33. Configuration Synchronization

Configuration synchronization must preserve version ordering.

Recommended sequence:

```text
Transactions
    ↓
Transaction Synchronization
    ↓
Configuration Synchronization
```

A configuration update must not cause an already-created offline transaction to be rewritten.

---

## 34. Stale Configuration

If an offline device submits a transaction using an older but previously valid configuration, the server validates:

* configuration version;
* effective session;
* product status;
* branch availability;
* price validity;
* subscription;
* employee permission;
* inventory.

If the transaction is valid under the applicable offline authorization rules, it may be accepted.

If not valid, it becomes an explicit synchronization conflict or rejection.

---

## 35. Price Change Concurrency

Two employees must not be able to silently overwrite the same price configuration.

The database should use optimistic concurrency through:

* version number;
* unique active version constraints;
* effective session;
* controlled update transaction.

A stale configuration update must be rejected.

---

## 36. Menu Change Concurrency

The same concurrency principle applies to menu availability.

Example:

```text
Manager A
reads Version 4

Manager B
updates Version 4 → Version 5

Manager A
attempts update using Version 4
        ↓
Rejected as stale
```

The client must reload the current configuration before retrying.

---

## 37. Product Deactivation

Deactivating a Product must not delete historical menu or price records.

The Product remains available for:

* historical orders;
* reports;
* audit;
* inventory history;
* recipe history.

It simply becomes unavailable for new sales.

---

## 38. Branch Product Deactivation

A Branch may disable a Product without deleting:

* Product;
* Product Price;
* Recipe;
* Set references;
* historical Orders.

The Branch Menu configuration records the disabled state.

---

## 39. Category Relationship

Each Product belongs to exactly one Business Category.

Menu ordering and display may use Category information.

The database must enforce:

```text
Product.business_id = Category.business_id
```

Cross-Business category assignment is invalid.

---

## 40. Product Image

Product images are optional.

Image metadata should be stored separately from core pricing records where appropriate.

Changing an image must not create a new Product Price Version.

Image changes must not modify historical Order snapshots.

---

## 41. Printer Routing Relationship

Menu configuration may be associated indirectly with Kitchen Printer routing.

The pricing database model must not directly control printing.

Conceptually:

```text
Product
  ↓
Kitchen Routing Configuration
  ↓
Printer
```

Printing remains a separate operational concern.

---

## 42. Subscription Entitlement

Menu and pricing operations are subject to Business subscription entitlements.

If a relevant feature is disabled:

* existing data remains;
* historical prices remain;
* historical orders remain;
* current read access remains where permitted;
* new modifying operations are blocked.

Subscription checks must not be implemented as destructive database operations.

---

## 43. Database Tables

The logical model may include:

```text
business_menu_items
product_price
product_price_versions
branch_menu_items
branch_price_overrides
set_prices
set_price_versions
```

Depending on the final implementation, some tables may be consolidated into the general Configuration model.

The final schema must preserve the logical boundaries defined in this document.

---

## 44. Suggested `business_menu_items` Fields

```text
id
business_id
product_id
status
display_order
current_version_id
created_at
updated_at
```

Recommended constraints:

```text
UNIQUE (business_id, product_id)
```

for the logical current menu item.

---

## 45. Suggested `branch_menu_items` Fields

```text
id
business_id
branch_id
product_id
enabled
current_version_id
created_at
updated_at
```

Recommended logical uniqueness:

```text
UNIQUE (business_id, branch_id, product_id)
```

Historical versions are stored separately.

---

## 46. Suggested `product_price` Fields

```text
id
business_id
product_id
currency
current_version_id
created_at
updated_at
```

Recommended logical uniqueness:

```text
UNIQUE (business_id, product_id)
```

---

## 47. Suggested `product_price_versions` Fields

```text
id
product_price_id
version
amount
status
effective_from_session_id
created_by
created_at
```

Recommended uniqueness:

```text
UNIQUE (product_price_id, version)
```

---

## 48. Suggested `branch_price_overrides` Fields

```text
id
business_id
branch_id
product_id
current_version_id
created_at
updated_at
```

Recommended uniqueness:

```text
UNIQUE (business_id, branch_id, product_id)
```

---

## 49. Suggested Branch Price Version Fields

```text
id
branch_price_override_id
version
amount
status
effective_from_session_id
created_by
created_at
```

Recommended uniqueness:

```text
UNIQUE (branch_price_override_id, version)
```

---

## 50. Foreign Key Rules

The database should enforce valid ownership relationships.

Important relationships include:

```text
business_menu_item.business_id
    → business.id

business_menu_item.product_id
    → product.id

branch_menu_item.business_id
    → business.id

branch_menu_item.branch_id
    → branch.id

branch_menu_item.product_id
    → product.id

product_price.product_id
    → product.id

branch_price_override.branch_id
    → branch.id

branch_price_override.product_id
    → product.id
```

Cross-Business relationships must be prevented through composite ownership validation or equivalent database constraints.

---

## 51. Active Price Uniqueness

For a given pricing scope, only one price version may be operationally active at a specific effective boundary.

The implementation must prevent ambiguous active pricing.

A database constraint, exclusion strategy, or transactional application rule may be used depending on the final PostgreSQL implementation.

---

## 52. Effective Session Reference

When a price version is configured to start from a Cash Session, the database should retain the referenced session identity.

This allows the system to determine:

```text
Which configuration was active?
When did it become active?
Which Cash Session activated it?
```

The reference must not be used to rewrite historical orders.

---

## 53. Historical Configuration

Historical configuration versions must remain immutable.

They may be referenced by:

* Orders;
* Reports;
* Audit events;
* synchronization records;
* configuration history.

Deleting an unused current configuration is different from deleting a historical configuration.

Historical records must remain available while required by retention rules.

---

## 54. Reports

Reports may need:

* current menu state;
* historical menu state;
* current prices;
* historical prices;
* branch overrides;
* effective configuration versions.

Reports must use the correct historical snapshot rather than blindly reading the current Product price.

---

## 55. Indexing Strategy

Important indexes include:

```text
business_menu_items(business_id, product_id)
branch_menu_items(business_id, branch_id, product_id)
product_price(business_id, product_id)
product_price_versions(product_price_id, version)
branch_price_overrides(business_id, branch_id, product_id)
```

Additional indexes may be added for:

* active status;
* effective session;
* configuration version;
* audit references.

Indexes must support POS read paths without creating unnecessary write overhead.

---

## 56. POS Read Path

The common POS query should efficiently resolve:

```text
Business
  ↓
Branch
  ↓
Category
  ↓
Product
  ↓
Branch Availability
  ↓
Effective Price
```

This must not require scanning historical configuration versions.

The current effective configuration should be directly queryable.

---

## 57. Cache Compatibility

Menu and pricing data may be cached.

Cache is never authoritative.

Recommended cache scope:

```text
Business + Branch + Configuration Version
```

A configuration change must invalidate or version the affected cache entry.

Historical order values must never depend on cache availability.

---

## 58. Transaction Boundary

Creating a new price configuration should be atomic.

A successful operation must not leave:

```text
Price Version created
BUT
configuration activation missing
```

or:

```text
Branch override created
BUT
required ownership validation missing
```

The database transaction must commit the complete configuration state together.

---

## 59. Historical Integrity

The following must remain immutable after transaction creation:

* Order Item price;
* applied discount snapshot;
* applied markup;
* Set price;
* relevant price/configuration references.

Current configuration changes must not rewrite transaction history.

---

## 60. Data Lifecycle

Menu and pricing data follow Business lifecycle rules.

During subscription expiry:

* historical menu data remains;
* historical prices remain;
* current configuration remains readable where permitted;
* modifying configuration is blocked.

During Business deletion:

* menu and pricing data are deleted according to the dependency-aware deletion process;
* historical dependencies are handled before parent deletion;
* deletion is idempotent.

---

## 61. Audit Relationship

Important changes must create audit events.

Examples:

* price created;
* price changed;
* branch override created;
* branch override changed;
* menu product enabled;
* menu product disabled;
* configuration approved;
* configuration activated;
* configuration archived.

Audit history does not replace immutable price/configuration history.

---

## 62. Security Requirements

The database model must support:

* Business isolation;
* Branch scope validation;
* permission-controlled changes;
* subscription entitlement checks;
* immutable historical versions;
* actor attribution;
* device attribution where applicable;
* Cash Session attribution where applicable;
* synchronization validation.

Database ownership constraints must complement application authorization.

---

## 63. Performance Requirements

Menu and pricing are high-frequency POS read paths.

Therefore:

* current configuration must be cheap to read;
* historical versions must not slow normal reads;
* indexes must support Business/Branch lookup;
* cache may reduce repeated reads;
* heavy history/report queries must not block POS;
* configuration writes are relatively infrequent compared with POS reads.

---

## 64. Consistency Model

Menu and pricing configuration uses strong consistency for server-side changes.

After successful commit:

```text
Database state = authoritative configuration state
```

Offline devices may temporarily use older valid configuration.

Synchronization eventually updates them.

---

## 65. Cross-Domain Relationships

### Product

Provides the sellable catalog identity.

### Category

Provides Product classification.

### Recipe

Defines production/consumption relationships.

### Set

Defines fixed product combinations and its own price.

### Branch

Defines local menu availability and possible price overrides.

### Cash Session

Defines the configuration activation boundary.

### Order

Stores historical price snapshots.

### Inventory

Provides stock availability and Last Purchase Cost.

### Subscription

Controls whether configuration changes are permitted.

### Audit

Records important configuration changes.

### Synchronization

Distributes configuration changes to trusted offline devices.

---

## 66. Database Invariants

The following invariants are mandatory:

1. Every menu record belongs to exactly one Business.
2. Every menu Product belongs to the same Business.
3. Every Branch Menu record belongs to the same Business as its Branch.
4. Every Branch Menu Product belongs to the same Business.
5. A Product cannot be assigned to a Branch from another Business.
6. A Product has exactly one Category.
7. Category and Product must belong to the same Business.
8. Business Menu Product identity is unique within the Business.
9. Branch Menu Product identity is unique within the Branch.
10. Standard Product Price belongs to exactly one Business Product.
11. Branch Price Override belongs to exactly one Business Branch Product combination.
12. Price amounts cannot be negative.
13. Historical price versions are immutable.
14. Price version numbers are unique within their price definition.
15. Branch price version numbers are unique within their override.
16. Only valid price versions may become active.
17. Ambiguous active prices are forbidden.
18. Price changes do not overwrite previous versions.
19. Price changes do not rewrite existing orders.
20. Order Item price snapshots remain authoritative for historical orders.
21. Set prices are independent from component Product prices.
22. Set price versions are immutable.
23. Recipe changes do not silently modify selling prices.
24. Last Purchase Cost is not treated as selling price.
25. Custom markup cannot be negative.
26. Custom markup cannot exceed 100%.
27. Custom markup does not modify the standard Product price.
28. Discounts do not modify Product Price Versions.
29. Branch price overrides require authorized application operations.
30. Cashier cannot bypass price authorization through direct database writes.
31. Price changes become effective only at the defined configuration boundary.
32. Existing active Cash Sessions retain their valid configuration.
33. Configuration versions cannot be silently overwritten.
34. Stale configuration updates must be rejected.
35. Unapproved configuration cannot become operational.
36. Inactive Products cannot be newly sold.
37. Deactivated Branch Menu items remain historically queryable.
38. Historical Products remain referenced by historical orders.
39. Historical price references cannot point to another Business.
40. Historical configuration cannot cross Branch scope.
41. Offline devices cannot invent authoritative prices.
42. Offline devices use the latest valid synchronized configuration.
43. Transaction synchronization cannot rewrite historical price snapshots.
44. Configuration synchronization cannot rewrite existing transactions.
45. Transaction synchronization takes precedence over configuration synchronization.
46. Price configuration changes are auditable.
47. Audit events do not replace price history.
48. Configuration changes must preserve actor attribution.
49. Effective configuration must be deterministic.
50. Cache must never be the authoritative source of price.
51. Cache invalidation must not delete historical prices.
52. POS reads must not require full historical version scans.
53. Current configuration queries must be indexed.
54. Historical configuration must remain available during subscription expiry.
55. Subscription expiry must not delete pricing history.
56. Subscription downgrade must not silently delete existing price versions.
57. Business deletion must follow the dependency-aware lifecycle.
58. Deletion operations must be idempotent.
59. Deleted Business identifiers are never reused.
60. Branch price overrides cannot affect another Branch.
61. Branch menu changes cannot affect another Business.
62. Product image changes cannot alter price history.
63. Printer routing changes cannot alter price history.
64. Price configuration transactions must be atomic.
65. Concurrent price updates cannot silently overwrite each other.
66. Concurrent menu updates cannot silently overwrite each other.
67. Effective price resolution must have one deterministic result.
68. Historical order totals must not depend on current menu configuration.
69. Historical reports must use historical configuration when required.
70. Database constraints and application validation must enforce the same ownership boundaries.

---

## 67. Related Documents

### Database

* `01_Database_Overview.md`
* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `06_Subscription_and_Entitlement_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `08_Product_and_Category_Data_Model.md`
* `09_Recipe_and_Recipe_Version_Data_Model.md`
* `10_Set_and_Set_Version_Data_Model.md`
* `11_Inventory_and_Warehouse_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `25_Database_Integrity_and_Constraints.md`
* `26_Database_Indexes_and_Query_Strategy.md`

### Domain

* `10_Menu_and_Pricing_Domain.md`
* `18_Configuration_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `17_Products_Recipes_and_Sets.md`
* `18_Menu_Pricing_and_Configuration.md`
* `27_System_Wide_Consistency_and_Concurrency.md`

### Architecture

* `07_Database_Architecture.md`
* `18_Technology_Selection.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 68. Final Rule

The Menu and Pricing Data Model must provide a fast current-price lookup for POS while preserving immutable historical configuration and transaction pricing.

The central rule is:

```text
Current Configuration may change.
Historical Transaction Pricing must not change.
```

Menu availability, pricing, discounts, recipes, Sets, inventory, and Orders must remain separate database concerns connected through explicit, validated relationships.

