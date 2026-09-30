# Inventory and Warehouse

**Document ID:** FF-BA-011
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for inventory and warehouse management in the FastFood ERP system.

The inventory system must provide accurate branch-level stock tracking for raw materials, semi-finished products, and finished products while maintaining consistency with recipes, orders, purchases, stock counts, and inventory adjustments.

The system must remain lightweight and practical for restaurant operations without introducing unnecessary operational complexity.

---

## 2. Inventory Model

Inventory is managed primarily at the branch level.

Each branch has its own warehouse and stock records.

The system must support:

* raw materials;
* semi-finished products;
* finished products;
* stock quantities;
* stock batches;
* purchase records;
* prepared stock;
* inventory adjustments;
* stock counts;
* inventory variances;
* low-stock and out-of-stock conditions;
* shopping lists;
* inventory history.

Inventory data must remain isolated between businesses and branches according to the user's authorized scope.

---

## 3. Branch Warehouse

Each branch may maintain its own warehouse.

A branch warehouse contains the inventory available for that branch's operations.

Branch inventory must not automatically become available to another branch.

Inventory operations must always be associated with:

* Business;
* Branch;
* Warehouse;
* Product;
* Quantity;
* Relevant transaction or adjustment;
* Responsible employee where applicable.

The current business model does not require multiple independent warehouses within a branch.

The architecture should not prevent future warehouse expansion, but multiple warehouses are not a current business requirement.

---

## 4. Product Types

The inventory system supports three primary product categories.

### 4.1 Raw Materials

Raw materials are ingredients or materials used directly or indirectly in production.

Examples include:

* meat;
* mayonnaise;
* flour;
* vegetables;
* spices.

### 4.2 Semi-Finished Products

Semi-finished products are prepared products that can be used as components of other products.

For example:

```text
Semi-Finished Product: Prepared Meat

Recipe:
- 1 kg meat
- 200 g mayonnaise
- spices
```

The system must preserve the relationship between the semi-finished product and its recipe components.

### 4.3 Finished Products

Finished products are products that can be sold through the restaurant menu.

A finished product may use:

* raw materials directly;
* semi-finished products;
* a combination of both.

---

## 5. Product Identity

Each inventory product must have a system-generated product code.

The product code is generated automatically by the system.

Products must also have sufficient identifying information for employees to distinguish them during:

* purchasing;
* inventory management;
* recipe configuration;
* stock counting;
* order processing;
* reporting.

Product identity must remain stable even when its stock quantity changes.

---

## 6. Stock Quantities and Units

The system must maintain the available quantity of each product in the relevant branch warehouse.

Quantities must be recorded using the appropriate unit for the product.

Examples include:

* kilograms;
* grams;
* liters;
* milliliters;
* pieces.

Inventory operations must preserve quantity accuracy when stock is:

* purchased;
* prepared;
* consumed;
* adjusted;
* counted;
* corrected.

The system must not allow stock to become negative.

---

## 7. Stock Batches

Inventory entries must preserve the source of the stock.

The minimum supported source types are:

1. **Prepared in Branch**
2. **Bought Ready**

These source types allow the system to distinguish between stock produced by the branch and stock purchased as a ready-to-use product.

The source information must remain available in inventory history.

The system must not silently merge historical source information in a way that removes traceability.

---

## 8. FIFO

Inventory consumption follows the **FIFO (First In, First Out)** principle.

When stock is consumed, the system should use the earliest applicable available stock first.

FIFO must apply when inventory is deducted through normal restaurant operations.

The system must preserve enough inventory history to determine the sequence in which stock became available.

---

## 9. Recipes and Inventory Dependency

Recipes define how products consume inventory.

A recipe may contain:

* raw materials;
* semi-finished products;
* required quantities;
* recipe components.

Inventory consumption must follow the approved recipe configuration.

For example:

```text
Finished Product
      ↓
Semi-Finished Product
      ↓
Raw Materials
```

