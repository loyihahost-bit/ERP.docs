# Inventory and Warehouse Data Model

**Document ID:** DB-11
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* warehouses;
* inventory balances;
* inventory transactions;
* purchases;
* stock adjustments;
* stock discrepancies;
* production;
* consumption;
* returns;
* losses and shrinkage;
* stock thresholds;
* shopping list generation;
* inventory history;
* Branch-level stock isolation.

The inventory model must guarantee:

* no negative stock;
* atomic stock changes;
* complete historical traceability;
* Branch isolation;
* concurrency safety;
* offline synchronization support.

---

# 2. Inventory Model Overview

Inventory is Branch-scoped.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Warehouse
   ↓
Inventory Balance
   ↓
Product
```

A Product definition is Business-level, while its stock quantity is normally Branch/Warehouse-level.

---

# 3. Warehouse Identity

Every Warehouse has:

* UUID;
* Business;
* Branch;
* name;
* status;
* timestamps.

Warehouse UUID must be:

* immutable;
* globally unique;
* never reused.

---

# 4. Warehouse Ownership

Every Warehouse belongs to exactly one Business and one Branch.

Conceptually:

```text
Warehouse.business_id
        =
Branch.business_id
```

Cross-Business Warehouse relationships are forbidden.

---

# 5. Warehouse Lifecycle

Conceptual lifecycle:

```text
Active
  ↓
Inactive
  ↓
Archived
```

Archiving a Warehouse must not delete historical inventory transactions.

---

# 6. Branch Inventory Isolation

Inventory operations must always execute within:

```text
Business → Branch → Warehouse
```

A Branch employee must not access another Branch's inventory unless their effective permission and Branch scope explicitly allow it.

---

# 7. Inventory Balance

Inventory Balance represents the current available stock for a Product in a Warehouse.

Conceptually:

```text
Warehouse
   +
Product
   ↓
Inventory Balance
```

A Product should have at most one active balance record per Warehouse.

Recommended uniqueness:

```text
UNIQUE(warehouse_id, product_id)
```

---

# 8. Inventory Balance Fields

Conceptual fields:

```text
id
business_id
branch_id
warehouse_id
product_id
quantity
reserved_quantity
available_quantity
updated_at
version
```

`available_quantity` must not become negative.

If reservation is not implemented for a specific operation, `reserved_quantity` remains zero.

---

# 9. Quantity Model

Inventory quantities must use exact decimal-compatible database types.

Floating-point values must not be used for authoritative stock quantities.

Examples:

```text
10 kg
1.250 kg
500 g
2.5 l
3 pieces
```

---

# 10. Unit of Measurement

Every inventory-managed Product must have a controlled Unit of Measurement.

Examples:

* kg;
* g;
* l;
* ml;
* piece.

Unit conversion must be deterministic.

---

# 11. Inventory Transaction

Inventory changes must be represented by Inventory Transactions.

Examples:

* purchase;
* sale consumption;
* production consumption;
* production output;
* return;
* adjustment;
* discrepancy correction;
* loss;
* shrinkage.

The Inventory Transaction is the historical source for stock movement.

---

# 12. Inventory Transaction Identity

Every inventory transaction has:

* UUID;
* Business;
* Branch;
* Warehouse;
* Product;
* quantity;
* transaction type;
* actor;
* timestamp;
* Transaction UUID.

The transaction UUID must be immutable and idempotency-safe.

No Client Transaction ID is required.

---

# 13. Transaction Quantity

Inventory transaction quantity must have a clear direction.

Two implementation approaches are acceptable:

```text
IN / OUT
```

or:

```text
positive / negative quantity
```

The chosen physical implementation must remain consistent.

The logical meaning must always be unambiguous.

---

# 14. Inventory Transaction Types

Supported logical transaction types include:

```text
PURCHASE
SALE_CONSUMPTION
PRODUCTION_CONSUMPTION
PRODUCTION_OUTPUT
RETURN
ADJUSTMENT_IN
ADJUSTMENT_OUT
LOSS
SHRINKAGE
CORRECTION
```

Additional types may be added through controlled schema evolution.

---

# 15. Purchase

A Purchase increases inventory.

Purchase data may include:

* supplier;
* quantity;
* unit;
* unit price;
* total price;
* purchase date;
* batch;
* source;
* comment;
* employee;
* Branch;
* Warehouse.

The Purchase creates Inventory Transactions.

---

# 16. Supplier

Supplier management is intentionally shallow.

A purchase may reference a Supplier.

A Product may have multiple Suppliers.

Supplier changes must not modify historical purchases.

---

# 17. Purchase Price

Purchase records preserve:

* quantity;
* unit price;
* total amount;
* purchase timestamp.

Later purchases must not rewrite previous purchase prices.

---

# 18. Last Purchase Cost

The current Last Purchase Cost may be derived from the latest valid purchase record.

It is operational state, not historical truth.

Historical transactions retain their original purchase prices.

---

# 19. Batch

A Purchase may contain a Batch reference.

Batch data may include:

* batch UUID;
* Product;
* Warehouse;
* purchase reference;
* received quantity;
* remaining quantity;
* unit cost;
* received timestamp.

Batch tracking supports FIFO and traceability.

---

# 20. FIFO

Inventory consumption follows FIFO where applicable.

Conceptually:

```text
Oldest available batch
        ↓
