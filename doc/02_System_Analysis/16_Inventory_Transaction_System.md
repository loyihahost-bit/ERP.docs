# Inventory Transaction System

**Document ID:** SA-16
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for inventory transactions.

Inventory is a core business subsystem responsible for maintaining the current stock state and the historical record of stock movement.

The system must ensure that:

* stock cannot become negative;
* stock movements are traceable;
* Order acceptance and inventory deduction remain consistent;
* concurrent operations cannot consume the same stock incorrectly;
* inventory corrections preserve history;
* offline inventory operations remain recoverable;
* inventory data remains attributable to Business, Branch, Employee, Device and transaction context.

---

## 2. Scope

This document covers:

* inventory context;
* stock identity;
* stock ownership;
* inventory movement types;
* purchases;
* sales deductions;
* recipe-based deduction;
* Set-based deduction;
* semi-finished production;
* stock returns;
* manual adjustments;
* inventory counts;
* discrepancies;
* costing;
* FIFO;
* Average Cost;
* Last Purchase Cost;
* concurrency;
* atomic transactions;
* offline inventory;
* synchronization;
* conflict resolution;
* audit;
* reporting;
* subscription restrictions;
* error handling;
* system invariants.

---

## 3. Inventory Context

Inventory is maintained within the following context:

```text
Business
   ↓
Branch
   ↓
Warehouse
   ↓
Product Stock
   ↓
Inventory Transactions
```

Inventory data is Branch-scoped unless a specific configuration explicitly defines otherwise.

---

## 4. Inventory Identity

Every important inventory entity must have a stable UUID.

Relevant identities include:

* Business UUID;
* Branch UUID;
* Warehouse UUID;
* Product UUID;
* Recipe UUID;
* Recipe Version UUID;
* Inventory Transaction UUID;
* Inventory Movement UUID;
* Purchase UUID;
* Adjustment UUID;
* Stock Count UUID;
* Order UUID;
* Order Item UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID where applicable.

UUIDs provide stable identity for local operations, synchronization and idempotency.

---

## 5. Stock Ownership

Stock belongs to a Business and Branch context.

A user may only operate on inventory when:

* Business context is valid;
* Branch scope is valid;
* employee is active;
* required permission exists;
* subscription entitlement permits the operation.

Cross-Business inventory access is prohibited.

Cross-Branch inventory transfer is currently out of scope.

---

## 6. Warehouse Context

A Branch may contain one or more logical warehouses.

Warehouse identity allows the system to distinguish where stock is physically or operationally stored.

Inventory operations must reference the applicable Warehouse where the operation requires warehouse-level tracking.

---

## 7. Product Types

Inventory supports:

* Raw Material;
* Semi-Finished Product;
* Finished Product.

The system must preserve the distinction because different product types may participate differently in recipes and production.

---

## 8. Inventory Movement Model

Inventory changes through explicit transactions.

Typical movement types include:

* Purchase;
* Sale Deduction;
* Recipe Consumption;
* Semi-Finished Production;
* Return;
* Adjustment Increase;
* Adjustment Decrease;
* Stock Count Adjustment;
* Other authorized inventory correction.

Every movement must have a clear business reason and source context.

---

## 9. Inventory Transaction

An Inventory Transaction represents a logical stock-changing operation.

It should contain sufficient context to identify:

* transaction UUID;
* Business;
* Branch;
* Warehouse;
* Product;
* quantity;
* unit;
* movement direction;
* movement type;
* source entity;
* source transaction UUID;
* Employee;
* Device;
* timestamp;
* source Online/Offline/Sync/System;
* reason where applicable.

Historical inventory transactions must remain immutable.

---

## 10. Inventory Movement Direction

A stock movement is either:

* Increase;
* Decrease.

The system must not represent a stock change as an unexplained overwrite of the current quantity.

Current stock is derived from valid inventory movements and the authoritative inventory state.

---

## 11. Current Stock

The system maintains a current stock state for efficient operational reads.