The system must be able to trace inventory dependencies from finished products through semi-finished products to their underlying raw materials.

---

## 10. Semi-Finished Product Preparation

When a semi-finished product is prepared in a branch, the system must:

1. consume the required recipe components;
2. create the prepared quantity;
3. record the resulting stock;
4. identify the stock source as `Prepared in Branch`;
5. preserve the preparation history.

The system must not treat prepared stock as purchased stock.

The resulting stock must remain traceable to the preparation operation.

---

## 11. Shrinkage and Preparation Loss

Prepared products may have an expected shrinkage/loss percentage.

The system must support a configured shrinkage/loss percentage for prepared items.

This allows the expected usable quantity to reflect normal preparation loss.

The configured loss must be applied consistently to the relevant preparation calculation.

The system must preserve the resulting inventory transaction in history.

---

## 12. Purchasing and Receiving

Purchased inventory may be added to a branch warehouse as `Bought Ready`.

When purchased stock is recorded, the system must allow the employee to enter at least:

* product;
* quantity;
* price;
* source;
* purchase date.

Purchase information must remain available in inventory history.

The current system does not require a complex procurement workflow.

---

## 13. Manual Inventory Entry and Adjustment

Authorized users may manually record inventory changes when required.

Manual changes must include an appropriate reason or comment where the operation requires explanation.

The system must not silently overwrite the previous stock state.

Inventory adjustments must remain traceable through history.

The adjustment record should preserve:

* previous quantity;
* new quantity;
* difference;
* responsible employee;
* date/time;
* reason or comment where applicable.

---

## 14. Stock Counting

The system must support physical stock counting.

During a stock count, the employee records the physically observed quantity.

The system compares the physical quantity with the system quantity.

The resulting difference becomes an inventory variance.

The stock count must update the current inventory quantity according to the approved result.

The stock count history must remain available after completion.

---

## 15. Inventory Variance

Inventory variance represents the difference between:

* system-recorded quantity; and
* physically counted quantity.

The system must preserve variance information rather than silently replacing historical values.

Variance records must be available for reporting and auditing.

Large inventory variances may generate an alert according to the notification rules defined elsewhere in the Business Analysis documentation.

---

## 16. No Negative Stock

The system must not allow inventory quantities to become negative.

If an operation would require more inventory than is available, the operation must be blocked.

This rule applies to inventory consumption caused by restaurant operations, including order-related consumption.

The system must not solve insufficient stock by creating artificial negative quantities.

---

## 17. Order-Based Inventory Deduction

When an order consumes a product, inventory must be deducted according to the approved recipe.

For recipe-based products, the system must trace the required components.

Example:

```text
Order
  ↓
Finished Product
  ↓
Recipe
  ↓
Semi-Finished / Raw Materials
  ↓
Inventory Deduction
```

Inventory deduction must be consistent with the order operation.

If the required stock is unavailable, the relevant order operation must be blocked.

---

## 18. Insufficient Stock

When an order cannot be completed because required inventory is insufficient, the system must prevent the operation from creating negative stock.

The user may modify the order where permitted.

For example, removing a recipe component may reduce the required inventory and may allow the operation to continue if the resulting configuration is valid.

The system must not automatically create missing stock.

---

## 19. Recipe Modification and Inventory Impact

Recipe modifications directly affect future inventory consumption.

Approved recipe changes must therefore be reflected in subsequent inventory deductions.

Historical transactions must not be rewritten to match a newer recipe.

A previous order must retain the historical product and recipe-related information applicable at the time of the transaction.

Detailed recipe management rules are defined in:

`12_Products_and_Recipes.md`

---

## 20. Low-Stock Thresholds

Products may have a configured low-stock threshold.

When available stock reaches or falls below the relevant threshold, the system may generate a low-stock alert.

The threshold must be evaluated against the current available quantity.

Low-stock status should be visible to authorized users responsible for inventory management.

---

## 21. Out-of-Stock Condition