Consumed first
```

FIFO calculation must not rewrite historical Inventory Transactions.

---

# 21. Sale Consumption

When an Order becomes Accepted:

1. required stock is calculated;
2. available stock is validated;
3. Inventory Transactions are created;
4. balances are updated;
5. Order acceptance succeeds atomically.

If stock is insufficient:

```text
Order Acceptance = Rejected
```

No partial stock deduction is allowed.

---

# 22. Recipe-Based Consumption

If a Product has a Recipe, inventory consumption follows the effective Recipe Version.

Conceptually:

```text
Order
 ↓
Product
 ↓
Recipe Version
 ↓
Components
 ↓
Inventory Transactions
```

Historical consumption must preserve the Recipe Version used.

---

# 23. Semi-Finished Production

Production of Semi-Finished Products consumes component stock and creates output stock.

Example:

```text
Meat       -10 kg
Mayonnaise -2 kg
Spices     -0.1 kg
             ↓
Prepared Meat +8.5 kg
```

The entire production operation must be atomic.

---

# 24. Actual Production Quantity

Expected output and actual output are separate.

Production records must preserve:

* planned quantity;
* actual quantity;
* expected loss;
* actual loss;
* Recipe Version.

Actual output must not rewrite Recipe configuration.

---

# 25. Production Loss

Actual loss or shrinkage is recorded as an inventory transaction.

It must not silently modify the Recipe.

Example:

```text
Expected output: 10 kg
Actual output:    9 kg
Loss:             1 kg
```

---

# 26. Inventory Return

Inventory can be returned when permitted by an Order modification or correction workflow.

Return must identify:

* source transaction;
* Product;
* quantity;
* Warehouse;
* actor;
* reason;
* timestamp.

Historical original transactions remain unchanged.

---

# 27. No Automatic Refund Inventory Return

A refund does not automatically return inventory.

Inventory return must be a separate explicitly authorized operation.

This preserves the distinction between:

```text
Financial refund
```

and:

```text
Physical inventory movement
```

---

# 28. Manual Inventory Adjustment

Manual stock adjustment requires the appropriate permission.

The adjustment must contain:

* Product;
* Warehouse;
* previous quantity;
* adjustment quantity;
* resulting quantity;
* reason;
* comment;
* actor;
* timestamp;
* device;
* Transaction UUID.

No adjustment may create negative stock.

---

# 29. Inventory Discrepancy

During inventory counting:

1. expected quantity is calculated;
2. physical quantity is entered;
3. discrepancy is shown;
4. authorized employee confirms adjustment;
5. adjustment transaction is created.

The physical count must not silently rewrite expected stock.

---

# 30. Inventory Count

An Inventory Count may contain:

* Count UUID;
* Business;
* Branch;
* Warehouse;
* employee;
* start time;
* completion time;
* status.

Possible states:

```text
DRAFT
COUNTING
REVIEW
CONFIRMED
CANCELLED
```

---

# 31. Count Snapshot

An Inventory Count should preserve the expected quantity at the time of counting.

This prevents later stock movements from rewriting the original comparison basis.

---

# 32. Stock Discrepancy

Discrepancy data may include:

```text
expected_quantity
counted_quantity
difference
reason
confirmed_by
confirmed_at
```

The discrepancy itself is historical data.

The resulting adjustment is a separate Inventory Transaction.

---

# 33. Negative Stock Prevention

Negative stock is forbidden.

Any operation that would produce:

```text
quantity < 0
```

must be rejected.

This rule applies to:

* online sales;
* offline sales after server validation;
* production;
* manual adjustments;
* corrections;
* synchronized operations.

---

# 34. Concurrent Stock Changes

Concurrent stock changes must be serialized safely.

Example:

```text
Stock = 1