The current stock must remain consistent with committed inventory transactions.

A direct stock quantity change without a corresponding authorized inventory operation is not allowed.

---

## 12. Sale Deduction

For a normal product sale, inventory deduction occurs when the Order transitions from Draft to Accepted.

The deduction is based on the applicable product recipe.

The operation must validate stock before committing the acceptance.

---

## 13. Order and Inventory Atomicity

Order acceptance and required inventory deduction are one core atomic business transaction.

Conceptually:

```text
Validate Order
      ↓
Validate Stock
      ↓
Deduct Inventory
      ↓
Commit Order as Accepted
```

If any required inventory deduction fails:

* Order acceptance fails;
* inventory changes are rolled back;
* Order remains unaccepted.

---

## 14. Stock Validation

The system must verify that sufficient stock exists for every required inventory component.

If any required component is insufficient:

* the complete operation is rejected;
* partial deduction is not allowed;
* no negative stock is created.

---

## 15. Concurrent Sales

When multiple Orders attempt to consume the same limited stock, the server must use authoritative database state.

Critical stock operations use transaction isolation, row locking, atomic update conditions or equivalent mechanisms.

Example:

```text
Stock = 1

Order A → requests 1
Order B → requests 1

Only one operation succeeds.
The other is rejected because stock is no longer sufficient.
```

---

## 16. Recipe-Based Deduction

A Finished Product may consume:

* Raw Materials;
* Semi-Finished Products;
* other configured recipe components.

The system resolves the approved applicable Recipe Version before deduction.

Historical Orders retain the recipe/price context required for historical reconstruction.

---

## 17. Recipe Version

Recipe changes do not silently rewrite historical inventory transactions.

A Recipe Version identifies the composition applicable to the operation.

New or changed recipes become effective according to the configured cash-session effective rule.

Existing historical transactions retain their original recipe context.

---

## 18. Semi-Finished Products

Semi-Finished Products may be produced from Raw Materials or other configured components.

Example:

```text
1 kg Meat
+
200 g Mayonnaise
+
Spices
=
Semi-Finished Product
```

Production consumes the configured input quantities and creates the actual output quantity.

---

## 19. Semi-Finished Production

Semi-finished production must record:

* input products;
* consumed quantities;
* output product;
* actual output quantity;
* recipe version;
* Branch;
* Warehouse;
* Employee;
* Device;
* timestamp;
* production transaction UUID.

The output quantity must be explicitly recorded.

---

## 20. Production Yield

Actual production output may differ from theoretical recipe output.

The system must support configured yield/loss behavior.

The actual produced quantity is recorded separately from theoretical recipe quantity.

The difference must remain explainable through the production transaction and applicable yield/loss configuration.

---

## 21. Production Atomicity

Semi-finished production is atomic.

The operation must not result in:

```text
Inputs consumed
+
Output not created
```

or:

```text
Output created
+
Inputs not consumed
```

If a required operation fails, the complete production transaction is rolled back.

---

## 22. Set Product Deduction

A Set is a separate sellable bundle.

When a Set is sold, inventory is deducted according to the Set's configured component products.

The Set's component configuration is stable for the applicable configuration version.

Changing the underlying product recipe does not automatically change the Set's component composition.

---

## 23. Set Configuration Version

A Set configuration change creates a new effective configuration/version.

The new configuration becomes effective according to the configured cash-session effective rule.

Historical Set sales retain the configuration required to reconstruct the original inventory deduction.

---

## 24. Product Modification After Acceptance

When an Accepted Order is modified:

* quantity increase requires additional stock;
* quantity reduction may return stock only if the user confirms return;
* product removal may return stock only if the user confirms return.

The inventory decision is recorded with the Order modification.

---

## 25. Modification Increase

If additional stock required by an Order modification is insufficient:

* the entire modification is rejected;
* no partial quantity is applied;
* no partial inventory deduction remains.

The original Order state remains unchanged.

---

## 26. Inventory Return on Modification

When a user chooses to return inventory after reducing/removing an item:

