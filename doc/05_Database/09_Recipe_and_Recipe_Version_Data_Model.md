# Recipe and Recipe Version Data Model

**Document ID:** DB-09
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* recipes;
* recipe versions;
* recipe components;
* raw material consumption;
* semi-finished product consumption;
* finished product recipes;
* yield and loss;
* recipe approval;
* effective configuration;
* historical recipe integrity;
* recipe references from inventory and orders.

The model must support traceability:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

Recipe history must remain immutable once a version becomes effective.

---

# 2. Recipe Model Overview

A Recipe defines how a Product is produced or consumed.

Conceptually:

```text
Product
   ↓
Recipe
   ↓
Recipe Version
   ↓
Recipe Components
```

A Recipe is the logical identity.

A Recipe Version represents a specific configuration of that Recipe.

---

# 3. Recipe Identity

Every Recipe has:

* UUID;
* Business ownership;
* Product reference;
* lifecycle state.

Recipe UUID must be:

* immutable;
* globally unique;
* never reused.

Recipe name must not be used as its identity.

---

# 4. Business Ownership

Every Recipe belongs to exactly one Business.

A Recipe may reference only Products belonging to the same Business.

Cross-Business recipe components are forbidden.

Conceptually:

```text
Recipe.business_id
      =
Recipe.product.business_id
      =
RecipeComponent.product.business_id
```

---

# 5. Product-to-Recipe Relationship

A Product may have a Recipe.

The relationship must preserve Product identity even if:

* Product name changes;
* Product becomes inactive;
* Product is archived.

Historical Recipe references must remain resolvable.

---

# 6. Recipe Types

The system primarily supports:

```text id="b2r4s7"
PRODUCTION_RECIPE
```

A production recipe describes how one Product is produced from components.

The same model can support:

* Semi-Finished Product recipes;
* Finished Product recipes.

---

# 7. Recipe Output

Each Recipe Version must define the expected output.

Conceptually:

```text
Recipe Version
      ↓
Expected Output Quantity
      +
Output Unit
```

Example:

```text
1 kg prepared meat
```

The output quantity is required for production calculations.

---

# 8. Recipe Components

A Recipe Version contains one or more components.

A component references a Product.

Examples:

```text id="4c7k1p"
Meat       1 kg
Mayonnaise 200 g
Spices     10 g
```

Components may reference:

* Raw Materials;
* Semi-Finished Products.

A Finished Product should not normally consume itself directly or indirectly.

---

# 9. Component Quantity

Each Recipe Component contains the required quantity for the recipe's defined output.

Example:

```text id="v4f8d2"
Output:
1 kg Prepared Meat

Components:
1 kg Meat
200 g Mayonnaise
10 g Spices
```

The quantity must use the component Product's supported unit.

---

# 10. Unit Consistency

Recipe quantities must be unit-compatible with the referenced Product.

Examples:

```text id="0g2x8d"
kg ↔ g
l  ↔ ml
piece ↔ piece
```

The database stores normalized quantities according to the system's measurement model.

Unit conversion must be deterministic.

---

# 11. Recipe Version

Every change to a Recipe creates a new Recipe Version.

A Recipe Version must have:

* UUID;
* Recipe UUID;
* version number;
* status;
* component definitions;
* output definition;
* effective boundaries;
* creation metadata.

Existing versions must not be modified after becoming historical.

---

# 12. Recipe Version Number

Versions are ordered within a Recipe.

Example:

```text id="q2k6w1"
Recipe A
 ├── Version 1
 ├── Version 2
 └── Version 3
```

Version numbers must be unique within the Recipe.

Recommended constraint:

```text
UNIQUE(recipe_id, version_number)
```

---

# 13. Recipe Version Lifecycle

Conceptual lifecycle:

```text id="s7h2x9"
Draft
  ↓
Pending Approval
  ↓
Approved
  ↓
Active
  ↓
Archived
```

A version may be rejected before activation.

Rejected versions remain available as history when required by audit policy.

---

# 14. Recipe Draft

