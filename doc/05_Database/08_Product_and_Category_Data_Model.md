# Product and Category Data Model

**Document ID:** DB-08
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* product categories;
* products;
* raw materials;
* semi-finished products;
* finished products;
* product lifecycle;
* product codes;
* product availability;
* product images;
* product-to-category relationships;
* product references used by recipes, menu, Sets, inventory and orders.

The model must preserve product identity and historical integrity while allowing products to be archived or made inactive without destroying historical transactions.

---

# 2. Product Model Overview

The system supports three operational product types:

```text id="n8z7ap"
Raw Material
     ↓
Semi-Finished Product
     ↓
Finished Product
```

A Product represents a Business-level product definition.

Inventory quantity is Branch-specific.

Product definition and inventory state must therefore remain separate.

---

# 3. Product Identity

## 3.1 Product UUID

Every Product has:

* UUID;
* Business ownership;
* stable identity;
* lifecycle state.

The Product UUID must be:

* immutable;
* globally unique;
* never reused.

Product names and product codes are not primary identities.

---

# 4. Business Ownership

Every Product belongs to exactly one Business.

Conceptually:

```text id="9w8a0h"
Business
   ↓
Product
```

A Product from Business A must never be usable by Business B.

This applies to:

* Orders;
* Recipes;
* Sets;
* Menu;
* Inventory;
* Branch configuration;
* pricing.

---

# 5. Product Type

Each Product must have exactly one product type.

Supported types:

```text id="y3y5n4"
RAW_MATERIAL
SEMI_FINISHED
FINISHED
```

The product type is authoritative.

A Product cannot simultaneously be treated as two product types.

---

# 6. Raw Material

A Raw Material is an ingredient or inventory item used as an input.

Examples:

* flour;
* meat;
* mayonnaise;
* oil;
* spices;
* vegetables.

Raw Materials may participate in recipes.

A Raw Material normally does not require another Product recipe to exist.

---

# 7. Semi-Finished Product

A Semi-Finished Product is produced from one or more other products.

Example:

```text id="r2j8w3"
Meat 1 kg
+
Mayonnaise 200 g
+
Spices
      ↓
Prepared Meat
```

A Semi-Finished Product may then be used in another recipe.

This supports:

```text id="0i1gl6"
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

---

# 8. Finished Product

A Finished Product is a sellable or operational menu product.

Examples:

* Lavash;
* Burger;
* Pizza;
* Hotdog.

A Finished Product may have a Recipe.

A Finished Product without a Recipe may exist where business rules allow it, but inventory-dependent sales must satisfy the applicable stock rules.

---

# 9. Product Category

Every Product belongs to exactly one Menu Category.

Conceptual relationship:

```text id="f55kjb"
Category
   ↓
Product
```

A Product must not belong to multiple categories simultaneously.

If a product needs to appear in multiple UI contexts, the system should use menu/configuration mechanisms rather than assigning multiple primary categories.

---

# 10. Category Identity

Category fields may include:

* `id`;
* `business_id`;
* `name`;
* `status`;
* `sort_order`;
* `created_at`;
* `updated_at`.

Category UUID is immutable and never reused.

---

# 11. Category Ownership

Categories are Business-scoped.

A category from Business A must never be referenced by a Product belonging to Business B.

Recommended constraint:

```text id="jv1g0p"
UNIQUE(business_id, name)
```

Exact uniqueness may be adjusted if the Business later requires duplicate category names.

---

# 12. Category Lifecycle

Category lifecycle may be represented as:

```text id="f74f4c"
Active
   ↓
Inactive
   ↓
Archived
```

Inactive or archived categories must not erase their Products.

Historical Products and Orders remain intact.

---

# 13. Product Lifecycle

Product lifecycle:

```text id="8w6yq4"
Draft
   ↓
Active
   ↓
Inactive
   ↓