* the corresponding inventory quantity is returned;
* the return is linked to the Order modification;
* the original deduction remains historically visible;
* the return is recorded as a separate inventory movement.

The original inventory transaction is not rewritten.

---

## 27. Failed Inventory Return

If an inventory return required by an Order modification fails:

* the complete Order modification is rolled back;
* the Order remains in its previous state;
* no partial price or quantity modification remains.

---

## 28. Served Items

Items that have already been served must never automatically return inventory as part of cancellation or refund.

Any exceptional inventory correction must use a separate authorized inventory correction workflow.

---

## 29. Purchases

A purchase increases stock.

A purchase record may contain:

* supplier;
* product;
* quantity;
* unit;
* unit price;
* total price;
* purchase date;
* batch;
* comment;
* Branch;
* Warehouse;
* Employee;
* Device;
* purchase UUID.

Supplier management remains intentionally shallow.

---

## 30. Purchase Stock Update

A confirmed purchase creates an inventory increase transaction.

The system must not add stock merely because a purchase form was started.

Only the appropriate confirmed state may affect current stock.

---

## 31. Purchase Cost

The system stores purchase cost information for inventory costing and reporting.

At minimum, purchase transactions retain:

* quantity;
* unit price;
* total;
* date;
* product;
* source context.

Historical purchase costs remain unchanged.

---

## 32. FIFO Costing

FIFO is supported for inventory cost tracking.

When FIFO is used, stock consumption is associated with the oldest applicable available inventory layer first.

Inventory layers must preserve sufficient historical information to calculate cost correctly.

---

## 33. Average Cost

Average Cost is also supported.

The system may calculate the weighted average cost of available inventory according to the configured costing rules.

Historical transactions retain the values required to reproduce the applicable cost calculation.

---

## 34. Last Purchase Cost

Last Purchase Cost represents the most recent valid purchase cost for the relevant Product and Branch/Warehouse context.

Last Purchase Cost is used for operations that explicitly depend on that value.

For example, custom Order markup uses:

```text
Final Price = Last Purchase Cost × (1 + Markup / 100)
```

where Markup is constrained to the allowed range of 0–100%.

---

## 35. Costing Separation

FIFO, Average Cost and Last Purchase Cost serve different purposes.

The system must not silently substitute one costing model for another.

The applicable costing context must be explicit for the operation or report that uses it.

---

## 36. Manual Stock Exit

Manual stock decrease is an authorized inventory operation.

It requires:

* Inventory Adjustment permission;
* reason;
* quantity;
* product;
* Branch;
* Warehouse where applicable;
* actor;
* timestamp.

The system must not provide an unexplained manual stock decrease.

---

## 37. Manual Stock Increase

Manual stock increase is also an authorized inventory operation.

The reason must be recorded.

Possible business reasons include:

* correction;
* stock count adjustment;
* verified physical difference;
* authorized operational adjustment.

The system preserves the original transaction and records the correction separately.

---

## 38. Inventory Count

Inventory Count compares:

* system quantity;
* physically counted quantity.

The difference is shown before an adjustment is committed.

The system must not automatically alter stock merely because a count was entered.

---

## 39. Inventory Count Confirmation

A discrepancy may be adjusted only after an authorized user confirms the adjustment.

The adjustment creates a separate Inventory Transaction.

The original system quantity remains reconstructable.

---

## 40. Inventory Discrepancy

A discrepancy may represent:

* shortage;
* overage.

The system stores:

* expected quantity;
* counted quantity;
* difference;
* reason/comment where required;
* actor;
* Branch;
* Warehouse;
* timestamp;
* related Stock Count UUID.

---

## 41. Discrepancy History

The original discrepancy remains immutable.

If a later correction is made:

* the original discrepancy remains;
* a new correction transaction is created;
* the correction references the original discrepancy;
* actor and reason are recorded.

---

## 42. Negative Stock Prevention

Negative stock is prohibited.

Every stock-decreasing operation must validate the authoritative available quantity before commitment.

