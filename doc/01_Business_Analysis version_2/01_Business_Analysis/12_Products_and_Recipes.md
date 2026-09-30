# Products and Recipes

**Document ID:** FF-BA-012
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for products, recipes, semi-finished products, finished products, recipe components, Sets, recipe approval, recipe modification, product availability, and recipe lifecycle management.

The goal is to ensure that products and their recipes provide a consistent basis for:

* menu management;
* inventory consumption;
* semi-finished product preparation;
* order processing;
* pricing;
* branch operations;
* reporting;
* historical traceability.

Product and recipe changes must preserve historical integrity and must not silently rewrite previous business transactions.

---

## 2. Product Model

A product represents an item managed by the FastFood ERP system.

Products may participate in:

* inventory;
* recipes;
* menus;
* orders;
* purchasing;
* preparation;
* reporting;
* Sets.

The system must distinguish between:

* the product itself;
* its configuration;
* its recipe;
* its current stock quantity;
* its current selling price;
* its availability state.

A product remains the same business entity even when:

* its stock changes;
* its price changes;
* its menu availability changes;
* its recipe changes;
* it is temporarily unavailable;
* it becomes inactive.

Historical transactions must continue to reference the applicable historical product configuration.

---

## 3. Product Types

The system supports three primary product types.

### 3.1. Raw Material

A raw material is an ingredient used directly or indirectly in food preparation.

Examples:

* meat;
* flour;
* mayonnaise;
* vegetables;
* spices.

A raw material normally acts as an input to a recipe rather than a sellable menu product.

---

### 3.2. Semi-Finished Product

A semi-finished product is prepared in advance and can be used as an ingredient in another product.

Example:

```text
Prepared Meat
├── Meat
├── Mayonnaise
└── Spices
```

A semi-finished product may itself have a recipe.

This allows the system to represent dependencies between products.

Semi-finished preparation creates inventory with the source:

`Prepared in Branch`

---

### 3.3. Finished Product

A finished product is a product that can be offered through the restaurant menu.

A finished product may contain:

* raw materials;
* semi-finished products;
* both.

A finished product may also be used as a component of a Set where applicable.

---

## 4. Product Identity

Every product must have a unique system-generated product code.

The system generates the code automatically.

Employees should not be required to manually create product codes.

Product identity must remain stable across the product lifecycle.

Historical transactions must continue to reference the same product identity even if its configuration changes later.

Changing a product's:

* price;
* recipe;
* category;
* availability;
* active/inactive state

must not create ambiguity about the identity of historical transactions.

---

## 5. Product Information

A product should contain the information necessary for normal restaurant operations.

Relevant information may include:

* product name;
* product type;
* product code;
* unit of measurement;
* category;
* recipe status;
* menu status;
* availability status;
* pricing information;
* branch availability where applicable.

The system must avoid requiring unnecessary information that does not contribute to the current business process.

---

## 6. Product Category

Each product belongs to exactly one category.

A product must not belong to multiple categories simultaneously.

Category changes must not destroy:

* product identity;
* inventory history;
* order history;
* recipe history.

Historical records must remain associated with the original product identity.

---

## 7. Product Recipe Relationship

A product may have a recipe.

A recipe defines the components and quantities required to produce or sell the product.

For example:

```text
Lavash
├── Bread
├── Meat
├── Sauce
└── Vegetables
```

The recipe is the business definition used to determine inventory consumption.

A product with a recipe must retain the relationship between:

* product;
* recipe;
* recipe version;
* recipe components;
* required quantities.

---

## 8. Recipe Components

A recipe may contain:

* raw materials;
* semi-finished products.

Recipe components must have:

* defined quantities;
* compatible measurement units;
* a defined product identity.

Example:

```text
Semi-Finished Sauce
├── Mayonnaise
├── Spices
└── Other approved ingredients
```

The system must prevent invalid recipe configurations that cannot be meaningfully converted or consumed.

A recipe must not create circular dependencies such as a product directly or indirectly depending on itself.

---

## 9. Nested Recipe Dependencies

A semi-finished product may be a component of another recipe.

For example:

```text
Finished Product
       ↓
Semi-Finished Product
       ↓
Raw Materials
```

The system must preserve these relationships.

Inventory consumption must be traceable through the dependency chain.

The system must not lose the relationship between a finished product and the raw materials required through a semi-finished product.

---

## 10. Recipe Quantity

Each recipe component must have a defined quantity.

The quantity represents the amount required according to the recipe definition.

For example:

```text
Prepared Meat:
- Meat: 1 kg
- Mayonnaise: 200 g
- Spices: configured quantity
```