Archived
```

A Product may be archived instead of deleted when historical references exist.

---

# 14. Product Deletion

Products referenced by:

* Orders;
* Recipes;
* Inventory;
* Sets;
* Payments through Orders;
* Reports;
* Audit records

must not be physically deleted during normal operations.

The preferred operation is:

```text id="7f5n6q"
Active → Inactive → Archived
```

---

# 15. Product Activation

A Product may be activated only when required configuration is valid.

Depending on Product type and business rules, validation may include:

* Category;
* Recipe;
* price;
* menu availability;
* required inventory configuration.

Activation must not invalidate historical transactions.

---

# 16. Product Inactivation

An inactive Product:

* is not shown for new normal sales;
* cannot be newly selected for Orders;
* remains available in historical Orders;
* remains available in reports;
* retains its UUID;
* retains Recipe and configuration history.

---

# 17. Product Code

The system may generate a Product code automatically.

Example:

```text id="y7apz4"
PRD-000001
PRD-000002
```

The code is a human-readable identifier.

It must not replace Product UUID.

Code generation must be Business-safe and concurrency-safe.

---

# 18. Product Code Uniqueness

Product codes should normally be unique within a Business.

Recommended constraint:

```text id="5d7qwe"
UNIQUE(business_id, code)
```

A code should not be reassigned to a different Product after the original Product is archived.

This preserves historical references.

---

# 19. Product Name

Product names are mutable descriptive values.

Changing a Product name must not modify historical Order item names where snapshots are required.

Historical Orders must preserve the product identity and transaction-time display information.

---

# 20. Product Description

A Product may contain a description.

Descriptions are informational and may change without affecting Product identity.

Historical transaction snapshots should not depend on the current description.

---

# 21. Product Image

A Product may have an optional image.

The database should store a reference to the image asset rather than embedding large binary image content in the main Product row.

Conceptually:

```text id="1l4k9e"
Product
   ↓
Image Reference
```

Image storage and delivery are separate concerns.

---

# 22. Product Image History

If image history is required, replacing an image should create a new image reference/version rather than rewriting historical transaction data.

An image change must not affect:

* Product UUID;
* historical Orders;
* Recipe history;
* inventory history.

---

# 23. Product Unit

Inventory-managed Products require a unit of measurement.

Examples:

* kg;
* g;
* l;
* ml;
* piece.

The unit definition should be standardized rather than stored as uncontrolled free text.

---

# 24. Quantity Precision

Inventory quantity must support fractional quantities where required.

Examples:

```text id="h4w4pn"
1.5 kg
0.25 kg
250 g
2.5 l
```

The physical numeric type must provide sufficient precision without using floating-point arithmetic for inventory quantities where exact decimal behavior is required.

---

# 25. Product Cost Reference

Products may participate in cost calculations.

For custom markup, the current rule uses:

```text id="p4xj1e"
Final Price =
Last Purchase Cost ×
(1 + Markup / 100)
```

Cost history must remain separate from the Product identity.

A later purchase must not rewrite historical Order prices.

---

# 26. Last Purchase Cost

The current last purchase cost is operational state derived from inventory purchase records.

It should not be treated as immutable Product master data.

Conceptually:

```text id="j0z7pj"
Purchase
   ↓
Inventory Cost History
   ↓
Current Last Purchase Cost
```

---

# 27. Product Price Separation

Product identity must be separate from pricing.

A Product may have:

* global standard price;
* Branch override;
* historical price versions.

Price changes belong to the Menu/Pricing/Configuration data model.

This document only defines the Product reference.

---

# 28. Product and Branch Availability

A Product may be globally active but unavailable in a specific Branch.

Conceptually:

```text id="e5m4x6"
Product
   ↓
BranchProduct
   ↓
Branch
```

This allows:

* Business-wide product definition;
* Branch-specific availability;
* Branch-specific price;
* temporary Branch disablement.

---

# 29. Equipment-Based Availability

A Product may become unavailable because required equipment is broken.

The system should represent availability state separately from Product identity.

Example:

```text id="d1n5u7"
Product = Active
Branch Product = Active
Equipment Status = Broken
Effective Availability = Unavailable
```

The Product itself should not be archived simply because equipment is temporarily unavailable.

---

# 30. Product and Recipe Relationship

A Product may have a Recipe.

Conceptually:

```text id="m5v6h2"
Product
   ↓
Recipe
   ↓
Recipe Components
```

Recipe ownership and versioning are defined in the Recipe Data Model.

A Product that has historical Recipe references must not be physically deleted.

---

# 31. Product and Set Relationship

A Product may be a component of a Set.

Conceptually:

```text id="6y2t9e"
Set
   ↓
Set Components
   ↓
Product
```

A Product referenced by a Set must remain historically resolvable.

Changing Product state does not silently rewrite Set history.

---

# 32. Product and Order Relationship

Order Items reference Products.

The relationship should preserve:

* Product UUID;
* Product type;
* Product name snapshot;
* quantity;
* unit price snapshot;
* applicable configuration/version;
* relevant recipe/configuration reference.

Historical Order Items must remain readable after Product archival.

---

# 33. Product Snapshot

An Order Item should preserve transaction-time values where required.

Recommended snapshot fields include:

* product UUID;
* product name;
* product code;
* unit price;
* quantity;
* relevant recipe/configuration version.

Snapshots protect historical transaction integrity.

---

# 34. Product and Inventory Relationship

Inventory records reference Product UUID.

The same Product may have different stock quantities by Branch.

Conceptually:

```text id="g5v2mb"
Product
   ↓