This applies to:

* Order acceptance;
* Order modification;
* recipe consumption;
* production;
* manual stock exit;
* offline synchronization.

---

## 43. Inventory Reservation

The current system does not require permanent stock reservation for Draft Orders.

Draft Orders:

* do not deduct stock;
* do not reserve stock;
* do not affect current stock.

Stock is validated and deducted at the appropriate operational transition.

---

## 44. Equipment Broken

A product may be temporarily marked unavailable because required equipment is broken.

This state is separate from inventory quantity.

A product may therefore be:

* active and in stock;
* active but equipment unavailable;
* inactive;
* unavailable because stock is insufficient.

The system must not confuse these states.

---

## 45. Low Stock

Low stock thresholds generate warnings.

A low-stock warning does not automatically authorize negative stock.

If stock reaches zero or becomes insufficient for an operation, the applicable sale or stock-consuming operation is blocked.

---

## 46. Shopping List

The shopping list is advisory.

It may be generated from:

* low stock;
* out-of-stock products;
* manual additions.

A shopping list does not change inventory.

Actual stock changes only after a valid purchase/receipt operation.

---

## 47. Inventory Transaction Source

Each inventory operation must identify its source.

Possible sources include:

* Online;
* Offline;
* Synchronization;
* System;
* authorized employee operation.

This information is required for traceability and reconciliation.

---

## 48. Employee and Device Attribution

Important inventory transactions must identify:

* Employee;
* Device;
* Branch;
* Warehouse;
* source.

System-generated transactions use `SYSTEM` as the actor where applicable.

---

## 49. Cash Session Context

Inventory operations do not generally require a Cash Session.

When an inventory operation is directly associated with a POS transaction, the applicable Cash Session may be included in the transaction context.

Inventory history must not incorrectly imply that every stock movement is a cash operation.

---

## 50. Inventory and Payment Independence

Inventory and payment are separate concerns.

Payment does not automatically create an inventory deduction.

Inventory deduction occurs according to Order lifecycle rules.

Similarly, a refund does not automatically return inventory.

---

## 51. Inventory and Order Cancellation

Cancellation behavior depends on the Order state and inventory history.

If inventory was previously deducted and the cancellation workflow allows inventory return:

* return is a new inventory movement;
* original deduction remains unchanged;
* served items are excluded from automatic return.

---

## 52. Inventory and Refund

A refund is a financial operation.

Refund creation does not automatically change stock.

If inventory correction is required, it must be performed through the appropriate authorized inventory workflow.

---

## 53. Offline Inventory

Trusted devices may perform permitted inventory operations while offline.

Offline operations must:

* use local UUIDs;
* use the latest valid authorized configuration;
* validate local stock;
* preserve transaction context;
* remain in the local synchronization queue.

Offline validation does not make the client permanently authoritative.

---

## 54. Offline Stock Conflict

A conflict may occur when offline stock assumptions differ from authoritative server state.

Example:

```text
Server stock = 2

Offline Device A:
consumes 2

Online Device B:
consumes 1 first

Device A reconnects
```

The server detects that the offline transaction cannot be applied under the authoritative state.

The system creates a conflict rather than creating negative stock.

---

## 55. Inventory Conflict Resolution

Inventory conflicts require explicit resolution by an authorized user.

Resolution records:

* original transaction;
* server state;
* conflict reason;
* decision;
* actor;
* timestamp;
* resulting adjustment/state.

The original offline event remains historically available.

---

## 56. Synchronization Ordering

Dependent inventory events must synchronize in dependency order.

For example:

```text
Purchase
   ↓
Stock Increase
   ↓
Sale Deduction
```

A sale that depends on a synchronized purchase must not be applied before its required dependency unless the server can independently validate the required stock state.

---

## 57. Inventory Idempotency

Every inventory-changing operation must use a stable transaction UUID.

If the same operation is submitted more than once:

* the first successful result remains authoritative;
* subsequent identical requests do not duplicate the stock movement.

