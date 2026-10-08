# Inventory Domain

**Document ID:** DA-08
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Inventory domain manages stock and inventory movements for each Branch.

It is responsible for:

* inventory items;
* raw materials;
* semi-finished products;
* finished products;
* stock quantities;
* stock movements;
* purchases;
* inventory adjustments;
* stock discrepancies;
* low-stock state;
* stock availability validation;
* recipe-driven consumption;
* FIFO-related inventory ordering;
* inventory history;
* inventory concurrency.

The Inventory domain does not own:

* Orders;
* Products and Recipes definitions;
* Payments;
* Cash Sessions;
* Employees;
* Reports;
* Notifications;
* Subscription.

Those domains interact with Inventory through explicit boundaries.

---

# 2. Inventory Ownership

Inventory is operationally Branch-scoped.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Warehouse
   ↓
Inventory State
```

A Branch has its own inventory state.

Inventory belonging to one Branch must not automatically affect another Branch.

Cross-branch inventory transfer is currently out of scope.

---

# 3. Warehouse

A Warehouse represents a stock-holding location within a Branch.

The current business model supports warehouse concepts while keeping the operational model simple.

A warehouse has a stable UUID.

Future support for multiple warehouses must not invalidate the current Branch-level inventory model.

---

# 4. Inventory Item

An Inventory Item represents a stock-controlled product or material.

An inventory item may correspond to:

* raw material;
* semi-finished product;
* finished product.

The Product/Recipe domain owns product definition.

The Inventory domain owns the current stock state and stock movements.

---

# 5. Product Types

The current inventory model supports:

```text
Raw Material
Semi-Finished Product
Finished Product
```

These types have different operational meanings but participate in the same stock movement model.

---

# 6. Raw Material

Raw materials are directly consumed by recipes or other inventory operations.

Examples include:

* meat;
* flour;
* oil;
* mayonnaise;
* spices.

Raw materials may be purchased directly into Branch inventory.

---

# 7. Semi-Finished Product

A semi-finished product is produced from one or more inputs.

Example:

```text
1 kg meat
+
200 g mayonnaise
+
spices
↓
Semi-Finished Product
```

The actual production quantity may differ from the planned quantity.

Inventory records the actual output.

---

# 8. Finished Product

A finished product is normally sold through the POS.

Its inventory consumption may be derived from its recipe.

A finished product may depend directly on:

```text
Raw Material
```

or indirectly:

```text
Raw Material
   ↓
Semi-Finished Product
   ↓
Finished Product
```

---

# 9. Stock Quantity

Stock quantity represents the current available inventory for an item in a Branch/Warehouse context.

The system must not allow negative stock.

Conceptually:

```text
Available Stock >= 0
```

A transaction requiring more stock than available must be rejected.

---

# 10. Stock Availability

Before a stock-consuming operation is committed, the system must validate availability.

For a required quantity `Q`:

```text
Available Quantity >= Required Quantity
```

If this condition is false, the consuming operation is rejected.

The system must not silently create negative stock.

---

# 11. Order Consumption

An accepted Order may consume inventory according to its product and recipe configuration.

Inventory deduction occurs when the Order is accepted.

Draft Orders do not consume inventory.

---

# 12. Atomic Order Consumption

Order acceptance and required inventory deduction form one core transactional boundary.

Conceptually:

```text
Accept Order
    ↓
Validate Stock
    ↓
Deduct Required Inventory
    ↓
Commit Order Acceptance
```

If inventory deduction fails:

```text
Order remains unaccepted
```

No partial deduction is allowed.

---

# 13. Recipe-Based Consumption

The Inventory domain receives the resolved consumption requirement from the Product/Recipe domain.

For example:

```text
Finished Product
      ↓
Recipe
      ↓
Semi-Finished Product
      ↓
Raw Materials
```

The Inventory domain applies the required stock movements.

Recipe definition itself is not owned by Inventory.

---

# 14. Recursive Dependency

Inventory must support dependency chains such as:

```text
Raw Material
      ↓
Semi-Finished Product A
      ↓
Semi-Finished Product B
      ↓
Finished Product
```

The system must resolve required stock without creating cyclic dependencies.

Circular recipe dependencies must be rejected by the Product/Recipe domain.

---

# 15. Semi-Finished Production

When a semi-finished product is prepared, inventory must record:

* input quantities;
* actual output quantity;
* Branch;
* Warehouse;
* actor;
* timestamp;
* source;
* relevant batch information.

The actual output quantity becomes available stock.

---

# 16. Proportional Recipe Scaling

If a recipe is defined for one production quantity but the actual production quantity differs, ingredient consumption scales proportionally.

Example:

```text
Recipe output: 10 kg
Actual output: 5 kg