Draft versions may be edited before approval.

Draft changes must not affect:

* current active Recipe;
* active menu;
* current POS calculations;
* historical Orders.

Draft is configuration work, not operational state.

---

# 15. Recipe Approval

New or changed Recipes require approval before becoming operational.

The approval record should identify:

* approving employee;
* approval timestamp;
* approved version;
* approval result;
* optional comment.

Approval history must not be overwritten.

---

# 16. Recipe Approval Authority

Approval must be controlled by permission.

The database stores the approval state and actor.

Application authorization determines whether the employee may approve.

A normal employee must not be able to approve a Recipe merely by changing a database-visible status.

---

# 17. Recipe Effective Boundary

Approved Recipe changes become effective from the next Cash Session according to the established configuration rule.

Conceptually:

```text id="x9z2m5"
Current Cash Session
       ↓
Old Recipe Version

Next Cash Session
       ↓
New Recipe Version
```

This prevents a live session from unexpectedly changing its operational configuration.

---

# 18. Effective Recipe Version

At any point, the system must be able to determine the effective Recipe Version for:

* Business;
* Branch;
* Cash Session;
* Order;
* Inventory operation.

The effective version must be deterministic.

---

# 19. Branch Scope

Recipes are Business-level definitions.

The same approved Recipe may be used by multiple Branches.

Branch-specific usage may still depend on:

* Product availability;
* Branch menu configuration;
* inventory;
* equipment;
* permissions.

---

# 20. Recipe Component Scope

Recipe components must belong to the same Business as the Recipe.

Example:

```text id="w5x7m4"
Business A
 ├── Recipe
 ├── Meat
 ├── Mayonnaise
 └── Spices
```

A Recipe from Business A cannot consume a Product from Business B.

---

# 21. Self-Reference Prevention

A Product must not directly consume itself.

Invalid:

```text id="d7v2q4"
Burger
 ↓
Burger
```

The database/application validation must reject direct self-reference.

---

# 22. Circular Recipe Prevention

Indirect cycles must also be prevented.

Invalid example:

```text id="m6y1p8"
A
 ↓
B
 ↓
C
 ↓
A
```

Cycle detection is primarily an application/domain validation responsibility.

The database should support constraints and transaction validation needed to prevent invalid active configurations.

---

# 23. Raw Material Recipe Component

Raw Materials may be consumed directly.

Example:

```text id="e3n7k2"
Lavash
 ├── Flour
 ├── Water
 └── Salt
```

Raw Material consumption is linked to inventory movement during production or sale.

---

# 24. Semi-Finished Recipe Component

Semi-Finished Products may be consumed by another Recipe.

Example:

```text id="g8c5p1"
Lavash
   ↓
Prepared Meat
```

This allows multi-level production.

---

# 25. Semi-Finished Production

When a Semi-Finished Product is produced:

1. component inventory is consumed;
2. output quantity is recorded;
3. actual output may differ from expected output;
4. yield/loss is recorded;
5. resulting inventory is increased.

The production transaction must be atomic.

---

# 26. Yield

A Recipe Version may define expected yield.

Example:

```text id="p5q8r2"
Input:
10 kg raw material

Expected output:
8.5 kg

Expected yield:
85%
```

Yield must be stored as configuration, while actual production results belong to inventory transaction data.

---

# 27. Loss / Shrinkage

Recipes may support expected loss or shrinkage.

Example:

```text id="x4m7k9"
Expected loss = 5%
```

Loss configuration must not silently alter historical production transactions.

Actual loss belongs to the production/inventory transaction.

---

# 28. Actual Production

Actual production must record:

* Recipe Version;
* output Product;
* planned quantity;
* actual quantity;
* component consumption;
* loss/shrinkage;
* Branch;
* employee;
* device;
* timestamp;
* transaction UUID.

Historical production must not depend on the current Recipe Version.

---

# 29. Recipe Snapshot in Inventory Transactions

When a Recipe is used for an inventory transaction, the transaction should preserve the relevant Recipe Version.

