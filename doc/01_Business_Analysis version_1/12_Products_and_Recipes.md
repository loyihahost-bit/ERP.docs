# Products and Recipes

**Document ID:** FF-BA-012
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`
    
---

## 1. Purpose

This document defines the business requirements for products, recipes, semi-finished products, finished products, recipe components, recipe approval, recipe modification, and recipe lifecycle management.

The goal is to ensure that products and their recipes provide a consistent basis for:

* menu management;
* inventory consumption;
* semi-finished product preparation;
* order processing;
* pricing;
* branch operations;
* reporting;
* historical traceability.

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
* reporting.

The system must distinguish between the product itself and its current stock quantity.

A product remains the same business entity even when:

* its stock changes;
* its price changes;
* its menu availability changes;
* its recipe changes;
* it is temporarily unavailable.

---

## 3. Product Types

The system supports three primary product types.

### 3.1 Raw Material

A raw material is an ingredient used directly or indirectly in food preparation.

Examples:

* meat;
* flour;
* mayonnaise;
* vegetables;
* spices.

A raw material normally acts as an input to a recipe rather than a sellable menu product.

---

### 3.2 Semi-Finished Product

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

---

### 3.3 Finished Product

A finished product is a product that can be offered through the restaurant menu.

A finished product may contain:

* raw materials;
* semi-finished products;
* both.

---

## 4. Product Identity

Every product must have a unique system-generated product code.

The system generates the code automatically.

Employees should not be required to manually create product codes.

Product identity must remain stable across the product lifecycle.

Historical transactions must continue to reference the same product identity even if its configuration changes later.

---

## 5. Product Information

A product should contain the information necessary for normal restaurant operations.

Relevant information may include:

* product name;
* product type;
* product code;
* unit of measurement;
* recipe status;
* menu status;
* availability status;
* pricing information;
* branch availability where applicable.

The system must avoid requiring unnecessary information that does not contribute to the current business process.

---

## 6. Product Recipe Relationship

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
* recipe components;
* required quantities.

---

## 7. Recipe Components

A recipe may contain:

* raw materials;
* semi-finished products.

Recipe components must have defined quantities and appropriate units.

The system must support recipes with multiple components.

Example:

```text
Semi-Finished Sauce
├── Mayonnaise
├── Spices
└── Other approved ingredients
```

---

## 8. Nested Recipe Dependencies

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

## 9. Recipe Quantity

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

The system must prevent invalid recipe configurations that cannot be meaningfully converted or consumed.

---

## 10. Recipe Approval

New recipes must be approved before becoming part of the active global product/menu configuration.

Recipe creation and recipe approval are separate business actions.

The person creating or modifying a recipe does not automatically make the recipe active unless they also have the required authority to approve it.

The approval requirement exists to protect inventory, pricing, and operational consistency.

---

## 11. Recipe Modification

Recipe modification requires the appropriate permission.

Authorized users may modify:

* recipe components;
* component quantities;
* recipe configuration.

Recipe modification must not silently rewrite historical transactions.

Existing orders and historical inventory operations must preserve the recipe-related state applicable when those operations occurred.

---

## 12. Recipe Change Lifecycle

A typical recipe change follows this process:

```text
Existing Recipe
      ↓
Modification
      ↓
Approval
      ↓
New Active Recipe
      ↓