Required ingredient consumption:
50% of the original recipe quantities
```

The final implementation must preserve measurement precision according to the supported unit model.

---

# 17. Production Loss

Production may include yield loss or shrinkage.

The system supports a configured loss percentage where applicable.

Loss must be represented explicitly.

It must not be hidden by silently changing recipe quantities.

---

# 18. Purchase

A purchase adds stock to inventory.

A purchase record may contain:

* supplier;
* product/material;
* quantity;
* unit price;
* total price;
* purchase date;
* batch;
* comment;
* Branch;
* Warehouse;
* actor.

Supplier management remains intentionally shallow.

---

# 19. Purchase Stock Addition

A confirmed purchase increases available stock.

The stock movement must retain enough information to reconstruct:

* what was purchased;
* how much;
* at what price;
* when;
* from which source;
* into which Branch/Warehouse.

---

# 20. Last Purchase Cost

The Inventory domain provides the latest valid purchase cost for products where applicable.

This value may be used by pricing/custom markup logic.

Inventory remains responsible for the source data.

Pricing remains responsible for selling-price calculation.

---

# 21. FIFO

Inventory supports FIFO-based stock consumption where applicable.

Conceptually:

```text
Oldest eligible stock
        ↓
Consumed first
        ↓
Next eligible stock
```

The system must preserve sufficient stock-layer information to support historical reconstruction.

The exact storage mechanism is an implementation concern for the Database/Architecture phases.

---

# 22. Stock Movement

Every material stock change must be represented as a stock movement.

Examples:

* Purchase;
* Sale Consumption;
* Semi-Finished Production;
* Inventory Adjustment;
* Return to Inventory;
* Approved Correction;
* Other explicitly supported movement.

A movement must preserve its source context.

---

# 23. Movement Identity

Each stock movement must have a stable UUID.

The UUID provides:

* identity;
* idempotency;
* synchronization support;
* audit correlation;
* historical reconstruction.

No Client Transaction ID is required.

---

# 24. Movement Direction

A stock movement is conceptually either:

```text
IN
OUT
```

Some business operations may produce both an OUT and an IN movement.

Example:

```text
Semi-Finished Production

Raw Materials → OUT
Semi-Finished Product → IN
```

---

# 25. Movement Context

A stock movement should retain applicable context:

* Business;
* Branch;
* Warehouse;
* Product/Material;
* quantity;
* unit;
* direction;
* source operation;
* actor;
* Device;
* timestamp;
* related Transaction UUID;
* related Order UUID where applicable.

---

# 26. Order Inventory Return

When an accepted Order is modified by removing a product or reducing quantity, the system asks whether the consumed inventory should be returned.

If return is confirmed:

```text
Inventory OUT
      ↓
Inventory IN
```

If return is rejected, no inventory return is created.

The decision must be preserved in history.

---

# 27. Served Items

Inventory already consumed for served items must not be automatically returned.

Serving an item creates a business boundary after which the consumed inventory cannot be silently restored.

Any exceptional correction must use an explicit authorized correction mechanism.

---

# 28. Modification Atomicity

If an Order modification requires an inventory return or additional inventory consumption:

```text
Validate
   ↓
Apply all required stock changes
   ↓
Commit modification
```

If any required inventory operation fails:

```text
Entire modification is rolled back
```

Partial inventory changes are not allowed.

---

# 29. Manual Stock Exit

Manual stock removal is a controlled operation.

It requires:

* appropriate Inventory Adjustment permission;
* reason;
* actor;
* Branch;
* affected inventory item;
* quantity;
* timestamp.

The system must not treat unexplained manual stock removal as a normal sale.

---

# 30. Inventory Adjustment

Inventory Adjustment is used when physical stock differs from system stock or an authorized operational correction is required.

An adjustment must preserve:

* previous quantity;
* adjustment quantity;
* resulting quantity;
* reason;
* actor;
* timestamp;
* source;
* Branch/Warehouse.

---

# 31. Stock Count

A stock count compares physical inventory against recorded inventory.

Conceptually:

```text
System Quantity
      ↓
Physical Count
      ↓