Order A → consumes 1
Order B → consumes 1
```

Only one operation may successfully consume the final unit.

The second operation must be rejected.

---

# 35. Database Locking

Where required, inventory balance rows should be locked during:

1. stock validation;
2. stock modification;
3. transaction creation.

The balance update and inventory transaction creation must occur in one database transaction.

---

# 36. Inventory Atomicity

Inventory operations must be atomic.

Example:

```text
Order Acceptance
    +
Inventory Deduction
```

must either:

```text
Both succeed
```

or:

```text
Both rollback
```

Partial success is forbidden for the core transaction.

---

# 37. Inventory Return Atomicity

If an inventory return is part of an Order modification, the complete modification must succeed together with the return.

If the return fails:

```text
Order Modification = Rollback
```

---

# 38. Inventory and Order UUID

Inventory Transactions related to Orders should reference:

* Order UUID;
* Order Item UUID where applicable;
* Transaction UUID.

This supports reconstruction and idempotency.

---

# 39. Inventory and Payment Separation

Inventory is not controlled by Payment state.

Payment completion does not automatically create an inventory transaction.

Inventory consumption occurs according to Order acceptance rules.

---

# 40. Inventory and Cash Separation

Cash Sessions do not own Inventory.

An Inventory Transaction may reference:

* Employee;
* Device;
* Cash Session where operational context requires it;

but inventory ownership remains Branch/Warehouse based.

---

# 41. Inventory and Branch Transfer

Branch-to-Branch transfer is outside the current scope.

The schema should not prevent future transfer functionality, but no current operational workflow depends on it.

---

# 42. Equipment-Based Product Availability

A Product may become unavailable because required equipment is broken.

Equipment availability must not directly modify stock.

Example:

```text
Product = Active
Stock = 100
Equipment = Broken
```

Effective sale availability becomes:

```text
Unavailable
```

without changing inventory quantity.

---

# 43. Stock Threshold

Each inventory-managed Product may have a low-stock threshold.

Conceptually:

```text
Product
   ↓
Inventory Threshold
   ↓
