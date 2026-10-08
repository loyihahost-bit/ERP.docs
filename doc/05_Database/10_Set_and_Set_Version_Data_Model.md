# Set and Set Version Data Model

**Document ID:** DB-10
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Sets;
* Set versions;
* Set components;
* Set pricing;
* Set availability;
* Set configuration history;
* Branch usage;
* inventory consumption;
* Order snapshots;
* effective configuration boundaries.

A Set represents a predefined combination of Products sold together.

A Set is different from a Recipe:

```text
Recipe
→ defines production/consumption composition.

Set
→ defines a stable combination of sellable Products.
```

Set components cannot be freely substituted during an Order.

---

# 2. Set Model Overview

Conceptually:

```text
Business
   ↓
Set
   ↓
Set Version
   ↓
Set Components
   ↓
Products
```

A Set may contain multiple Products.

Example:

```text
Combo 1
 ├── Burger × 1
 ├── Fries × 1
 └── Cola × 1
```

---

# 3. Set Identity

Every Set has:

* UUID;
* Business ownership;
* lifecycle state.

Set UUID must be:

* immutable;
* globally unique;
* never reused.

Set name is descriptive and must not be used as identity.

---

# 4. Business Ownership

Every Set belongs to exactly one Business.

All Set Components must reference Products belonging to the same Business.

Cross-Business Set relationships are forbidden.

Conceptually:

```text
Set.business_id
      =
SetComponent.product.business_id
```

---

# 5. Set vs Product

A Set is not itself a normal Product component.

It is a sellable configuration composed of Products.

A Set may have its own:

* name;
* code;
* price;
* status;
* category/configuration;
* version history.

The implementation may expose a Set as a POS sellable item while preserving the distinction in the database.

---

# 6. Set Components

Each Set Version contains one or more components.

A component references a Product and quantity.

Example:

```text
Burger × 1
Fries × 1
Cola × 1
```

The component definition is part of the Set Version.

---

# 7. Component Quantity

Set component quantity must be positive.

Examples:

```text
Burger × 1
Cola × 2
```

Zero or negative quantities are invalid.

Changing quantity creates a new Set Version.

---

# 8. Set Version

Every configuration change to a Set creates a new Set Version.

Examples:

* adding a Product;
* removing a Product;
* changing quantity;
* changing composition;
* changing effective configuration.

Historical versions remain immutable.

---

# 9. Set Version Number

Versions are ordered within a Set.

Example:

```text
Set A
 ├── Version 1
 ├── Version 2
 └── Version 3
```

Recommended constraint:

```text
UNIQUE(set_id, version_number)
```

---

# 10. Set Version Lifecycle

Conceptual lifecycle:

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

Rejected configuration may remain stored for historical/audit purposes.

---

# 11. Draft Set Version

Draft versions may be edited before approval.

Draft changes must not affect:

* active POS;
* current Orders;
* current inventory calculations;
* historical transactions.

---

# 12. Set Approval

Set configuration changes require the applicable permission.

Approval should record:

* Set Version;
* approving Employee;
* timestamp;
* result;
* optional comment.

Approval history is append-only.

---

# 13. Effective Boundary

Set configuration changes become effective from the next Cash Session according to the established configuration rule.

Conceptually:

```text
Current Cash Session
      ↓
Old Set Version

Next Cash Session
      ↓
New Set Version
```

This prevents a live POS session from changing its operational Set composition unexpectedly.

---

# 14. Active Set Version

At a given operational time and scope, only one Set Version should be effective.

Overlapping active versions must be prevented.

---

# 15. Set Composition Stability

Set composition is stable.

A component cannot be silently replaced during an Order.

Example:

```text
Combo A
 ├── Burger
 ├── Fries
 └── Cola
```

A cashier cannot replace Cola with another Product unless the Business explicitly implements a separate configurable feature in the future.

Current scope does not allow component substitution.

---

# 16. Set Modification

If the Business wants to change a Set:

```text
Version 1
   ↓
Version 2
```

The old version remains historically valid.

Existing Orders continue to reference the version used at the time of sale.

---

# 17. Set Price

A Set has its own selling price.

Set price is separate from:

* component Product prices;
* Product Recipe cost;
* discounts;
* custom markup.

Changing a component Product's price does not silently rewrite historical Set sale prices.

---

# 18. Set Price History

Price changes must preserve historical prices.

Recommended model:

```text
Set
 ↓
Set Version
 ↓
Set Price Version
```

Alternatively, price may be stored as part of the configuration version if the implementation keeps composition and price versioning synchronized.

The chosen implementation must preserve historical integrity.