This protects against:

* network retry;
* client retry;
* lost response;
* duplicate synchronization.

---

## 58. Inventory Concurrency

Critical stock operations use server-side transaction control.

The system must protect against:

* concurrent sales;
* concurrent purchases;
* simultaneous adjustments;
* simultaneous production;
* simultaneous returns;
* inventory count adjustments.

Only one logically valid final state may be committed for a conflicting stock resource.

---

## 59. Transaction Isolation

Inventory operations must use appropriate database transaction isolation and locking.

The exact database mechanism is an implementation concern, but the system behavior must guarantee:

* no negative stock;
* no lost stock movement;
* no duplicate movement;
* no invalid concurrent deduction.

---

## 60. Core Transaction Boundary

A core inventory transaction includes all state changes that must succeed or fail together.

Examples:

### Order acceptance

```text
Order Accepted
+
Required Inventory Deduction
```

### Semi-finished production

```text
Input Consumption
+
Output Creation
```

### Order modification

```text
Order Modification
+
Required Inventory Change
```

If one required part fails, the complete core operation fails.

---

## 61. Secondary Operations

The following are secondary operations:

* notifications;
* report regeneration;
* analytics;
* background synchronization metadata;
* non-critical display updates.

Failure of a secondary operation must not roll back a committed core inventory transaction.

Failed secondary operations must be retried or recorded as failed.

---

## 62. Inventory Audit

Important inventory operations must be audited.

Audit events include:

* purchase;
* sale deduction;
* production;
* return;
* manual adjustment;
* stock count;
* discrepancy confirmation;
* correction;
* offline conflict resolution;
* relevant configuration changes.

---

## 63. Inventory Audit Context

Audit records should contain:

* Event UUID;
* Business UUID;
* Branch UUID;
* Warehouse UUID where applicable;
* Employee/System actor;
* Device UUID;
* Transaction UUID;
* source;
* Entity type/UUID;
* old state;
* new state;
* reason;
* timestamp;
* result.

Audit records are immutable.

---

## 64. Historical Integrity

Inventory transactions must not be silently edited.

If an error is discovered:

```text
Original Transaction
        ↓
Correction Transaction
```

The original remains available.

This allows historical stock movements and business reports to be reconstructed.

---

## 65. Report Integration

Inventory reports may use:

* current stock;
* inventory movements;
* purchases;
* deductions;
* returns;
* adjustments;
* discrepancies;
* costing information.

Report generation must use the appropriate report snapshot/version model.

Historical reports must not change silently.

---

## 66. Subscription Restrictions

When the Business is read-only because of subscription expiry:

* inventory history remains viewable;
* permitted reports remain available;
* Excel export remains available according to permission;
* new modifying inventory operations are blocked.

Offline authorization must not bypass the restriction.

---

## 67. Employee Deactivation

If an employee becomes inactive:

* new inventory operations from that employee are rejected;
* offline events created after the effective inactive timestamp are rejected or become conflicts;
* historical inventory transactions remain valid.

---

## 68. Branch Switching

When an employee changes Branch context:

* effective permissions are recalculated;
* inventory context is changed to the selected Branch;
* stock from the previous Branch is not automatically exposed;
* operations require permission in the new Branch.

Cross-Branch inventory access requires explicit supported scope.

Cross-Branch transfer remains out of current scope.

---

## 69. Error Handling

Inventory errors are classified as:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

Examples:

```text
Insufficient Stock → Business Rule Violation
Unauthorized Adjustment → Authorization Error
Offline Stock Conflict → Conflict
Database Unavailable → Temporary Infrastructure Error
Invalid Product/Recipe → Validation Error
```

---

## 70. Recovery

Inventory recovery relies on:

* transaction rollback;
* idempotency;
* retry;
* synchronization queue;
* conflict resolution;
* immutable history;
* audit.

The system must never repair inventory by silently overwriting historical transactions.

---

## 71. Performance

Inventory operations must remain suitable for ordinary POS and office hardware.