Branch/Warehouse
```

The threshold may be Business or Branch configurable according to configuration rules.

---

# 44. Low Stock

When:

```text
Current Stock <= Threshold
```

the system may create a low-stock notification and/or shopping-list suggestion.

Low stock does not automatically create an inventory adjustment.

---

# 45. Out of Stock

When:

```text
Current Stock = 0
```

the Product becomes unavailable for inventory-dependent sales.

The Product itself is not archived.

---

# 46. Shopping List

Shopping List entries may be generated from:

* low stock;
* zero stock;
* manual additions.

Shopping List is advisory.

It does not modify inventory until an actual Purchase is recorded.

---

# 47. Purchase Confirmation

When goods are physically purchased and received:

1. Purchase is recorded;
2. quantity is validated;
3. inventory increases;
4. purchase cost is stored;
5. relevant Batch data is recorded.

The stock update and purchase transaction must be atomic.

---

# 48. Inventory Source

Inventory additions may identify source:

```text
BOUGHT_READY
PREPARED_IN_BRANCH
```

Source belongs to the inventory operation, not Product identity.

---

# 49. Inventory Corrections

Corrections must never silently rewrite original Inventory Transactions.

A correction creates a new transaction referencing the original.

Conceptually:

```text
Original Transaction
       ↓
Correction Transaction
```

---

# 50. Correction Chain

A correction should preserve:

* original Transaction UUID;
* correction Transaction UUID;
* reason;
* actor;
* timestamp;
* previous state;
* corrected state.

Correction chains must be reconstructable.

---

# 51. Inventory Audit

Important inventory events should create Audit records:

* purchase;
* manual adjustment;
* discrepancy confirmation;
* correction;
* production;
* inventory return;
* loss;
* shrinkage;
* configuration changes affecting inventory.

---

# 52. Offline Inventory

Trusted devices may perform authorized offline inventory operations.

Offline operations must:

* use local validated configuration;
* create UUID-based transactions;
* store transactions durably;
* preserve Business/Branch/Warehouse scope;
* synchronize later.

Server validation remains authoritative.

---

# 53. Offline Stock Conflict

If offline stock consumption conflicts with newer server stock:

```text
Conflict
```

must be created.

The system must not silently produce negative stock.

Authorized conflict resolution requires:

* reason;
* actor;
* timestamp;
* audit record.

---

# 54. Inventory Synchronization

Inventory synchronization should:

1. authenticate the Device;
2. validate Business;
3. validate Branch;
4. validate Employee;
5. validate permission;
6. validate Product;
7. validate Warehouse;
8. validate configuration;
9. validate transaction UUID;
10. validate stock;
11. apply transaction atomically;
12. return deterministic result.

Duplicate Transaction UUIDs must not create duplicate stock movements.

---

# 55. Inventory Idempotency

If the same Inventory Transaction is submitted more than once:

```text
First submission → Applied
Repeated submission → Existing result
```

It must not consume stock twice.

---

# 56. Inventory Transaction Status

Operational synchronization may track:

```text
PENDING
SYNCING
APPLIED
REJECTED
CONFLICT
```

The authoritative inventory transaction remains server-controlled.

---

# 57. Warehouse Deactivation

A Warehouse cannot receive new normal inventory operations after deactivation.

Historical transactions remain readable.

Existing stock must be handled through an authorized workflow before permanent lifecycle deletion.

---

# 58. Product Archival

Archiving a Product does not delete:

* stock history;
* purchase history;
* production history;
* adjustment history;
* discrepancy history.

Existing stock remains historically visible.

---

# 59. Inventory Data Lifecycle

Inventory follows Business data lifecycle rules.

During subscription read-only state:

* inventory history remains visible;
* modifying inventory operations are blocked.

During Business deletion:

* dependency-aware deletion removes inventory data;
* deletion is idempotent;
* stale offline events cannot recreate inventory state.

---

# 60. Inventory Reporting

Inventory data supports:

* current stock;
* stock movements;
* purchases;
* consumption;
* production;
* discrepancies;
* losses;
* shrinkage;
* inventory valuation where implemented;
* Branch performance.

Reports must use immutable transaction history.

---

# 61. FIFO and Historical Integrity

FIFO allocation must not modify the underlying historical transaction records.

Allocation may be represented through:

* batch consumption records;
* inventory allocation records;
* or equivalent normalized structures.

Historical purchase and consumption transactions remain immutable.

---

# 62. Inventory Database Structure

Recommended logical structure:

```text id="j0s0wt"
Business
   │
   └── Branch
         │
         └── Warehouse
                │
                ├── InventoryBalance
                │
                ├── InventoryCount
                │
                └── InventoryTransaction
                         │
                         ├── Purchase
                         ├── Production
                         ├── Adjustment
                         ├── Consumption
                         └── Return