---

# 19. Set and Product Price

Component Product prices are not automatically added to determine the Set selling price.

The Set may intentionally have:

* lower combined price;
* promotional price;
* independent configured price.

Therefore Set price is authoritative for Set sales.

---

# 20. Set Discount

Discounts apply separately to the Set sale.

A discount must not modify the Set master price.

Historical Orders preserve:

* Set price;
* discount;
* final amount.

---

# 21. Set and Recipe

A Set is not a Recipe.

Example:

```text
Set:
Burger + Fries + Cola

Recipe:
Burger → Bun + Meat + Sauce
```

The Set may indirectly consume inventory through its component Products.

---

# 22. Set Inventory Consumption

When a Set is sold, inventory consumption is calculated from its components.

Example:

```text
Set × 1

→ Burger × 1
→ Fries × 1
→ Cola × 1
```

Each component follows its own inventory/Recipe rules.

The complete Set sale must satisfy stock requirements.

---

# 23. Atomic Set Sale

Set inventory consumption must be atomic with Set Order acceptance.

If any required component cannot be fulfilled:

```text
Set Acceptance = Rejected
```

The system must not partially accept the Set.

---

# 24. Set Component Recipe Consumption

If a Set component has a Recipe:

```text
Set
 ↓
Burger
 ↓
Burger Recipe
 ↓
Recipe Components
```

Inventory consumption may therefore traverse:

```text
Set
 → Product
 → Recipe
 → Inventory
```

The effective Recipe Version must be resolved according to configuration rules.

---

# 25. Set Component Stock Validation

Before accepting a Set sale, the system must validate required stock for all components.

Insufficient stock for one component rejects the complete Set operation.

No negative inventory is permitted.

---

# 26. Set and Order Snapshot

When a Set is added to an Order, the Order must preserve enough information to reconstruct what was sold.

Recommended snapshot data:

* Set UUID;
* Set Version UUID;
* Set name;
* Set code;
* Set price;
* quantity;
* component snapshot;
* applicable configuration reference.

---

# 27. Historical Set Integrity

Later Set changes must not modify historical Orders.

For example:

```text
Order 100
Set Version 1
Burger + Fries + Cola

Later:
Set Version 2
Burger + Fries + Juice
```

Order 100 must continue to show:

```text
Burger + Fries + Cola
```

---

# 28. Set and Order Modification

An unpaid Order may be modified according to Order rules.

If a Set is removed or its quantity is reduced:

* inventory return behavior follows the established Order modification rules;
* the system must preserve the original transaction history;
* any inventory decision is audited.

A Set cannot be silently transformed into another Set.

---

# 29. Set Quantity Increase

Increasing Set quantity requires additional inventory validation.

If stock is insufficient:

```text
Modification = Rejected
```

The original Order remains unchanged.

---

# 30. Set Quantity Reduction

Reducing Set quantity may return inventory if the user explicitly confirms the inventory return according to Order modification rules.

The inventory decision must be recorded.

---

# 31. Set Removal

Removing a Set from an Accepted unpaid Order follows the same controlled inventory-return rules as other accepted products.

The original Set consumption remains historically traceable.

---

# 32. Paid Set Order

A paid Set Order cannot be ordinarily edited.

Required changes use:

* cancellation;
* refund;
* correction;

according to the applicable permissions and business rules.

The original Set sale remains historically preserved.

---

# 33. Set and Branch Availability

A Set may be globally defined but unavailable in a Branch.

Conceptually:

```text
Set
 ↓
BranchSet
 ↓
Branch
```

Branch availability may depend on:

* Product availability;
* inventory;
* equipment;
* Branch menu configuration;
* subscription entitlement.

---

# 34. Set Availability

Set availability should be derived from:

```text
Set State
+
Branch State
+
Component Availability
+
Configuration
+
Subscription
```

The exact availability calculation belongs to application/domain logic.

---

# 35. Component Inactivation

If a component Product becomes inactive, the Set should not silently change its composition.

The Set may become unavailable until the configuration is changed.

This protects Set historical integrity.

---

# 36. Component Archival

If a component Product is archived:

* historical Set Versions remain valid;
* historical Orders remain readable;
* current Set availability may become invalid;
* a new Set Version is required for operational changes.

---

# 37. Set Category

If Sets appear in the POS menu, their category assignment must follow the menu/category model.

The category relationship must remain Business-scoped.

Category changes must not rewrite historical Order snapshots.

---

# 38. Set Code

A Set may have a human-readable code.

The code should be Business-scoped and unique.

Recommended:

```text
UNIQUE(business_id, code)
```