Discrepancy
```

The discrepancy must be shown before the system applies the resulting adjustment.

---

# 32. Discrepancy Confirmation

A discrepancy does not automatically rewrite stock.

An authorized employee must confirm the adjustment according to permission rules.

This prevents accidental stock changes caused by an incorrect count.

---

# 33. Low Stock

The Inventory domain may calculate low-stock state using configured thresholds.

Possible states include:

```text
Normal
Low
Out
```

Low stock does not automatically modify inventory.

It produces a condition that may be consumed by the Notification domain.

---

# 34. Out of Stock

If required stock is unavailable:

* the sale is blocked;
* the Order is not accepted;
* inventory remains unchanged.

The user may remove or modify the affected product if the Order workflow allows it.

---

# 35. Shopping List

The system may generate an advisory shopping list from:

* low-stock items;
* out-of-stock items;
* manually added items.

The shopping list does not itself increase inventory.

Only a confirmed purchase/receipt operation adds stock.

---

# 36. Equipment Availability

Equipment failures may temporarily make products unavailable.

This is not itself an inventory adjustment.

The relevant product configuration is marked unavailable by the appropriate business operation.

Inventory quantity remains unchanged.

---

# 37. Branch Isolation

Inventory is Branch-scoped.

A stock movement belonging to Branch A cannot modify Branch B inventory.

All inventory operations must validate:

```text
Business Scope
+
Branch Scope
+
Warehouse Scope where applicable
```

---

# 38. Cross-Branch Transfer

Cross-branch inventory transfer is currently out of scope.

The domain must not introduce transfer semantics merely to solve ordinary inventory operations.

Future transfer functionality should be designed as an explicit business capability.

---

# 39. Offline Inventory

Trusted devices may perform supported inventory operations offline.

Offline inventory operations must use:

* valid offline authorization;
* local inventory state;
* UUID-based identity;
* durable local transaction storage.

---

# 40. Offline Stock Validation

Offline stock validation is provisional.

When synchronization occurs, the server revalidates:

* Branch;
* product;
* quantity;
* permission;
* current stock;
* transaction identity;
* relevant configuration.

The server remains authoritative.

---

# 41. Offline Stock Conflict

If offline stock consumption conflicts with another committed transaction:

* the server does not silently overwrite inventory;
* the stock operation is preserved;
* a conflict may be created;
* authorized resolution is required;
* the original event remains identifiable.

---

# 42. Inventory Synchronization

Inventory synchronization must be idempotent.

A repeated synchronization request must not duplicate:

* stock consumption;
* stock additions;
* purchases;
* adjustments;
* returns.

Movement UUIDs and Transaction UUIDs provide stable identity.

---

# 43. Concurrent Stock Consumption

Online stock consumption must be concurrency-safe.

Example:

```text
Stock = 1

Sale A → requests 1
Sale B → requests 1
```

Only one sale may successfully consume the final unit.

The other operation must be rejected or handled as an explicit conflict.

---

# 44. Concurrent Purchase and Sale

Purchase and sale may occur concurrently.

The system must ensure that stock validation and stock mutation are performed within an appropriate transactional boundary.

The implementation must prevent:

* negative stock;
* lost updates;
* duplicate deductions;
* inconsistent stock totals.

---

# 45. Inventory History

Inventory history must preserve:

* previous stock state where relevant;
* movements;
* purchases;
* deductions;
* returns;
* adjustments;
* discrepancies;
* corrections.

Historical records must not be silently rewritten.

---

# 46. Inventory Corrections

A correction changes the effective inventory result without destroying the original movement history.

Conceptually:

```text
Original Movement
       +
Correction
       ↓
Current Derived State
```

The correction must preserve reason, actor, timestamp, and authorization.

---

# 47. Inventory and Product Domain

The Product/Recipe domain owns:

* product identity;
* product type;
* recipe;
* recipe version;
* recipe approval;
* recipe dependencies;
* product configuration.

Inventory owns:

* current stock;
* stock movements;
* availability;
* purchases;
* adjustments;
* discrepancies.

---

# 48. Inventory and Order Domain

Order requests inventory consumption when an Order becomes Accepted.

Inventory validates and applies the required stock changes.

Order acceptance must not complete if required inventory deduction fails.

---

# 49. Inventory and Payment Domain

Inventory does not depend on payment completion for initial sale consumption.

Inventory is consumed when the Order is Accepted.

Payment occurs as a separate financial operation.

Therefore:

```text
Order Accepted
    ↓
Inventory Consumed

Payment
    ↓