Critical operations should avoid unnecessary:

* full inventory scans;
* synchronous report generation;
* notification processing;
* expensive historical queries.

Heavy reports and recalculations should run asynchronously.

---

## 72. System Invariants

The following invariants apply to Inventory Transaction System:

1. Inventory is isolated by Business and Branch context.
2. Inventory operations cannot cross Business boundaries.
3. Cross-Branch transfer is currently out of scope.
4. Every important inventory transaction has a stable UUID.
5. Historical inventory transactions are immutable.
6. Stock changes occur through explicit inventory operations.
7. Direct unexplained stock overwrites are prohibited.
8. Current stock must remain consistent with committed inventory transactions.
9. Negative stock is never allowed.
10. Order acceptance and required inventory deduction are atomic.
11. Insufficient stock rejects the complete stock-consuming operation.
12. Concurrent stock consumption cannot create negative stock.
13. Draft Orders do not deduct inventory.
14. Draft Orders do not reserve inventory.
15. Recipe-based sales use the applicable approved Recipe Version.
16. Historical transactions preserve their original recipe context.
17. Semi-finished production consumes inputs and creates output atomically.
18. Actual production output is explicitly recorded.
19. Yield/loss differences remain traceable.
20. Set sales use the applicable Set configuration.
21. Set configuration changes do not rewrite historical sales.
22. Order quantity increases require sufficient additional stock.
23. Failed inventory return rolls back the complete Order modification.
24. Inventory returns are separate movements.
25. Served items never automatically return inventory.
26. Purchases increase stock only after valid confirmation.
27. Purchase cost history is immutable.
28. FIFO and Average Cost are distinct costing concepts.
29. Last Purchase Cost is distinct from FIFO and Average Cost.
30. Custom markup uses the configured Last Purchase Cost.
31. Manual stock changes require appropriate permission.
32. Manual stock decreases require a reason.
33. Inventory count does not automatically change stock.
34. Count discrepancy must be confirmed before adjustment.
35. Corrections create new transactions instead of rewriting originals.
36. Low-stock warnings do not permit negative stock.
37. Shopping lists do not change inventory.
38. Equipment availability is separate from stock quantity.
39. Inventory operations retain relevant Employee and Device context.
40. System-generated operations use SYSTEM actor where applicable.
41. Cash Session context is included only where relevant.
42. Payment does not automatically create inventory movement.
43. Refund does not automatically return inventory.
44. Cancellation inventory return follows explicit business rules.
45. Offline inventory operations require trusted authorized devices.
46. Offline transactions retain their original UUIDs.
47. Server validation remains authoritative after synchronization.
48. Offline stock conflicts never silently create negative stock.
49. Inventory conflicts require explicit resolution.
50. Conflict resolution is separately auditable.
51. Dependent inventory events synchronize in dependency order.
52. Duplicate synchronization cannot duplicate stock movement.
53. Critical inventory operations use server-side concurrency control.
54. Core inventory failures roll back the affected transaction.
55. Secondary failures do not roll back committed inventory transactions.
56. Important inventory changes are audited.
57. Audit records are immutable.
58. Subscription expiry blocks modifying inventory operations.
59. Offline authorization cannot bypass subscription restrictions.
60. Deactivated employees cannot create new valid inventory operations.
61. Branch switching recalculates inventory scope and permissions.
62. Historical inventory data remains available after employee deactivation.
63. Inventory reports use authoritative inventory state.
64. Historical report versions remain immutable.
65. Inventory recovery never silently overwrites historical data.
66. POS operations must not be blocked by heavy inventory reporting.
67. Inventory synchronization must not block normal POS operation.
68. Every stock decrease must be explainable by a valid business operation.
69. Every stock increase must be explainable by a valid business operation.
70. Inventory state must remain reconstructable from transaction history and correction history.

---

## 73. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
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

**Current Document:** `16_Inventory_Transaction_System.md`

**Next Document:** `17_Products_Recipes_and_Sets.md`