This ensures that later Recipe changes do not rewrite historical inventory movements.

---

# 30. Recipe Snapshot in Orders

If an Order consumes inventory based on a Recipe, the Order/Inventory transaction must preserve the effective Recipe Version reference.

The current Recipe must never be used retroactively to reinterpret a historical Order.

---

# 31. Recipe Component Snapshot

Operational inventory consumption should preserve enough information to reconstruct what was consumed.

Recommended snapshot information includes:

* Recipe UUID;
* Recipe Version UUID;
* component Product UUID;
* component quantity;
* unit;
* effective configuration version.

---

# 32. Recipe Change

A Recipe change must create a new Recipe Version.

Examples:

```text id="k2v7m4"
Version 1:
Meat 100 g

Version 2:
Meat 120 g
```

Version 1 remains immutable.

Version 2 becomes active only after approval and effective-boundary rules are satisfied.

---

# 33. Recipe Component Addition

Adding a component creates a new Recipe Version.

The previous version remains unchanged.

---

# 34. Recipe Component Removal

Removing a component creates a new Recipe Version.

The previous version remains historically available.

---

# 35. Recipe Quantity Change

Changing component quantity creates a new Recipe Version.

The old quantity must remain visible in historical configuration.

---

# 36. Recipe Output Change

Changing expected output creates a new Recipe Version.

The old output definition remains immutable.

---

# 37. Recipe Archive

A Recipe may be archived when the associated Product no longer uses it.

Archiving must not delete:

* Recipe;
* Recipe Versions;
* approval history;
* inventory references;
* Order references;
* audit history.

---

# 38. Product Archive and Recipe

Archiving a Product does not require deleting its Recipe.

The Recipe remains available for historical reconstruction.

A new operational sale must not use an inactive Product.

---

# 39. Recipe Version Activation

Only one Recipe Version should be operationally effective for a given Recipe and effective scope at a given point in time.

The database/application must prevent ambiguous overlapping active versions.

---

# 40. Configuration Versioning

Recipe Versioning is separate from general Configuration Versioning.

Recipe Version answers:

> What recipe definition is this?

Configuration Version answers:

> Which business configuration is effective for this operational context?

Both references may be required for historical reconstruction.

---

# 41. Recipe and Menu

An approved Recipe may be associated with a Product used in the global menu.

Recipe approval does not automatically mean that every Branch can sell the Product.

Branch availability remains separately controlled.

---

# 42. Recipe and Branch Menu

Branch menu configuration determines whether a Product is available in a Branch.

Recipe validity is a prerequisite for recipe-dependent operations but does not replace Branch menu configuration.

---

# 43. Recipe and Inventory

Recipe consumption produces inventory movements.

Conceptually:

```text id="z5m1q6"
Recipe
   ↓
Inventory Transaction
   ↓
Component Stock Decrease
```

Production additionally creates output stock.

---

# 44. Recipe and Order Acceptance

When an Order is Accepted:

1. the effective Recipe Version is determined;
2. required stock is validated;
3. stock is deducted atomically;
4. Order becomes Accepted only if the required inventory transaction succeeds.

If inventory validation fails, the Order must not become Accepted.

---

# 45. Recipe and Order Modification

If an Accepted Order is modified:

* quantity increases require additional stock;
* quantity reductions may return inventory if explicitly selected;
* product removal may return inventory if explicitly selected;
* insufficient stock rejects the entire modification.

Recipe Version used by the original consumption must remain historically identifiable.

---

# 46. Recipe and Set

A Set is separate from a Recipe.

A Set defines a stable combination of Products.

A Recipe defines production/consumption composition.

Changing a Recipe must not silently rewrite Set composition.

---

# 47. Recipe and Pricing

Recipe changes may affect cost calculations.

However, changing a Recipe must not silently rewrite historical selling prices.

Historical Orders preserve their transaction-time prices.

---

# 48. Recipe Cost

Recipe cost may be calculated from component costs.

The exact costing mechanism belongs to Inventory/Costing logic.