Recipe quantities must use compatible measurement units.

The system must preserve the defined unit and quantity as part of the recipe version.

---

## 11. Recipe Approval

New recipes must be approved before becoming part of the active global product/menu configuration.

Recipe creation and recipe approval are separate business actions.

An employee may create or modify a recipe if they have the appropriate permission, but creation or modification does not automatically make the new recipe active.

The business Owner is responsible for approval unless the relevant authority has explicitly been delegated through the permission model.

The approval requirement exists to protect:

* inventory consumption;
* pricing;
* operational consistency;
* historical traceability.

---

## 12. Recipe Modification

Recipe modification requires the appropriate dedicated permission.

Authorized users may modify:

* recipe components;
* component quantities;
* recipe configuration.

Recipe modification must not silently rewrite historical transactions.

Existing orders and historical inventory operations must preserve the recipe-related state applicable when those operations occurred.

---

## 13. Recipe Change Lifecycle

A typical recipe change follows this process:

```text
Existing Active Recipe
        ↓
Modification
        ↓
Pending Recipe Version
        ↓
Owner / Authorized Approval
        ↓
Approved Recipe Version
        ↓
Effective Next Cash Session
        ↓
Future Operations Use New Recipe
```

The system must not apply an unapproved recipe modification to normal production or order operations.

An approved recipe change does not immediately rewrite an already-open cash session's historical operating configuration.

---

## 14. Recipe Effective Time

Approved recipe changes become effective from the **next applicable cash session**.

Therefore:

* the current cash session continues using its applicable recipe configuration;
* a newly opened cash session uses the newly effective approved recipe;
* historical orders remain associated with the recipe applicable when they were processed;
* inventory transactions are not recalculated because a recipe later changed.

This rule prevents mid-session recipe changes from creating inconsistent inventory behavior.

---

## 15. Recipe History

Previous recipes must remain available as historical records.

When a recipe changes, the previous recipe configuration must not be destroyed.

The system must preserve enough information to determine:

* what the previous recipe contained;
* what the new recipe contains;
* when the change was created;
* when it was approved;
* when it became effective;
* who made the change;
* who approved the change;
* why the change was made, where a reason is required.

---

## 16. Recipe Versioning

Recipe changes must create a new historical state rather than silently replacing the old state.

For business purposes, the system must be able to distinguish between:

* previous recipe versions;
* current active recipe version;
* pending recipe versions;
* approved but not yet effective recipe versions, where applicable.

Historical orders and inventory operations must remain associated with the recipe state applicable at that time.

Recipe versions are immutable after becoming part of historical business transactions.

---

## 17. Global Recipes

Approved recipes are managed at the business level.

The same approved recipe definition applies across the business's branches.

Branches must not independently create conflicting versions of the same global recipe.

A branch may use the approved product according to its branch menu availability and permissions.

This ensures consistent inventory consumption across branches.

---

## 18. Branch Menu Availability

A product may become available to permitted branch menus after the required product and recipe configuration has been approved.

The recipe definition itself remains part of the business-level product configuration.

Branch-level menu availability determines whether the product can be offered at a particular branch.

The branch does not create a separate recipe merely because the product is enabled there.

---

## 19. Recipe Visibility

Recipe access is controlled separately from general menu access.

An employee may be allowed to:

* view a menu product;
* process an order;
* manage inventory;

without being allowed to view the complete recipe.

Recipe visibility therefore requires a dedicated permission.

This separation protects operationally sensitive recipe information.

---

## 20. Recipe Modification Permission

Viewing recipes and modifying recipes are separate capabilities.

An employee may have permission to view recipes without having permission to change them.

Recipe modification must require explicit permission.

Recipe approval is also a separately controlled action.

Permission enforcement must apply consistently across:

* normal online operation;
* offline operation;
* branch access;
* management interfaces.

---

## 21. Semi-Finished Product Recipe

Semi-finished products may have their own recipes.

For example:

```text
Prepared Meat
├── Raw Meat
├── Mayonnaise
└── Spices
```

When the semi-finished product is prepared, the system consumes the recipe components and creates the resulting semi-finished stock.

The resulting inventory must identify the stock as:

`Prepared in Branch`

Detailed inventory behavior is defined in:

`11_Inventory_and_Warehouse.md`

---

## 22. Semi-Finished Product as a Recipe Component

A semi-finished product can be used in another recipe.

Example:

```text
Lavash
├── Bread
├── Prepared Meat
└── Vegetables
```

The system must preserve the dependency chain.