Inventory Balance
   ↓
Branch
```

Inventory quantity is not stored as a single Business-global number when Branch-specific stock is required.

---

# 35. Product and Inventory Lifecycle

Archiving a Product does not erase:

* stock history;
* inventory transactions;
* purchases;
* adjustments;
* discrepancies.

If a Product is inactive, existing stock remains historically visible.

New sales are blocked according to Product availability rules.

---

# 36. Product and Shopping List

Shopping list entries may reference Products.

A Product may appear on a shopping list because:

* stock is below threshold;
* stock is zero;
* user manually added the item.

The shopping list does not become part of Product identity.

---

# 37. Product and Inventory Source

Inventory records may distinguish:

```text id="y6x7h0"
Bought Ready
Prepared in Branch
```

The Product definition remains unchanged.

Source is transaction/inventory data.

---

# 38. Product and Supplier

Supplier management is intentionally shallow.

Products may appear in purchase records associated with suppliers.

Supplier information must not be embedded into the Product identity because:

* one Product may have multiple suppliers;
* supplier price changes over time;
* historical purchases must remain immutable.

---

# 39. Product and Discount

Discounts apply to transaction pricing.

A discount must not modify the Product's standard price.

Conceptually:

```text id="2v7s6x"
Product Price
      +
Discount
      ↓
Order Final Price
```

Historical Orders preserve the discount context.

---

# 40. Product and Custom Markup

Custom markup is a transaction/configuration pricing mechanism.

It must not overwrite the standard Product price.

The applicable markup and resulting price should be stored with the relevant configuration or Order snapshot.

---

# 41. Product Category Ordering

Categories may contain display ordering.

`sort_order` should be treated as presentation/configuration data.

Changing category order must not affect:

* Product identity;
* Orders;
* Inventory;
* Recipes.

---

# 42. Product Ordering

Products may have display ordering within a category.

The ordering is UI/configuration data.

It must not be used as a Product identity.

---

# 43. Product Search

Product lookup may use:

* UUID;
* code;
* name;
* category;
* product type;
* Branch availability.

Search must always remain Business-scoped.

A Product code or name from another Business must never be returned to the current Business.

---

# 44. Product Query Isolation

Product queries must include Business context.

For Branch-specific operations, queries must additionally validate:

* Branch;
* Product availability;
* subscription entitlement;
* employee permission.

Client-supplied Business/Branch IDs cannot override authenticated scope.

---

# 45. Product Concurrency

Concurrent Product changes may occur.

Examples:

* Product activation;
* Product archival;
* Category change;
* Branch availability change;
* price configuration;
* Recipe configuration.

Versioning or optimistic concurrency should prevent stale updates from silently overwriting newer configuration.

---

# 46. Product Archival

Archiving should preserve:

* Product UUID;
* code;
* historical name;
* category reference;
* Product type;
* Recipe references;
* Set references;
* Order references;
* Inventory references.

Archiving should normally be represented as a state transition.

---

# 47. Product Restoration

An archived Product may be restored where allowed.

Restoration must validate:

* Business active;
* Category valid;
* required configuration;
* subscription entitlement;
* permissions.

Restoration creates an active state but does not modify historical transactions.

---

# 48. Category Archival

A Category with Products should not cause Products to disappear from historical records.

Before archiving a Category, the system should require:

* moving active Products to another valid Category;
* or inactivating affected Products.

Historical category references remain available.

---

# 49. Cross-Business Integrity

The database must prevent:

```text id="5x1l9a"
Product.business_id
    !=
Category.business_id
```

and:

```text id="h2m8q5"
Product.business_id
    !=
Recipe.business_id
```

and equivalent cross-Business relationships.

Composite foreign keys should be used where practical.

---

# 50. Recommended Logical Entity Set

```text id="f4c2ws"
Business
   │
   ├── Category
   │
   ├── Product
   │     ├── ProductImage
   │     ├── ProductHistory
   │     └── BranchProduct
   │
   └── ProductUnit
```

Related domains:

```text id="7v4c1m"
Product
 ├── Recipe
 ├── Set
 ├── Inventory
 ├── OrderItem
 ├── Price
 └── Configuration