Set UUID remains the authoritative identity.

---

# 39. Set Name

Set name is mutable descriptive data.

Changing the Set name does not change Set UUID.

Historical Order snapshots preserve the transaction-time name.

---

# 40. Set Image

A Set may have an optional image.

Image storage should use an external asset reference rather than storing large binary content in the primary Set row.

Image changes must not affect historical Orders.

---

# 41. Set and Configuration

Set composition is configuration data.

Configuration changes must support:

* versioning;
* approval;
* effective boundaries;
* audit;
* concurrency control.

A configuration change must not modify historical versions.

---

# 42. Set and Branch Configuration

Branch-specific availability is separate from Set definition.

A Branch may enable or disable a Set without changing the Business-level Set definition.

---

# 43. Set and Pricing Configuration

Set pricing may be:

* Business-level;
* Branch-overridden where permitted.

Branch price overrides must preserve:

* effective date/session;
* previous price;
* actor;
* reason where required.

---

# 44. Set and Inventory Cost

Set cost may be calculated from component Product costs.

Cost calculation is separate from Set selling price.

Historical Order prices remain unchanged when component costs change.

---

# 45. Set and Last Purchase Cost

Last Purchase Cost belongs to Product/Inventory data.

It must not become a Set identity field.

Set cost calculations may consume current Product cost information according to the costing model.

---

# 46. Set Approval History

Approval records should include:

* Set Version UUID;
* action;
* actor;
* timestamp;
* comment;
* previous status;
* new status.

Approval records must be append-only.

---

# 47. Set Audit

Important Set events should create Audit records:

* creation;
* component addition;
* component removal;
* quantity change;
* price change;
* submission;
* approval;
* rejection;
* activation;
* deactivation;
* archival;
* restoration.

---

# 48. Set and Offline Operation

Trusted offline devices may use the latest valid synchronized Set Version.

Offline devices must not use unknown or unsynchronized Set configurations.

When synchronizing:

1. offline transactions are submitted;
2. transaction configuration is validated;
3. server determines validity;
4. configuration updates are synchronized;
5. conflicts are handled explicitly.

---

# 49. Offline Set Version

A later Set Version does not invalidate a previously valid offline transaction.

Historical Set Version references must remain resolvable until Business data lifecycle rules permit deletion.

---

# 50. Set Database Structure

Recommended logical structure:

```text
Business
   │
   └── Set
         │
         ├── SetVersion
         │      │
         │      ├── SetComponent
         │      │       └── Product
         │      │
         │      └── SetApproval
         │
         └── BranchSet
```

Related operational entities:

```text
SetVersion
   ├── OrderItem
   ├── InventoryTransaction
   ├── PriceConfiguration
   └── AuditEvent
```

---

# 51. Suggested Core Fields

## Set

```text
id
business_id
code
name
status
category_id
image_reference
created_at
updated_at
archived_at
version
```

## SetVersion

```text
set_id
version_number
status
effective_from
effective_to
created_by_employee_id
created_at
approved_by_employee_id
approved_at
version
```

## SetComponent

```text
set_version_id
product_id
quantity
sort_order
created_at
```

## BranchSet

```text
business_id
branch_id
set_id
status
availability_status
price_override_reference
created_at
updated_at
version
```

## SetApproval

```text
set_version_id
action
actor_employee_id
comment
created_at
```

The final physical schema may normalize additional fields.

---

# 52. Database Constraints

Recommended constraints include:

```text
UNIQUE(set_id, version_number)
```

```text
UNIQUE(business_id, code)
```

Component quantity:

```text
quantity > 0
```

Tenant consistency must ensure:

```text
Set.business_id
=
SetVersion.Set.business_id
=
SetComponent.Product.business_id
```

Composite foreign keys should be used where practical.

---

# 53. Circular Set References

A Set Component must reference a Product.

A Set must not indirectly create an invalid recursive Set structure.

If the implementation represents Sets as separate sellable entities rather than Products, the application must still prevent unsupported recursive composition.

Current scope does not require nested Sets.

---

# 54. Concurrency

Concurrent Set configuration changes must not cause:

* duplicate version numbers;
* two simultaneously active versions;
* stale overwrite;
* historical version mutation.

Optimistic concurrency or database locking should be used where appropriate.

---

# 55. Set Archival

Archiving a Set preserves:

* Set UUID;
* code;
* name;
* historical versions;
* components;
* prices;
* Branch references;
* Order references;
* audit history.

Archival must not physically remove historical Set data.

---

# 56. Set Restoration

Restoration requires validation of:

* Business state;
* Category;
* Products;
* component availability;
* Branch configuration;
* subscription entitlement;
* permissions.

Restoration does not rewrite historical Orders.

---

# 57. Category and Set Integrity

If a Set has a category:

```text
Set.category.business_id
=
Set.business_id
```

Cross-Business category references are forbidden.

---

# 58. Product and Set Integrity

Every Set Component Product must belong to the same Business as the Set.

This must be validated both:

* at application level;
* at database integrity level where practical.

---

# 59. Performance

Set lookup is a frequent POS operation.

Therefore:

* active Set queries must be indexed;
* Set Components must be efficiently retrievable;
* Branch availability must be efficiently resolvable;
* active Set Versions should be cacheable;
* historical versions should not burden normal POS lookup.

Cache is never authoritative.

---

# 60. Data Lifecycle

Set data follows Business lifecycle rules.

During subscription read-only state:

* Set history remains visible;
* Set modifications are blocked.

During Business deletion:

* Set data is removed through dependency-aware deletion;
* deletion is idempotent;
* stale offline events cannot recreate deleted Sets.

---

# 61. Database vs Application Responsibilities

### Database responsibilities

* Set identity;
* Business ownership;
* version uniqueness;
* Product references;
* quantity constraints;
* referential integrity;
* historical storage.

### Application responsibilities

* Set validation;
* approval;
* effective version selection;
* availability calculation;
* inventory validation;
* pricing;
* permission checks;
* subscription checks;
* concurrency workflow;
* recursive composition validation.

---

# 62. Core Invariants

The following invariants are mandatory:

1. Every Set belongs to exactly one Business.
2. Set UUID is immutable.
3. Set UUID is never reused.
4. Set code is not the primary identity.
5. Set code is Business-scoped.
6. Set codes are not silently reassigned.
7. Every Set Version belongs to exactly one Set.
8. Set Version numbers are unique within a Set.
9. Historical Set Versions are immutable.
10. Draft Set Versions may be edited before approval.
11. Active Set Versions cannot be silently rewritten.
12. Every Set Version has at least one valid component.
13. Every Set Component references a Product.
14. Set Components belong to the same Business as the Set.
15. Cross-Business Set components are forbidden.
16. Set component quantities must be positive.
17. Set composition cannot be silently substituted during an Order.
18. Nested Sets are not supported in the current scope.
19. Set changes create new versions.
20. Component additions create new versions.
21. Component removals create new versions.
22. Quantity changes create new versions.
23. Set configuration approval is permission-controlled.
24. Approval history is append-only.
25. Set activation follows effective configuration boundaries.
26. Only one effective Set Version exists for a Set at a given operational scope/time.
27. Set price is separate from component Product prices.
28. Set price changes preserve historical prices.
29. Discounts do not modify the Set master price.
30. Set sale uses the applicable Set price snapshot.
31. Historical Orders preserve Set Version identity.
32. Historical Orders preserve required Set composition snapshots.
33. Later Set changes do not rewrite historical Orders.
34. Set inventory consumption is atomic with Set acceptance.
35. Insufficient component stock rejects the complete Set operation.
36. Set sales cannot create negative inventory.
37. Component Products may have Recipes.
38. Recipe consumption follows the applicable Recipe Version.
39. Set is distinct from Recipe.
40. Recipe changes do not silently rewrite Set composition.
41. Component Product inactivity does not rewrite Set composition.
42. Component Product archival does not rewrite historical Set Versions.
43. A Set may become unavailable when a required component is unavailable.
44. Branch availability is separate from global Set definition.
45. Branch Set availability is Business-scoped.
46. Set queries are always Business-scoped.
47. Client-supplied Business IDs cannot bypass isolation.
48. Set category belongs to the same Business.
49. Set images are separate from Set identity.
50. Set image changes do not rewrite historical transactions.
51. Set price overrides are version/effective-boundary aware.
52. Set configuration changes are auditable.
53. Set approval changes are auditable.
54. Offline devices use only synchronized valid Set Versions.
55. Later Set Versions do not invalidate previously valid offline transactions.
56. Offline Set transactions preserve Set Version identity.
57. Set configuration conflicts are explicit.
58. Concurrent Set updates are concurrency-safe.
59. Cache is not authoritative for Set state.
60. Historical Set data remains readable during subscription read-only state.
61. Set modification is blocked when entitlement does not allow it.
62. Set deletion follows Business data lifecycle rules.
63. Stale offline events cannot resurrect deleted Set data.
64. Historical Set UUIDs are never reused.
65. Set history remains reconstructable until Business lifecycle deletion.

---

## Related Documents

* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