A product is considered out of stock when its available quantity is insufficient for its required use.

The system must provide an out-of-stock alert.

Out-of-stock conditions must not allow normal inventory deduction to create negative quantities.

---

## 22. Shopping List

The system must support an inventory shopping list.

The shopping list is an operational planning tool and does not represent a mandatory procurement workflow.

Users may manually add products to the shopping list.

The system may also generate shopping-list suggestions based on inventory conditions such as:

* low stock;
* out of stock.

The user does not have to mark a shopping-list item as completed before purchasing it.

---

## 23. Recording a Purchase

After purchasing a product, the user can manually record the purchased inventory.

The purchase record must support:

* product;
* quantity;
* price;
* source;
* purchase date.

The user may purchase an item even if it was not previously marked as completed in the shopping list.

The system should preserve the relationship between inventory purchases and their historical records where applicable.

---

## 24. Shopping and Purchase History

Purchase-related inventory information must remain available as historical data.

The system must preserve relevant:

* quantity;
* price;
* source;
* date;
* product;
* branch;
* responsible user.

Historical purchase information must not be silently removed when current inventory changes.

---

## 25. Product Unavailability

A product may temporarily become unavailable for operational reasons.

One supported example is:

**Equipment Broken**

When a product is marked unavailable for this reason, the system may prevent or restrict its normal use until the product is made available again.

This is an operational availability state and is not the same as deleting or archiving the product.

The system must preserve the product and its historical data.

---

## 26. Product Archive and Deletion

Products with historical inventory or recipe relationships must not be physically deleted in a way that destroys historical traceability.

A product with a recipe cannot be deleted.

Instead, the product or recipe must be archived according to the applicable business rules.

Historical transactions must continue to reference the original product identity.

Detailed product and recipe lifecycle rules are defined in:

`12_Products_and_Recipes.md`

---

## 27. Branch Isolation

Inventory must be isolated by business and branch.

An employee operating within one branch must not automatically gain access to another branch's inventory.

Inventory operations must respect:

* business scope;
* branch scope;
* employee permissions;
* subscription limits.

Cross-branch inventory access requires explicit authorization through the permission model.

---

## 28. Inventory Permissions

Inventory operations are permission-controlled.

Permissions may determine whether an employee can:

* view inventory;
* add inventory;
* record purchases;
* adjust inventory;
* perform stock counts;
* view inventory history;
* manage shopping lists;
* manage product availability.

The system must not create a separate inventory-expense role solely for inventory operations.

Where an explanation is needed, an appropriate comment is sufficient.

The exact permission matrix is defined in:

`05_Users_Roles_and_Permissions.md`

---

## 29. Recipe Permission Relationship

Access to recipes is a separate permission.

Having access to inventory does not automatically mean that an employee can view recipe details.

Similarly:

* menu access does not automatically grant recipe access;
* inventory access does not automatically grant recipe modification access.

Recipe modification requires the appropriate dedicated permission.

---

## 30. Offline Inventory Operation

Authorized trusted devices may perform supported inventory operations while offline.

Offline inventory operations must:

* remain associated with the correct business;
* remain associated with the correct branch;
* preserve the responsible employee;
* preserve the device identity;
* use transaction UUIDs;
* remain in the synchronization queue until synchronized.

Offline operation must not bypass:

* permissions;
* branch isolation;
* no-negative-stock rules;
* other established business rules.

---

## 31. Inventory Synchronization

When connectivity returns, offline inventory operations must synchronize with the central system.

Synchronization must preserve:

* transaction identity;
* original transaction context;
* inventory changes;
* responsible employee;
* device identity;
* transaction time;
* audit information.

Duplicate synchronization of the same transaction must not create duplicate inventory effects.

The server remains the authoritative source after synchronization.

Detailed offline and synchronization rules are defined in:

`07_Offline_Operation_and_Synchronization.md`

---

## 32. Inventory Conflicts