Future Operations Use New Recipe
```

The system must not apply an unapproved recipe modification to normal production or order operations.

---

## 13. Recipe History

Previous recipes must remain available as historical records.

When a recipe changes, the previous recipe configuration must not be destroyed.

The system must preserve enough information to determine:

* what the previous recipe contained;
* what the new recipe contains;
* when the change occurred;
* who made the change;
* who approved the change;
* why the change was made, where a reason is required.

---

## 14. Recipe Versioning

Recipe changes must create a new historical state rather than silently replacing the old state.

For business purposes, the system must be able to distinguish between:

* previous recipe;
* current active recipe;
* future or pending recipe changes, where applicable.

Historical orders and inventory operations must remain associated with the recipe state applicable at that time.

---

## 15. Global Recipes

Approved recipes are managed at the business level.

The same approved recipe definition applies across the business's branches unless a future business rule explicitly introduces branch-specific recipes.

Branches must not independently create conflicting versions of the same global recipe.

This ensures consistent inventory consumption across branches.

---

## 16. Branch Menu Availability

A recipe may become available to permitted branch menus after approval.

The recipe definition itself remains part of the business-level product configuration.

Branch-level menu availability determines whether the product can be offered at a particular branch.

The branch does not create a separate recipe merely because the product is enabled there.

---

## 17. Recipe Visibility

Recipe access is controlled separately from general menu access.

An employee may be allowed to:

* view a menu product;
* process an order;
* manage inventory;

without being allowed to view the complete recipe.

Recipe visibility therefore requires a dedicated permission.

This separation protects operationally sensitive recipe information.

---

## 18. Recipe Modification Permission

Viewing recipes and modifying recipes are separate capabilities.

An employee may have permission to view recipes without having permission to change them.

Recipe modification must require explicit permission.

Permission enforcement must apply consistently across:

* normal online operation;
* offline operation;
* branch access;
* management interfaces.

---

## 19. Semi-Finished Product Recipe

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

## 20. Semi-Finished Product as a Recipe Component

A semi-finished product can be used in another recipe.

Example:

```text
Lavash
├── Bread
├── Prepared Meat
└── Vegetables
```

In this situation, the system must follow the dependency chain when determining inventory requirements.

The finished product must not be treated as requiring only the semi-finished product itself if the business process requires the underlying components to be consumed through preparation.

---

## 21. Recipe and Inventory Consumption

The active approved recipe determines the inventory components required by normal operations.

When an order is processed:

1. the system identifies the applicable product;
2. the system determines its active recipe;
3. required components are calculated;
4. inventory availability is checked;
5. inventory is deducted if sufficient stock exists.

The system must not create negative inventory.

If required inventory is insufficient, the operation must be blocked according to the inventory rules.

---

## 22. Recipe Component Removal

During order customization, authorized users may remove supported recipe components.

Removing a component must:

* reduce the applicable product price when the component has an associated price impact;
* reduce the corresponding inventory requirement;
* remain recorded as part of the order customization.

Example:

```text
Product
+ Full Recipe
      ↓
Customer removes component
      ↓
Modified Recipe Requirement
      ↓
Lower Inventory Consumption
      ↓