```

Related:

```text id="e5b0gi"
InventoryTransaction
   ├── Product
   ├── RecipeVersion
   ├── Order
   ├── Employee
   ├── Device
   └── CashSession
```

---

# 63. Suggested Core Fields

## Warehouse

```text id="k4l7zq"
id
business_id
branch_id
name
status
created_at
updated_at
archived_at
version
```

## InventoryBalance

```text id="q3q7ry"
id
business_id
branch_id
warehouse_id
product_id
quantity
reserved_quantity
updated_at
version
```

## InventoryTransaction

```text id="c8q4x2"
id
business_id
branch_id
warehouse_id
product_id
transaction_type
quantity
unit_id
order_id
order_item_id
recipe_version_id
employee_id
device_id
cash_session_id
transaction_uuid
reason
comment
created_at
```

## Purchase

```text id="qj4y3d"
id
business_id
branch_id
warehouse_id
supplier_id
purchase_date
total_amount
comment
created_by_employee_id
created_at
```

## PurchaseItem

```text id="s8m1z6"
purchase_id
product_id
quantity
unit_id
unit_price
total_price
batch_id
```

## InventoryCount

```text id="p9f3r1"
id
business_id
branch_id
warehouse_id
status
started_at
completed_at
created_by_employee_id
confirmed_by_employee_id
created_at
updated_at
```

## InventoryCountItem

```text id="v2h7m8"
inventory_count_id
product_id
expected_quantity
counted_quantity
difference
reason
confirmed_at
```

The final physical schema may normalize additional data.

---

# 64. Database Constraints

Recommended constraints include:

```text id="0d3b4x"
UNIQUE(warehouse_id, product_id)
```

and:

```text id="3y1w9m"
CHECK(quantity >= 0)
```

for authoritative balance quantities.

Transaction UUID:

```text id="2s4g8n"
UNIQUE(business_id, transaction_uuid)
```

Tenant consistency must ensure:

```text id="6v8k2x"
Warehouse.business_id
=
Branch.business_id
=
InventoryBalance.business_id
=
InventoryTransaction.business_id
```

---

# 65. Indexing

Important indexes include:

* InventoryBalance by Warehouse + Product;
* InventoryBalance by Branch + Product;
* InventoryTransaction by Business + Branch;
* InventoryTransaction by Product;
* InventoryTransaction by Order;
* InventoryTransaction by Transaction UUID;
* InventoryTransaction by timestamp;
* Purchase by Branch/date;
* Batch by Product/Warehouse;
* InventoryCount by Branch/status.

Indexes must support high-frequency POS stock validation.

---

# 66. Performance

Inventory is part of the POS critical path.

Therefore:

* stock validation must be fast;
* balance lookup must use indexed access;
* transactions must avoid unnecessary joins;
* historical reporting must not block operational writes;
* heavy reports should run asynchronously;
* cache may accelerate read operations;
* authoritative stock remains in PostgreSQL.

---

# 67. Transaction Boundaries

### Core transaction

The following operations may belong to one database transaction:

```text
Order Acceptance
+
Inventory Validation
+
Inventory Deduction
```

and:

```text
Purchase Confirmation
+
Inventory Increase
```

and:

```text
Production
+
Component Consumption
+
Output Creation
```

### Secondary processing

The following should not roll back the inventory transaction:

* notifications;
* printer operations;
* report generation;
* analytics;
* non-critical external processing.

---

# 68. Database vs Application Responsibilities

### Database responsibilities

* inventory identity;
* Branch/Warehouse ownership;
* balance integrity;
* quantity constraints;
* uniqueness;
* transaction persistence;
* foreign-key integrity;
* concurrency control.

### Application responsibilities

* Recipe expansion;
* FIFO allocation;
* stock validation workflow;
* permission checks;
* threshold evaluation;
* shopping-list generation;
* discrepancy workflow;
* conflict resolution;
* equipment availability;
* Business rules.

---

# 69. Core Invariants

The following invariants are mandatory:

1. Every Warehouse belongs to exactly one Business.
2. Every Warehouse belongs to exactly one Branch.
3. Warehouse and Branch belong to the same Business.
4. Every Inventory Balance belongs to one Warehouse.
5. Every Inventory Balance references one Product.
6. A Warehouse/Product pair has at most one active balance.
7. Inventory quantities use exact numeric representation.
8. Negative authoritative stock is forbidden.
9. Every inventory movement has a Transaction UUID.
10. Transaction UUID is idempotency-safe.
11. Duplicate Transaction UUIDs cannot create duplicate movements.
12. Inventory Transactions preserve historical movement.
13. Historical Inventory Transactions are not silently rewritten.
14. Corrections create new transactions.
15. Correction chains remain reconstructable.
16. Purchase transactions increase stock.
17. Sale consumption decreases stock.
18. Production consumption decreases component stock.
19. Production output increases output stock.
20. Inventory returns are separate transactions.
21. Refunds do not automatically return inventory.
22. Manual adjustments require appropriate permission.
23. Manual adjustments require a reason.
24. Inventory discrepancies preserve expected and counted quantities.
25. Count snapshots preserve the original comparison basis.
26. Discrepancy confirmation creates an explicit adjustment.
27. FIFO does not rewrite historical transactions.
28. Purchase prices remain historically immutable.
29. Last Purchase Cost does not rewrite historical costs.
30. Stock validation occurs before stock deduction.
31. Stock validation and deduction are atomic.
32. Order acceptance and required inventory deduction are atomic.
33. Failed inventory deduction rejects Order acceptance.
34. Partial Order inventory deduction is forbidden.
35. Inventory return failure rolls back the related Order modification.
36. Concurrent stock operations are serialized safely.
37. Only one operation may consume the final available unit.
38. Inventory is Branch-scoped.
39. Warehouse is Branch-scoped.
40. Client-supplied Business IDs cannot bypass tenant isolation.
41. Client-supplied Branch IDs cannot bypass Branch authorization.
42. Product and Warehouse must belong to the same Business.
43. Inventory Transactions preserve Branch scope.
44. Inventory Transactions preserve Warehouse scope.
45. Recipe-based consumption references the effective Recipe Version.
46. Historical consumption retains the Recipe Version used.
47. Production records preserve actual output.
48. Actual loss is separate from Recipe configuration.
49. Equipment failure does not modify stock quantity.
50. Low stock does not automatically modify stock.
51. Shopping Lists do not modify stock.
52. Purchase confirmation modifies stock atomically.
53. Offline inventory operations require a trusted device.
54. Offline inventory operations preserve UUID identity.
55. Offline transactions are server-validated.
56. Offline stock conflicts are explicit.
57. Offline conflict resolution is authorized and audited.
58. Synchronization cannot create duplicate stock movement.
59. Synchronization cannot bypass Business scope.
60. Synchronization cannot bypass Branch scope.
61. Synchronization cannot bypass Warehouse scope.
62. Inventory cache is not authoritative.
63. Inventory history remains readable during subscription read-only state.
64. Inventory modifications are blocked when entitlement does not allow them.
65. Warehouse archival does not delete history.
66. Product archival does not delete inventory history.
67. Inventory data follows Business lifecycle rules.
68. Stale offline transactions cannot resurrect deleted Business inventory.
69. Inventory reports use historical transaction data.
70. Heavy inventory reports must not block POS-critical transactions.

---

## Related Documents

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