When inventory requirements are calculated, the system must be able to resolve the underlying recipe dependencies according to the applicable preparation and inventory rules.

The finished product must not lose traceability to the raw materials required through the semi-finished product.

---

## 23. Semi-Finished Production Output

When a semi-finished product is prepared, the actual resulting quantity must be recorded.

The system must not assume that the theoretical recipe output is always equal to the actual production output.

If the recipe defines a standard output quantity, component consumption must scale proportionally according to the actual output.

Example:

```text
Standard Recipe Output: 10 kg
Actual Output:          5 kg

Required component quantities:
5 kg / 10 kg = 50%

Component consumption:
Standard quantity × 50%
```

The resulting inventory quantity is the actual output quantity.

Preparation history must preserve:

* recipe version;
* planned/standard output where applicable;
* actual output;
* consumed components;
* responsible employee;
* branch;
* preparation time;
* applicable shrinkage/loss information.

---

## 24. Shrinkage and Preparation Loss

Prepared products may have a configured shrinkage/loss percentage.

The system must support a configured shrinkage/loss percentage for prepared items.

The configured loss may be used to determine expected usable output from preparation.

Actual production output remains the authoritative resulting stock quantity.

The system must preserve the preparation transaction and the applicable loss information in history.

---

## 25. Recipe and Inventory Consumption

The active approved recipe determines the inventory components required by normal operations.

For an accepted order:

1. the system identifies the applicable product;
2. the system identifies the recipe version effective for the current cash session;
3. required components are resolved;
4. inventory availability is checked;
5. inventory is deducted atomically if sufficient stock exists.

The system must not create negative inventory.

If required inventory is insufficient, the applicable operation must be blocked.

Detailed inventory behavior is defined in:

`11_Inventory_and_Warehouse.md`

---

## 26. Recipe Component Removal

During order customization, authorized users may remove supported recipe components.

Removing a component must:

* reduce the applicable inventory requirement;
* remain recorded as part of the order customization;
* affect price according to the configured business pricing rules where the component has a price impact.

Example:

```text
Base Product
+ Full Recipe
      ↓
Customer removes component
      ↓
Modified Order Configuration
      ↓
Reduced Inventory Requirement
      ↓
Applicable Price Adjustment
```

The base recipe itself is not modified.

The customization applies only to the relevant order unit.

---

## 27. Recipe Component Addition

Supported extras or add-ons may be added to an order.

When an extra is added:

* the order price must update according to the applicable pricing rule;
* inventory consumption must reflect the added quantity where applicable;
* the order must retain the customization history.

Extras do not automatically modify the base product recipe.

---

## 28. Ingredient Quantity Increase

A supported recipe component may be increased for a specific order unit where the business permits it.

When the quantity is increased:

* the base recipe remains unchanged;
* the additional quantity creates an additional inventory requirement;
* the additional inventory must be validated before acceptance;
* the applicable price adjustment is calculated according to the configured pricing rules.

If the additional required inventory is unavailable, the entire modification must be rejected.

No partial modification or partial inventory deduction is allowed.

---

## 29. Unit-Level Customization

Each unit of the same product within one order may have different customization.

For example:

```text
2 × Lavash

Unit 1:
- normal sauce

Unit 2:
- no sauce
- extra meat
```

The system must calculate inventory and price effects for each customized unit independently where the configurations differ.

The current business model does not require an **Apply to All** customization action.

---

## 30. Component Swapping

The current system does not support direct component swapping.

For example:

```text
Remove A
Add B
```

must not automatically be treated as a recipe substitution mechanism.

Supported customization is based on:

* removing supported components;
* increasing supported component quantities;
* adding supported extras;
* comments for non-recipe changes.

Future product customization models may expand this behavior if required.

---

## 31. Non-Recipe Changes

Not every operational customization requires a recipe modification.

If a requested change is not represented as a supported recipe component or extra, it may be recorded as an order comment.

Such a comment does not change:

* the official product recipe;
* the global recipe version;
* the product configuration.

This distinction prevents individual customer requests from permanently changing the business recipe.

---

## 32. Recipe and Pricing

Recipe configuration may affect product pricing where recipe components have defined price contributions.

Recipe changes made by authorized users may affect future pricing behavior.

Historical order prices must not be recalculated when the recipe changes later.

Order-level customization pricing is separate from changing the base recipe.

Where the business uses cost-based custom markup, the applicable inventory cost reference may use **Last Purchase Cost** according to the pricing rules defined in:

`13_Menu_and_Pricing.md`

---

## 33. Recipe and Menu

Products may be included in the global menu after the required product and recipe configuration has been approved.