Recipe data must provide deterministic component quantities required for costing.

---

# 49. Recipe Approval History

Approval history should include:

* Recipe Version UUID;
* actor;
* action;
* timestamp;
* previous state;
* new state;
* comment/reason where applicable.

Approval history must be append-only.

---

# 50. Recipe Audit

Important Recipe events should generate Audit records:

* creation;
* component addition;
* component removal;
* quantity change;
* output change;
* submission;
* approval;
* rejection;
* activation;
* archival;
* restoration.

Audit is separate from Recipe version history.

---

# 51. Recipe Database Structure

Recommended logical entity set:

```text id="u6w2f9"
Recipe
   │
   ├── RecipeVersion
   │       │
   │       ├── RecipeComponent
   │       │        └── Product
   │       │
   │       └── RecipeApproval
   │
   └── Product
```

Related operational entities:

```text id="m4p7x2"
RecipeVersion
   ├── InventoryTransaction
   ├── OrderItem
   ├── Configuration
   └── AuditEvent
```

---

# 52. Suggested Core Fields

## Recipe

```text id
business_id
product_id
status
created_at
updated_at
archived_at
version
```

## RecipeVersion

```text id
recipe_id
version_number
status
output_quantity
output_unit_id
expected_yield
expected_loss_percent
effective_from
effective_to
created_by_employee_id
created_at
approved_by_employee_id
approved_at
version
```

## RecipeComponent

```text id
recipe_version_id
component_product_id
quantity
unit_id
sort_order
created_at
```

## RecipeApproval

```text id
recipe_version_id
action
actor_employee_id
comment
created_at
```

The final physical schema may normalize additional metadata.

---

# 53. Database Constraints

Recommended constraints include:

```text id="2r9y5m"
UNIQUE(recipe_id, version_number)
```

and Business consistency constraints ensuring:

```text id="v7m3q1"
Recipe.business_id
=
Recipe.product.business_id
```

and:

```text id="n5k8x2"
RecipeComponent.product.business_id
=
Recipe.business_id
```

Where practical, composite foreign keys should enforce tenant consistency.

---

# 54. Indexing

Important indexes include:

* Recipe by Business;
* Recipe by Product;
* RecipeVersion by Recipe;
* active RecipeVersion;
* RecipeComponent by RecipeVersion;
* RecipeComponent by Product;
* approval history by RecipeVersion;
* effective Recipe lookup;
* Branch/Business operational lookup.

POS and inventory queries must not require scanning historical Recipe Versions.

---

# 55. Concurrency

Recipe changes may happen while POS operations are active.

The system must prevent:

* stale Recipe Version activation;
* duplicate version numbers;
* concurrent activation of incompatible versions;
* changing an already immutable version.

Optimistic concurrency or row locking should be used where required.

---

# 56. Offline Recipe Configuration

Trusted offline devices may operate using the latest valid synchronized Recipe configuration.

Offline devices must not invent or modify active Recipe Versions without the required workflow.

New Recipe approval remains subject to server-side validation.

After reconnection:

1. offline transactions synchronize;
2. transaction configuration is validated;
3. configuration updates synchronize;
4. conflicts are handled explicitly.

---

# 57. Recipe Configuration Conflict

If an offline device uses an older but still valid Recipe Version, the server must determine whether the transaction was valid at the time of operation.

A later Recipe Version must not automatically invalidate a previously valid offline transaction.

Historical transaction state remains immutable.

---

# 58. Recipe Deletion

Physical Recipe deletion should not be allowed when historical references exist.

Archive instead.

The same principle applies to Recipe Versions.

---

# 59. Data Lifecycle

Recipe data follows Business lifecycle rules.

During Business expiration:

* Recipe data remains readable;
* modifying Recipe operations are blocked;
* history remains available.

During Business deletion:

* Recipe data is deleted according to dependency-aware lifecycle processing;
* deletion is idempotent;
* stale offline events cannot recreate Recipe data.

---

# 60. Performance

Recipe reads are frequent during:

* POS product selection;
* Order acceptance;
* inventory validation;
* costing;
* production.

Therefore:

* active versions should be efficiently indexed;
* component lookup should be fast;
* historical versions should not burden normal operational queries;
* effective configuration may be cached;
* cache must not become authoritative.

---

# 61. Database vs Application Responsibilities

### Database responsibilities

* Recipe identity;
* Business ownership;
* Product references;
* version uniqueness;
* referential integrity;
* immutable historical rows;
* basic state constraints.

### Application responsibilities

* Recipe validation;
* cycle detection;
* approval authorization;
* effective-date rules;
* yield calculations;
* production logic;
* inventory consumption;
* Recipe activation;
* configuration conflict handling.

---

# 62. Core Invariants

The following invariants are mandatory:

1. Every Recipe belongs to exactly one Business.
2. Every Recipe references a Product from the same Business.
3. Every Recipe Version belongs to exactly one Recipe.
4. Recipe UUID is immutable.
5. Recipe Version UUID is immutable.
6. Recipe Version numbers are unique within a Recipe.
7. Historical Recipe Versions are immutable.
8. Draft Recipe Versions may be edited before approval.
9. Active Recipe Versions cannot be silently rewritten.
10. Every Recipe Version has a defined output quantity.
11. Every Recipe Version has an output unit.
12. Recipe component quantities are deterministic.
13. Recipe components reference Products from the same Business.
14. Cross-Business Recipe components are forbidden.
15. Direct Product self-reference is forbidden.
16. Indirect Recipe cycles are forbidden for active configurations.
17. Raw Materials may be recipe inputs.
18. Semi-Finished Products may be recipe inputs.
19. Finished Products may have Recipes.
20. Recipe changes create new versions.
21. Component additions create new versions.
22. Component removals create new versions.
23. Quantity changes create new versions.
24. Output changes create new versions.
25. Expected yield changes create new versions.
26. Expected loss changes create new versions.
27. Recipe approval is permission-controlled.
28. Approval history is append-only.
29. Recipe activation follows the effective configuration boundary.
30. Only one effective Recipe Version exists for a Recipe at a given scope/time.
31. Branches may use the same Business-level Recipe.
32. Branch menu availability remains separate from Recipe validity.
33. Product inactivity prevents new normal sales.
34. Product archival does not erase Recipe history.
35. Recipe archival does not erase Recipe Versions.
36. Historical Orders retain the Recipe Version required for reconstruction.
37. Historical inventory transactions retain the Recipe Version used.
38. Current Recipe changes do not rewrite historical transactions.
39. Recipe configuration does not rewrite historical selling prices.
40. Recipe is separate from Set composition.
41. Recipe changes do not silently rewrite Set composition.
42. Production consumption is transactional.
43. Production output is transactional.
44. Actual production results are separate from expected Recipe values.
45. Actual loss belongs to transaction data.
46. Recipe cost calculations use deterministic component quantities.
47. Last Purchase Cost remains separate from Recipe identity.
48. Recipe approval does not automatically enable Branch sales.
49. Recipe queries are Business-scoped.
50. Recipe components are Business-scoped.
51. Client-supplied Business IDs cannot bypass isolation.
52. Historical Recipe data remains readable during subscription read-only state.
53. Recipe modification is blocked when subscription entitlement does not allow it.
54. Offline devices use only valid synchronized Recipe configuration.
55. Offline transactions preserve the Recipe Version used.
56. Later Recipe versions do not invalidate previously valid transactions.
57. Configuration conflicts are explicit.
58. Recipe version activation is concurrency-safe.
59. Duplicate Recipe Version numbers are forbidden.
60. Cache is not authoritative for Recipe state.
61. Recipe history is auditable.
62. Recipe UUIDs are never reused.
63. Product UUIDs referenced by historical Recipe Versions are never rewritten.
64. Recipe deletion follows Business data lifecycle rules.
65. Stale offline events cannot resurrect deleted Recipe data.

---

## Related Documents

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
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
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