Adjusted Price
```

The exact POS customization rules are defined in:

`08_POS_and_Order_Management.md`

---

## 23. Recipe Component Addition

Supported extras or add-ons may be added to an order.

When an extra is added:

* the order price must update accordingly;
* inventory consumption must reflect the added component where applicable;
* the order must retain the customization history.

Extras do not automatically modify the base product recipe.

---

## 24. Component Swapping

The current system does not support direct component swapping.

For example:

```text
Remove A
Add B
```

must not automatically be treated as a recipe substitution mechanism.

Supported customization is based on:

* removing supported components;
* adding supported extras;
* comments for non-recipe changes.

Future product customization models may expand this behavior if required.

---

## 25. Non-Recipe Changes

Not every operational customization requires a recipe modification.

If a requested change is not represented as a supported recipe component or extra, it may be recorded as an order comment.

Such a comment does not change the official product recipe.

This distinction prevents individual customer requests from permanently changing the business recipe.

---

## 26. Recipe and Pricing

Recipe configuration may affect product pricing where recipe components have defined price contributions.

When a supported component is removed during an order customization, the applicable price reduction must be calculated according to the configured business pricing rules.

Recipe changes made by authorized users may therefore affect future pricing behavior.

Historical order prices must not be recalculated when the recipe changes later.

---

## 27. Recipe and Menu

Products may be included in the global menu after the required recipe and product configuration has been approved.

The menu determines whether a product is available for sale at a branch.

Recipe status and menu status are related but separate concepts.

A product may exist in the product catalog without being currently available for sale.

---

## 28. Product Availability

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

---

## 29. Product Archive

Products that are no longer actively used should be archived rather than physically deleted when historical relationships exist.

Archiving should prevent inappropriate future use while preserving historical information.

Archived products must remain available for historical reporting where required.

---

## 30. Products with Recipes Cannot Be Deleted

A product that has an active or historical recipe relationship must not be physically deleted in a way that destroys recipe or transaction history.

The system must preserve the product and recipe history.

Archiving is the appropriate lifecycle mechanism.

---

## 31. Recipe Archive

Old recipes must be archived when replaced by a new approved recipe.

Archiving must preserve historical information.

An archived recipe must not automatically become the active recipe for new operations.

Historical transactions may continue to reference the archived recipe state.

---

## 32. Historical Transaction Protection

Changing a product or recipe must not rewrite historical business transactions.

Historical orders must preserve the relevant information from the time the order was processed.

Historical inventory operations must preserve the recipe/product state used at the time.

This ensures that reports remain consistent with the actual historical operation.

---

## 33. Recipe Approval and Branch Consistency

Once a recipe is approved at the business level, branches using that product should use the approved recipe configuration.

Branches must not independently modify the same global recipe without the required business-level approval process.

This prevents different branches from silently consuming different quantities for the same global product.

---

## 34. Offline Recipe Behavior

Offline devices may continue using the latest valid recipe configuration available to them under their valid offline authorization.

Offline operation must not allow an unauthorized employee to modify or approve recipes.

Recipe changes made while a device is offline must follow the same permission and synchronization rules as other protected business operations.

The server becomes authoritative after synchronization.

---

## 35. Recipe Synchronization

When recipe-related changes are synchronized, the system must preserve:

* recipe identity;
* version/state;
* business identity;
* responsible employee;
* approval information;
* timestamp;
* change history.

Duplicate synchronization must not create duplicate recipe changes.

Conflicting recipe changes must be handled according to the centralized business and synchronization rules.

---

## 36. Permissions and Subscription

Recipe functionality is subject to two independent control layers:

1. subscription entitlement;
2. employee permissions.

A user may access a recipe function only when:

* the business subscription permits the relevant functionality; and
* the employee has the required permission.

A trusted device or offline authorization must not bypass either control.

---

## 37. Auditability

Important product and recipe changes must be traceable.

The system should preserve:

* actor;
* timestamp;
* product;
* recipe;
* previous state;
* new state;
* action type;
* approval information;
* reason/comment where required.

Historical states must remain available for audit and reporting.

No important recipe change should silently overwrite its previous state.

---

## 38. Reporting

Product and recipe information may contribute to:

* inventory reports;
* product reports;
* menu reports;
* order reports;
* recipe history;
* inventory consumption analysis.

Historical reports must use the relevant historical product and recipe state.

Current product configuration must not retroactively change historical reporting.

---

## 39. Performance Requirements

Recipe and product operations must remain lightweight enough for normal restaurant hardware.

Common POS operations must not require expensive recalculation when a product is selected.

Recipe calculations should be efficient enough that normal order processing remains responsive.

The system should support nested recipe dependencies without making normal POS operation noticeably slow.

---

## 40. Business Rules Summary

| Area                   | Rule                                              |
| ---------------------- | ------------------------------------------------- |
| Product types          | Raw, semi-finished, finished                      |
| Product code           | Automatically generated                           |
| Recipes                | Define product components and quantities          |
| Recipe components      | Raw materials and semi-finished products          |
| Nested recipes         | Supported                                         |
| Recipe approval        | Required before active use                        |
| Recipe modification    | Requires dedicated permission                     |
| Recipe history         | Preserved                                         |
| Recipe versioning      | Historical states retained                        |
| Global recipe          | Business-level                                    |
| Branch menu            | Controls branch availability                      |
| Recipe visibility      | Separate permission                               |
| Semi-finished products | May have recipes                                  |
| Inventory consumption  | Based on active approved recipe                   |
| Negative stock         | Not allowed                                       |
| Component removal      | Supported during order customization              |
| Component addition     | Supported through extras                          |
| Component swapping     | Not currently supported                           |
| Non-recipe changes     | Recorded as order comments                        |
| Historical orders      | Must not be rewritten                             |
| Product availability   | Temporary unavailable state supported             |
| Equipment Broken       | Supported availability reason                     |
| Product deletion       | Historical/recipe-dependent products are archived |
| Old recipes            | Archived                                          |
| Offline operation      | Latest valid configuration may be used            |
| Subscription           | Separate from employee permissions                |
| Audit                  | Important changes preserved                       |

---

## 41. Business Boundaries

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

## 42. Related Documents

* `01_Product_Overview.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `11_Inventory_and_Warehouse.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `16_Reports_and_Dashboards.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