The menu determines whether a product is available for sale at a branch.

Recipe status and menu status are related but separate concepts.

A product may exist in the product catalog without being currently available for sale.

---

## 34. Product Availability

A product may have an operational availability state.

A product can temporarily become unavailable without being deleted.

One supported reason is:

**Equipment Broken**

This allows the restaurant to prevent normal use of the product while preserving:

* product identity;
* recipe;
* historical orders;
* inventory history;
* reports.

Equipment Broken is an operational availability state, not a deletion or archive operation.

---

## 35. Inactive Products

A product may be marked inactive.

An inactive product:

* must not appear as a normal sellable menu item;
* must not be available for new normal sales;
* remains available in historical records;
* retains its product and recipe history.

Inactive state must not destroy historical references.

---

## 36. Product Archive

Products that are no longer actively used should be archived rather than physically deleted when historical relationships exist.

Archiving should prevent inappropriate future use while preserving historical information.

Archived products must remain available for historical reporting where required.

---

## 37. Products with Recipes Cannot Be Deleted

A product that has an active or historical recipe relationship must not be physically deleted in a way that destroys recipe or transaction history.

The system must preserve:

* product identity;
* recipe history;
* inventory history;
* order history;
* audit history.

Archiving is the appropriate lifecycle mechanism.

---

## 38. Recipe Archive

Old recipes must be archived when replaced by a new approved recipe.

Archiving must preserve historical information.

An archived recipe must not automatically become the active recipe for new operations.

Historical transactions may continue to reference the archived recipe state.

---

## 39. Set Products

A Set is a separate product configuration representing a bundle of component products.

A Set has:

* its own product identity;
* its own selling price;
* a defined component composition;
* its own availability state.

A Set is not a replacement for the recipes of its component products.

---

## 40. Set Composition

A Set contains a defined list of component products.

The component composition is stable for the applicable Set configuration.

The customer cannot replace one Set component with another product during normal order processing.

Direct component swapping is therefore not supported for Sets.

If a mandatory component is unavailable, the Set cannot be sold.

---

## 41. Set Inventory Consumption

When a Set is sold, inventory consumption must be calculated from its configured component products.

Each component product is resolved according to its applicable product and recipe configuration.

The system must preserve the relationship:

```text
Set
 ↓
Component Product
 ↓
Component Recipe
 ↓
Inventory Requirements
```

The resulting inventory deductions must be associated with the Set sale and must remain traceable.

---

## 42. Set Configuration Versioning

A Set composition must not be silently changed in place when historical orders depend on the previous composition.

When Set composition changes:

1. a new Set configuration/version is created;
2. the new configuration requires the applicable approval;
3. the new configuration becomes effective from the next applicable cash session;
4. future orders use the new configuration;
5. historical orders retain the previous configuration.

Changing the underlying recipe of a component product does not automatically change the historical Set composition.

---

## 43. Historical Transaction Protection

Changing a product or recipe must not rewrite historical business transactions.

Historical orders must preserve the relevant information from the time the order was processed.

Historical inventory operations must preserve:

* product identity;
* applicable recipe version;
* applicable Set configuration where relevant;
* actual quantities;
* customization;
* inventory effects.

Current product configuration must not retroactively alter historical transactions.

---

## 44. Recipe Approval and Branch Consistency

Once a recipe is approved at the business level, branches using that product must use the approved recipe configuration.

Branches must not independently modify the same global recipe without the required business-level approval process.

This prevents different branches from silently consuming different quantities for the same global product.

Branch-specific selling price or menu availability does not create a branch-specific recipe.

---

## 45. Offline Recipe Behavior

Offline devices may continue using the latest valid recipe configuration available to them under their valid offline authorization.

Offline operation must not allow an unauthorized employee to:

* modify a recipe;
* approve a recipe;
* bypass subscription entitlement;
* bypass recipe permissions.

An approved recipe change becomes available to offline devices according to the synchronization and offline-configuration rules.

The server becomes authoritative after synchronization.

---

## 46. Recipe Synchronization

When recipe-related changes are synchronized, the system must preserve:

* recipe identity;
* recipe version;
* business identity;
* responsible employee;
* approval information;
* creation timestamp;
* effective timestamp;
* change history.

Duplicate synchronization must not create duplicate recipe changes.

Conflicting recipe changes must be handled according to the centralized business and synchronization rules.

A synchronized historical recipe version must not be silently overwritten by another version.

---

## 47. Permissions and Subscription

Recipe functionality is subject to two independent control layers:

1. subscription entitlement;
2. employee permissions.