If multiple authorized devices perform inventory operations while offline, synchronization may reveal conflicting operations.

The system must preserve transaction history and must not silently overwrite inventory history.

The final inventory state must follow the authoritative business rules and synchronization model.

Conflict handling must preserve enough information to identify:

* the affected inventory;
* the original transaction;
* the responsible employee;
* the device;
* the resulting resolution.

Technical conflict-resolution mechanisms belong to the Architecture and System Analysis documentation.

---

## 33. Inventory History and Auditability

Important inventory changes must be traceable.

The system must preserve relevant events such as:

* purchases;
* preparation;
* consumption;
* stock counts;
* adjustments;
* variances;
* product availability changes;
* recipe-related inventory changes.

Where an adjustment changes a quantity, the historical record should preserve the previous and resulting values.

Important actions must identify the responsible user and timestamp.

No important inventory change should be silently overwritten.

---

## 34. Inventory Alerts

Inventory-related alerts include:

* low stock;
* out of stock;
* large inventory variance.

Alerts must be available to authorized users according to their branch scope and notification permissions.

Notifications must not expose inventory information outside the user's authorized business or branch scope.

---

## 35. Inventory Reporting

Inventory information must be available for relevant reports.

Reports may include:

* current stock;
* inventory movements;
* purchases;
* stock counts;
* variances;
* inventory history;
* low-stock conditions;
* out-of-stock conditions.

Reporting must respect branch and employee permissions.

Historical inventory information must remain available even when the current product configuration changes.

Detailed report structures are defined in:

`16_Reports_and_Dashboards.md`

---

## 36. Performance Requirements

Inventory operations must remain lightweight enough for normal restaurant hardware.

The system should avoid unnecessary processing during common operations such as:

* order inventory deduction;
* stock lookup;
* purchase entry;
* stock counting;
* inventory adjustment.

Inventory calculations must not introduce noticeable delays into normal POS operations.

The system should support the established offline-first model without requiring powerful branch hardware.

---

## 37. Business Rules Summary

| Area                   | Rule                                              |
| ---------------------- | ------------------------------------------------- |
| Warehouse              | Branch-level warehouse                            |
| Product types          | Raw, semi-finished, finished                      |
| Product code           | Automatically generated                           |
| Stock source           | Prepared in Branch / Bought Ready                 |
| Consumption            | FIFO                                              |
| Recipes                | Control inventory consumption                     |
| Semi-finished products | Can be prepared from recipe components            |
| Shrinkage              | Supported for prepared items                      |
| Negative stock         | Not allowed                                       |
| Insufficient stock     | Operation is blocked                              |
| Stock count            | Physical quantity compared with system quantity   |
| Variance               | Preserved in history                              |
| Low stock              | Threshold-based alert                             |
| Out of stock           | Alert and no negative deduction                   |
| Shopping list          | Advisory                                          |
| Purchase recording     | Quantity, price, source, date                     |
| Product unavailability | Equipment Broken state supported                  |
| Product deletion       | Historical/recipe-dependent products are archived |
| Branch isolation       | Required                                          |
| Recipe access          | Separate permission                               |
| Inventory permissions  | Role and employee permission based                |
| Offline operation      | Supported for authorized trusted devices          |
| Synchronization        | UUID-based and idempotent                         |
| Audit                  | Important inventory changes preserved             |
| Performance            | Lightweight and POS-friendly                      |

---

## 38. Business Boundaries

The current Inventory and Warehouse scope does **not** define:

* complex procurement workflows;
* supplier management as a full business module;
* multiple warehouses inside one branch;
* warehouse-to-warehouse transfers;
* advanced accounting valuation;
* barcode hardware requirements;
* batch expiration management;
* automatic purchasing;
* customer inventory;
* advanced demand forecasting.

These areas may be considered in future documentation if business requirements justify them.

---

## 39. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `19_Data_Lifecycle_and_Deletion.md`
* `20_Business_Rules.md`