Financial Settlement
```

---

# 50. Inventory and Cash Domain

Inventory does not directly modify Cash Sessions.

A sale may produce both:

* inventory consumption;
* payment/cash impact.

These are separate domain responsibilities.

---

# 51. Inventory and Reports

Inventory reports may include:

* current stock;
* stock movements;
* purchases;
* consumption;
* discrepancies;
* adjustments;
* low-stock items;
* product availability.

The Report domain owns report generation.

---

# 52. Inventory and Notifications

Inventory may emit conditions such as:

* low stock;
* out of stock;
* significant inventory discrepancy.

The Notification domain owns notification lifecycle and delivery.

Inventory remains authoritative for stock state.

---

# 53. Aggregate Boundaries

The Inventory domain should conceptually contain:

* Warehouse;
* Inventory Item/Stock;
* Stock Movement;
* Purchase Stock Receipt;
* Inventory Adjustment;
* Inventory Discrepancy.

It should not contain:

* Order;
* Payment;
* Cash Session;
* Employee;
* Recipe definition;
* Report;
* Notification.

---

# 54. Domain Services

Potential Inventory domain services include:

```text
Stock Availability Service
Inventory Consumption Service
Stock Receipt Service
Production Service
Inventory Adjustment Service
Inventory Count Service
Stock Discrepancy Service
FIFO Allocation Service
Inventory Conflict Resolver
```

These are logical domain services, not necessarily separate applications.

---

# 55. Domain Events

Potential events include:

```text
StockReceived
StockConsumed
StockReturned
SemiFinishedProductProduced
InventoryAdjusted
InventoryDiscrepancyDetected
LowStockDetected
OutOfStockDetected
InventoryCorrectionCreated
```

Events represent facts that have already occurred.

---

# 56. Inventory Invariants

### Identity

1. Every stock movement has a stable UUID.
2. Every inventory item belongs to a valid Business.
3. Every inventory item belongs to a valid Branch/Warehouse context.
4. Stock movement identity remains stable during synchronization.
5. No Client Transaction ID is required.

### Stock

6. Stock quantity cannot become negative.
7. Stock-consuming operations require sufficient available quantity.
8. Stock validation and mutation must be concurrency-safe.
9. Failed stock consumption does not partially modify inventory.
10. Every material stock change is represented by a movement.
11. Stock history remains reconstructable.
12. Stock corrections do not erase original movements.

### Orders

13. Draft Orders do not consume inventory.
14. Accepted Orders consume required inventory.
15. Order acceptance fails if required stock cannot be deducted.
16. Order acceptance and required inventory deduction share one core transactional boundary.
17. Accepted Order quantity increases require additional stock validation.
18. Failed modification stock operations roll back the entire modification.
19. Inventory return decisions are preserved.
20. Served item inventory is never silently returned.

### Recipes

21. Recipe definitions are owned by the Product/Recipe domain.
22. Inventory consumes the resolved recipe requirements.
23. Raw-to-semi-finished dependencies are traceable.
24. Semi-finished production records actual output.
25. Production loss is represented explicitly.
26. Circular recipe dependencies must not produce infinite inventory consumption.

### Purchases

27. Confirmed purchases increase stock.
28. Purchase records preserve quantity and cost information.
29. Purchase source information is preserved where available.
30. Last Purchase Cost can be reconstructed from valid purchase history.

### FIFO

31. FIFO allocation consumes eligible older stock before newer stock where FIFO applies.
32. Stock layers required for FIFO remain historically identifiable.
33. FIFO allocation must not create negative stock.

### Adjustments

34. Manual stock exit requires appropriate permission.
35. Manual stock exit requires a reason.
36. Stock counts do not automatically rewrite inventory without required confirmation.
37. Inventory discrepancies are preserved.
38. Inventory adjustments preserve before and after quantities.
39. Corrections preserve original inventory history.

### Branch

40. Inventory is Branch-scoped.
41. Branch A operations cannot modify Branch B stock.
42. Cross-branch transfer is not implicitly created.
43. Warehouse scope is validated where applicable.

### Offline

44. Offline inventory requires trusted-device authorization.
45. Offline stock operations have stable UUIDs.
46. Offline stock operations are durably stored.
47. Server revalidates offline inventory operations.
48. Offline conflicts are not silently overwritten.
49. Synchronization does not duplicate stock movements.

### Concurrency

50. Only one concurrent operation may consume the final available unit.
51. Concurrent purchases and sales cannot create lost stock updates.
52. Duplicate requests cannot duplicate stock movement.
53. Synchronization retries are idempotent.
54. Inventory transaction boundaries prevent partial state.

### History

55. Inventory movement history is immutable.
56. Adjustment history is preserved.
57. Purchase history is preserved.
58. Discrepancy history is preserved.
59. Original stock operations remain identifiable after correction.
60. Historical inventory can be reconstructed from authoritative movements and corrections.

### Security

61. Inventory operations require authentication.
62. Inventory operations require applicable permission.
63. Branch scope is validated server-side.
64. Device trust is validated for offline operations.
65. Subscription entitlement is enforced where applicable.

---

# 57. Completion Criteria

The Inventory domain is considered complete when:

* raw, semi-finished, and finished stock are defined;
* Branch/Warehouse ownership is defined;
* stock quantity rules are defined;
* stock movement identity is defined;
* order consumption is defined;
* recipe-based consumption boundary is defined;
* semi-finished production is defined;
* purchases are defined;
* FIFO responsibility is defined;
* inventory adjustment is defined;
* stock discrepancy handling is defined;
* low/out-of-stock conditions are defined;
* offline inventory is defined;
* synchronization and conflict boundaries are defined;
* concurrency requirements are defined;
* historical integrity is defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