A user may access a recipe function only when:

* the business subscription permits the relevant functionality; and
* the employee has the required permission.

These controls apply independently.

A trusted device does not grant recipe permissions.

Offline authorization must not bypass either control.

---

## 48. Branch Scope

Product and recipe operations must respect branch scope.

Global recipes are business-level configurations, while actual product availability and inventory usage are branch-specific.

An employee's access to a branch does not automatically grant permission to modify global recipes.

Branch-level menu access does not create a separate recipe.

---

## 49. Auditability

Important product and recipe changes must be traceable.

The system should preserve:

* actor;
* timestamp;
* business;
* branch where applicable;
* product;
* recipe;
* recipe version;
* previous state;
* new state;
* action type;
* approval information;
* effective time;
* reason/comment where required.

Historical states must remain available for audit and reporting.

No important recipe change should silently overwrite its previous state.

---

## 50. Reporting

Product and recipe information may contribute to:

* inventory reports;
* product reports;
* menu reports;
* order reports;
* recipe history;
* inventory consumption analysis;
* product availability reports;
* Set configuration history.

Historical reports must use the relevant historical product, recipe, and Set configuration state.

Current product configuration must not retroactively change historical reporting.

---

## 51. Performance Requirements

Recipe and product operations must remain lightweight enough for normal restaurant hardware.

Common POS operations must not require expensive recalculation when a product is selected.

Recipe calculations should be efficient enough that normal order processing remains responsive.

The system should support nested recipe dependencies without making normal POS operation noticeably slow.

Frequently used product and recipe configuration should be available efficiently to the POS while preserving server authority and synchronization rules.

---

## 52. Business Rules Summary

| Area                        | Rule                                              |
| --------------------------- | ------------------------------------------------- |
| Product types               | Raw, semi-finished, finished                      |
| Product code                | Automatically generated                           |
| Product category            | Exactly one category                              |
| Product identity            | Stable                                            |
| Recipes                     | Define product components and quantities          |
| Recipe components           | Raw materials and semi-finished products          |
| Nested recipes              | Supported                                         |
| Circular recipe dependency  | Not allowed                                       |
| Recipe creation             | Separate from approval                            |
| Recipe approval             | Required before active use                        |
| Recipe modification         | Requires dedicated permission                     |
| Recipe approval authority   | Owner or explicitly authorized user               |
| Recipe history              | Preserved                                         |
| Recipe versioning           | Historical states retained                        |
| Recipe effective time       | Next applicable cash session                      |
| Global recipe               | Business-level                                    |
| Branch menu                 | Controls branch availability                      |
| Branch-specific recipe      | Not supported                                     |
| Recipe visibility           | Separate permission                               |
| Semi-finished products      | May have recipes                                  |
| Semi-finished output        | Actual output recorded                            |
| Production scaling          | Recipe scales proportionally to actual output     |
| Shrinkage                   | Supported                                         |
| Inventory consumption       | Based on applicable approved recipe               |
| Order deduction             | At Accepted state                                 |
| Negative stock              | Not allowed                                       |
| Component removal           | Supported                                         |
| Component quantity increase | Supported                                         |
| Component addition          | Supported through extras                          |
| Component swapping          | Not supported                                     |
| Unit-level customization    | Supported                                         |
| Apply to All                | Not required                                      |
| Non-recipe changes          | Recorded as order comments                        |
| Modification failure        | Entire modification rejected                      |
| Historical orders           | Must not be rewritten                             |
| Product availability        | Temporary unavailable state supported             |
| Equipment Broken            | Supported availability reason                     |
| Inactive product            | Not sellable, history retained                    |
| Product deletion            | Historical/recipe-dependent products are archived |
| Old recipes                 | Archived                                          |
| Sets                        | Separate bundle product                           |
| Set component swapping      | Not supported                                     |
| Set composition             | Versioned/stable                                  |
| Set composition changes     | Effective next applicable cash session            |
| Set unavailable component   | Set sale blocked                                  |
| Offline operation           | Latest valid configuration may be used            |
| Subscription                | Separate from employee permissions                |
| Audit                       | Important changes preserved                       |

---

## 53. Business Boundaries

The current Products and Recipes scope does **not** define:

* supplier management;
* nutritional information;
* allergen management;
* automatic recipe optimization;
* AI-generated recipes;
* branch-specific recipe variants;
* customer-specific recipe profiles;
* component substitution engines;
* advanced food-cost optimization;
* automatic procurement;
* barcode-based recipe operations.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 54. Related Documents

* `01_Product_Overview.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `16_Reports_and_Dashboards.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