```

---

# 51. Suggested Core Fields

## Category

```text id
business_id
name
status
sort_order
created_at
updated_at
```

## Product

```text id
business_id
category_id
code
name
description
product_type
unit_id
status
image_reference
created_at
updated_at
archived_at
version
```

## BranchProduct

```text id
business_id
branch_id
product_id
status
availability_status
price_override_reference
created_at
updated_at
version
```

The final physical schema may add or normalize fields during implementation.

---

# 52. Indexing

Important indexes should support:

* Product by Business;
* Product by Business + code;
* Product by Business + category;
* Product by Business + type;
* active Products;
* BranchProduct by Branch;
* BranchProduct by Product;
* Category by Business;
* Product search fields;
* historical Product references.

Indexes must reflect actual POS query patterns.

POS product lookup should be optimized because it is a high-frequency operation.

---

# 53. Performance

Product data is frequently read by POS clients.

Therefore:

* active Product queries should be efficient;
* Branch availability should be efficiently resolvable;
* configuration versions should be cacheable;
* images should not require loading large binary data for every product query;
* historical data should not slow normal active-product lookup.

Cache may accelerate reads but must not become authoritative.

---

# 54. Database vs Application Responsibilities

### Database responsibilities

* Product identity;
* Business ownership;
* Category relationships;
* Product type;
* uniqueness;
* lifecycle state;
* Branch relationship;
* referential integrity.

### Application responsibilities

* Product activation;
* Product availability rules;
* permission checks;
* subscription checks;
* Recipe validation;
* pricing;
* equipment availability;
* archival workflow;
* restoration workflow.

---

# 55. Core Invariants

The following invariants are mandatory:

1. Every Product belongs to exactly one Business.
2. Product UUID is immutable.
3. Product UUID is never reused.
4. Product code is not the primary identity.
5. Product code is Business-scoped.
6. Product code is not silently reassigned.
7. Every Product has exactly one Product type.
8. Supported Product types are Raw Material, Semi-Finished, and Finished.
9. Every Product belongs to exactly one primary Category.
10. Category belongs to the same Business as its Product.
11. Categories are Business-scoped.
12. Products from different Businesses cannot share Categories.
13. Raw Materials may be recipe inputs.
14. Semi-Finished Products may be produced from other Products.
15. Finished Products may have Recipes.
16. Product identity is separate from inventory quantity.
17. Inventory quantity is Branch-scoped where required.
18. Global Product activation does not imply Branch availability.
19. Branch availability is separate from global Product state.
20. Equipment failure does not require Product archival.
21. Inactive Products cannot be newly sold.
22. Inactive Products remain historically visible.
23. Archived Products retain historical references.
24. Products referenced by Orders are not physically deleted during normal operations.
25. Products referenced by Recipes are not physically deleted during normal operations.
26. Products referenced by Sets are not physically deleted during normal operations.
27. Product names may change without changing Product UUID.
28. Historical Order Items preserve required Product snapshots.
29. Historical Orders are not rewritten by Product changes.
30. Product images are separate from Product identity.
31. Product image changes do not modify historical transactions.
32. Product units use controlled definitions.
33. Inventory quantities use appropriate exact numeric precision.
34. Last Purchase Cost comes from inventory purchase history.
35. Last Purchase Cost does not overwrite historical Order prices.
36. Standard Product price is separate from Product identity.
37. Branch price overrides do not change the global Product price.
38. Discounts do not modify the Product master price.
39. Custom markup does not overwrite the Product master price.
40. Category ordering does not affect Product identity.
41. Product ordering does not affect Product identity.
42. Product search is always Business-scoped.
43. Branch Product queries validate Branch scope.
44. Client-supplied Business IDs cannot bypass tenant isolation.
45. Client-supplied Branch IDs cannot bypass Branch authorization.
46. Cross-Business Product relationships are forbidden.
47. Product archival preserves history.
48. Category archival does not erase Product history.
49. Product restoration does not rewrite historical transactions.
50. Concurrent Product updates must not silently overwrite newer state.
51. Product configuration changes are version-aware.
52. Product lifecycle changes are auditable.
53. Product category changes are auditable where applicable.
54. Product availability changes are auditable.
55. Product Branch availability is independently controlled.
56. Product inventory history survives Product archival.
57. Product shopping-list references survive Product archival where historically required.
58. Product supplier history belongs to purchase data, not Product identity.
59. Product cache is not authoritative.
60. Product data must remain Business-isolated.

---

## Related Documents

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

