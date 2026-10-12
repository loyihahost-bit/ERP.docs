# 13. Inventory and Recipe Testing

**Document ID:** TEST-13
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing architecture and business correctness requirements for inventory, stock, recipes, semi-finished products, stock deductions, FIFO consumption, inventory adjustments, and related inventory workflows.

Inventory testing must prove that the system maintains correct stock quantities, correct product composition, correct recipe behavior, correct historical records, and correct branch-level inventory state under normal, concurrent, offline, and failure conditions.

Inventory correctness is especially important because inventory data directly affects:

* product availability;
* order acceptance;
* recipe execution;
* semi-finished product production;
* purchasing and shopping recommendations;
* food cost calculations;
* inventory reports;
* branch profitability;
* financial results;
* historical order correctness.

The primary principle is:

> Inventory testing must prove that every stock movement has a valid business reason, correct quantity, correct source, correct destination, correct product, correct branch scope, and traceable historical meaning.

---

# 2. Scope

This document covers testing for:

* raw ingredients;
* ready-to-use products;
* semi-finished products;
* recipes;
* recipe components;
* recipe versions;
* recipe approval;
* stock receipts;
* stock deductions;
* FIFO consumption;
* yield loss and shrinkage;
* inventory adjustments;
* inventory discrepancies;
* stock availability;
* low-stock thresholds;
* shopping lists;
* manual shopping-list items;
* prepared-in-branch inventory;
* bought-ready inventory;
* warehouses;
* branch inventory;
* product availability;
* order-driven stock deduction;
* recipe modification during order entry;
* archived recipes and products;
* inventory reports;
* historical inventory state;
* offline inventory operations;
* synchronization;
* concurrent stock operations;
* idempotency;
* auditability;
* failure and recovery behavior.

This document does not redefine the general concurrency strategy, offline synchronization architecture, security testing architecture, or database testing architecture. Those concerns are covered by:

* `03_Unit_Testing_Architecture.md`
* `04_Domain_Testing_Architecture.md`
* `05_Application_and_Use_Case_Testing.md`
* `06_Repository_and_Database_Integration_Testing.md`
* `08_Integration_Testing_Architecture.md`
* `10_Offline_and_Synchronization_Testing.md`
* `11_Concurrency_and_Consistency_Testing.md`
* `14_Authentication_Authorization_and_Security_Testing.md`

This document applies those testing principles specifically to inventory and recipe behavior.

---

# 3. Inventory Testing Principles

Inventory tests MUST follow these principles:

1. Stock quantities must never become negative through a valid business operation.
2. Every stock movement must have a traceable business reason.
3. Stock movements must belong to the correct business and branch scope.
4. A stock deduction must correspond to an actual business event.
5. A successful order must produce the expected inventory effect.
6. A failed order must not create an unintended inventory deduction.
7. Duplicate processing must not duplicate a stock movement.
8. FIFO behavior must be deterministic and verifiable.
9. Recipe composition must be tested independently from stock availability.
10. Recipe changes must not silently rewrite historical inventory meaning.
11. Semi-finished products must preserve their component dependency structure.
12. Yield loss and shrinkage must be represented consistently.
13. Inventory adjustments must preserve the original history.
14. Inventory discrepancies must be explicitly recorded.
15. Branch inventory must remain isolated.
16. Offline inventory operations must synchronize without creating duplicate effects.
17. Concurrent stock operations must preserve inventory invariants.
18. Inventory reports must reconcile with the underlying stock ledger.
19. Archived products and recipes must preserve historical references.
20. Inventory correctness takes priority over performance shortcuts.

---

# 4. Inventory Domain Model Under Test

Inventory testing must recognize the following conceptual entities.

## 4.1 Product

A product may represent:

* raw ingredient;
* ready-to-use product;
* semi-finished product;
* other inventory-managed item defined by the business model.

Tests must verify that product type affects only the business rules that are explicitly defined for that type.

---

## 4.2 Stock

Stock represents the currently available quantity of an inventory item within its valid inventory scope.

Tests must distinguish:

* available quantity;
* reserved or otherwise committed quantity if supported;
* consumed quantity;
* adjusted quantity;
* historical movement quantity.

Tests must never assume that a single numeric field is sufficient to prove historical inventory correctness.

---

## 4.3 Stock Movement

A stock movement represents a change to inventory.

Typical movement reasons include:

* purchase/receipt;
* production;
* order consumption;
* adjustment;
* discrepancy correction;
* transfer where supported;
* waste/loss where supported;
* other explicitly authorized inventory operations.

Every movement must have sufficient information to explain:

* what changed;
* by how much;
* why it changed;
* where it changed;
* when it changed;
* which business operation caused it.

---

## 4.4 Recipe

A recipe defines the components required to produce or sell a product.

A recipe may reference:

* raw ingredients;
* ready products;
* semi-finished products.

Tests must verify recipe composition independently from whether those components currently exist in stock.

---

## 4.5 Semi-Finished Product

A semi-finished product is an inventory item whose composition is defined through its own recipe or component structure.

For example:

```text
Semi-Finished Meat Sauce
    1 kg meat
    200 g mayonnaise
    spices
```

Testing must verify the dependency chain:

```text
Finished Product
        ↓
Semi-Finished Product
        ↓
Raw Ingredients
```

The system must preserve enough information to determine why raw inventory was consumed.

---

# 5. Stock Ledger Testing

The stock ledger is the primary source for verifying inventory history.

Tests must verify that each stock movement:

* references the correct product;
* belongs to the correct business;
* belongs to the correct branch or inventory scope;
* has the correct quantity;
* has the correct direction;
* has a valid reason;
* has the correct timestamp;
* references the originating business operation where required;
* cannot silently disappear from history.

## 5.1 Positive Tests

Examples:

* receiving 10 kg of flour increases flour stock by 10 kg;
* consuming 2 kg of flour decreases stock by 2 kg;
* producing 5 kg of a semi-finished product creates the expected stock;
* an authorized inventory adjustment changes stock by the intended amount.

## 5.2 Negative Tests

Examples:

* unknown product movement is rejected;
* invalid quantity is rejected;
* zero quantity is rejected where not meaningful;
* negative quantity cannot bypass normal movement rules;
* unauthorized adjustment is rejected;
* movement for another branch is rejected;
* movement without a valid reason is rejected.

---

# 6. Stock Receipt Testing

Stock receipt tests verify that purchased or otherwise received inventory enters the correct stock.

Tests must cover:

* product identification;
* quantity;
* unit;
* price;
* source;
* date;
* branch;
* warehouse where applicable;
* receipt status;
* historical movement.

For example:

```text
Purchase:
Flour = 50 kg
Price = X
Source = Supplier A
Branch = Branch 1
```

The test must verify both:

1. current stock;
2. historical receipt information.

A successful receipt must not create duplicate stock if the same operation is retried.

---

# 7. FIFO Testing

FIFO must be tested as a business rule rather than merely as an implementation detail.

FIFO means that when multiple stock batches exist, earlier eligible stock is consumed before later eligible stock.

Example:

```text
Batch A:
10 kg
Received: Day 1

Batch B:
20 kg
Received: Day 2
```

A 12 kg consumption must result in:

```text
Batch A → 10 kg consumed
Batch B → 2 kg consumed
```

Remaining:

```text
Batch A → 0 kg
Batch B → 18 kg
```

## 7.1 FIFO Test Cases

Tests must cover:

* one batch;
* multiple batches;
* exact batch consumption;
* partial batch consumption;
* consumption across multiple batches;
* multiple products;
* identical receipt timestamps;
* different receipt timestamps;
* batch exhaustion;
* insufficient total stock;
* repeated consumption;
* concurrent consumption;
* offline consumption followed by synchronization.

## 7.2 FIFO Integrity

Tests must verify that:

* later stock is not consumed before earlier eligible stock;
* consumed quantities do not exceed available batch quantities;
* a batch cannot be consumed twice;
* retries do not create duplicate consumption;
* historical batch information remains traceable.

FIFO tests must also verify the result after inventory reconciliation.

---

# 8. Recipe Testing

Recipe tests must verify business composition independently from inventory availability.

A valid recipe may exist even when its ingredients are currently unavailable.

Therefore:

```text
Recipe exists
≠
Required stock exists
```

Tests must explicitly distinguish these states.

## 8.1 Recipe Creation

Test:

* valid recipe creation;
* required components;
* component quantities;
* units;
* product type;
* duplicate components where prohibited;
* invalid quantities;
* invalid product references;
* circular dependencies where prohibited;
* incomplete recipe definitions.

## 8.2 Recipe Availability

Tests must verify:

* recipe exists but stock is unavailable;
* recipe exists and all stock is available;
* only some components are available;
* exact required quantity exists;
* quantity is insufficient;
* component is completely absent.

The system must not treat a missing ingredient as zero stock while still allowing an operation that requires it.

---

# 9. Recipe Approval Testing

New or changed recipes require approval before becoming active according to the business rules.

Tests must cover:

1. draft/new recipe;
2. recipe submitted for approval;
3. approval;
4. rejection where supported;
5. activation;
6. availability in the global menu;
7. availability in allowed branch menus;
8. historical recipe preservation.

A changed recipe must not unexpectedly modify already completed historical orders.

---

# 10. Recipe Version Testing

Recipe versions must be tested as historical business states.

Example:

```text
Recipe V1
Burger:
100 g meat

Recipe V2
Burger:
120 g meat
```

After V2 becomes active:

* new orders use V2;
* historical orders using V1 remain associated with V1;
* inventory history remains explainable;
* reports do not silently recalculate historical consumption using V2.

Tests must verify that changing a recipe does not rewrite historical inventory deductions.

---

# 11. Semi-Finished Product Testing

Semi-finished products require multi-level dependency testing.

Example:

```text
Lavash
  ↓
Meat Filling
  ↓
Meat
Mayonnaise
Spices
```

Tests must verify that consuming the final product correctly resolves the dependency chain according to the approved recipe model.

## 11.1 Production Testing

If a semi-finished product is prepared in a branch:

```text
Raw ingredients
        ↓
Production
        ↓
Semi-finished stock
```

Tests must verify:

* raw ingredient deduction;
* semi-finished product creation;
* production quantity;
* yield/loss handling;
* branch ownership;
* source = prepared in branch;
* historical traceability.

## 11.2 Bought-Ready Testing

If the same product is bought ready:

```text
Supplier
   ↓
Ready product stock
```

Tests must verify:

* no unnecessary raw-material deduction;
* source = bought ready;
* correct received quantity;
* correct stock;
* correct branch;
* correct historical source.

The two flows must not produce identical ledger histories when their business meanings differ.

---

# 12. Recipe-to-Inventory Deduction Testing

When an order is accepted and inventory deduction is required, tests must verify the complete relationship:

```text
Order
  ↓
Product
  ↓
Active Recipe
  ↓
Recipe Components
  ↓
Required Quantities
  ↓
Available Stock
  ↓
FIFO Selection
  ↓
Stock Deduction
```

The test must verify the final stock state, not only the fact that an order was accepted.

---

# 13. Insufficient Stock Testing

The system must not create negative stock.

Tests must cover:

### Exact stock

```text
Required: 5 kg
Available: 5 kg
Result: allowed
Remaining: 0 kg
```

### Insufficient stock

```text
Required: 5 kg
Available: 4 kg
Result: blocked
```

### Missing stock

```text
Required: 5 kg
Available: 0 kg
Result: blocked
```

The system must not silently:

* create negative stock;
* partially deduct stock while completing an operation that requires all components;
* ignore missing ingredients;
* bypass recipe requirements.

---

# 14. Recipe Modification During Order Entry

The order workflow allows recipe-related modification where permitted.

Tests must verify:

* recipe components are displayed correctly;
* current stock information is correct;
* adding an allowed component changes the calculated price correctly;
* removing an allowed component changes the calculated price correctly;
* non-recipe modifications are recorded as comments where required;
* unauthorized modifications are rejected;
* resulting inventory deduction matches the final accepted order state.

A failed modification must not create an unintended inventory movement.

---

# 15. Yield Loss and Shrinkage Testing

Where yield loss or shrinkage percentage is configured, tests must verify that production calculations use the configured business rule.

Example:

```text
Input:
10 kg raw material

Yield:
90%

Expected usable output:
9 kg
```

Tests must cover:

* zero loss;
* normal loss;
* configured percentage;
* boundary percentages;
* invalid percentages;
* production quantity;
* resulting raw-material consumption;
* resulting semi-finished stock;
* historical production record.

Yield calculations must not silently create additional usable stock.

---

# 16. Inventory Adjustment Testing

Inventory adjustments are controlled corrections, not replacements for normal stock operations.

Tests must cover:

* authorized adjustment;
* positive adjustment;
* negative adjustment;
* reason/comment;
* branch scope;
* affected product;
* before quantity;
* adjustment quantity;
* resulting quantity;
* audit information.

An adjustment must not erase the original stock history.

Example:

```text
Before: 100 units
Adjustment: -5
After: 95 units
```

The ledger must retain enough information to explain the change.

---

# 17. Inventory Discrepancy Testing

Physical inventory may differ from system inventory.

Tests must verify:

```text
System Quantity
       ↓
Physical Count
       ↓
Discrepancy
       ↓
Recorded Result
       ↓
Stock Adjustment
```

Examples:

```text
System: 100
Physical: 97
Discrepancy: -3
```

Tests must verify:

* original system quantity remains historically identifiable;
* physical count is recorded;
* discrepancy is recorded;
* resulting stock is correct;
* authorized correction is required;
* reports reflect the correction correctly.

A discrepancy must not simply overwrite the previous quantity.

---

# 18. Low-Stock and Shopping List Testing

Low-stock thresholds must produce the expected shopping recommendation.

Tests must cover:

* quantity above threshold;
* quantity exactly at threshold;
* quantity below threshold;
* zero stock;
* manual shopping-list item;
* automatic shopping-list item;
* duplicate recommendation prevention;
* stock replenishment;
* shopping-list recalculation.

Example:

```text
Threshold: 10 kg
Stock: 8 kg

Expected:
Low-stock condition detected
Shopping recommendation generated
```

The shopping list is advisory and must not itself increase inventory.

Inventory increases only after the appropriate receipt/production operation.

---

# 19. Shopping Completion Testing

After purchasing, the system must correctly record:

* quantity;
* price;
* source;
* date;
* branch;
* warehouse where applicable.

Tests must verify that entering a shopping-list completion does not accidentally create duplicate inventory.

The relationship must be:

```text
Shopping Recommendation
        ↓
Purchase
        ↓
Stock Receipt
        ↓
Inventory Increase
```

not:

```text
Shopping Recommendation
        ↓
Automatic Stock Increase
```

unless explicitly defined by the business operation.

---

# 20. Warehouse Testing

Where multiple warehouses exist, tests must verify that stock belongs to the correct warehouse.

Tests must cover:

* receipt into warehouse A;
* receipt into warehouse B;
* deduction from the correct warehouse;
* branch/warehouse scope;
* stock availability calculation;
* warehouse reporting;
* authorized movement between warehouses where supported.

A product available in Warehouse A must not automatically be treated as available in Warehouse B unless the business rules explicitly allow aggregation.

---

# 21. Branch Isolation Testing

Inventory is branch-sensitive.

Tests must verify:

```text
Business A
 ├── Branch 1
 │     └── Stock
 └── Branch 2
       └── Stock
```

Branch 1 must not consume, modify, or report Branch 2 inventory without an explicitly authorized cross-branch operation.

Test cases must include:

* order in Branch 1;
* inventory in Branch 1;
* inventory in Branch 2;
* same product in both branches;
* concurrent operations across branches;
* branch-scoped reports;
* branch-scoped adjustments;
* offline branch operations.

The same product identifier does not remove branch inventory isolation.

---

# 22. Archive and Historical Inventory Testing

Products and recipes that are no longer active may be archived rather than deleted.

Tests must verify that archiving:

* prevents inappropriate new usage;
* does not destroy historical references;
* does not remove previous stock movements;
* does not invalidate historical orders;
* does not rewrite historical recipes;
* does not break reports.

Historical inventory data must remain understandable after product or recipe archival.

---

# 23. Order and Inventory Atomicity

Order processing and inventory deduction must be tested as a coordinated business operation.

Critical cases:

### Successful operation

```text
Order accepted
+
Inventory deduction succeeds
=
Valid final state
```

### Inventory failure

```text
Order processing requires stock
+
Inventory deduction fails
=
No invalid completed state
```

### Retry

```text
Operation retried
=
No duplicate inventory effect
```

Tests must verify the transaction boundary defined by the application architecture.

---

# 24. Offline Inventory Testing

Offline inventory behavior must be tested according to `10_Offline_and_Synchronization_Testing.md`.

Inventory-specific tests must verify:

* offline stock visibility;
* authorized offline deductions;
* local durability;
* operation identity;
* synchronization;
* duplicate prevention;
* rejected operations;
* conflict handling;
* reconciliation;
* historical traceability.

Example:

```text
Device offline
      ↓
Order accepted locally
      ↓
Inventory deduction recorded locally
      ↓
Connection restored
      ↓
Synchronization
      ↓
Server inventory updated once
```

The same operation must not be applied twice.

---

# 25. Concurrency-Specific Inventory Testing

Inventory is a high-risk concurrency area.

Detailed concurrency methods are defined in `11_Concurrency_and_Consistency_Testing.md`.

Inventory-specific tests must verify scenarios such as:

```text
Stock = 10

Order A requires 7
Order B requires 5

Both start at approximately the same time.
```

The final system state must never imply that 12 units were successfully consumed from 10 units of stock.

Tests must also cover:

* simultaneous receipts;
* simultaneous deductions;
* simultaneous adjustments;
* simultaneous production;
* simultaneous recipe changes;
* order acceptance during stock adjustment;
* offline synchronization during online consumption;
* repeated requests;
* worker retries.

---

# 26. Idempotency Testing

Inventory operations must be safe against repeated processing where the operation contract requires idempotency.

Tests must verify:

```text
Same operation
    ↓
First execution → stock changes
Second execution → no duplicate stock change
```

Cases include:

* repeated order submission;
* repeated synchronization;
* worker retry;
* network timeout followed by retry;
* duplicated client request;
* duplicated event delivery.

Idempotency must be based on stable operation identity rather than unreliable assumptions such as request timing.

---

# 27. Inventory Report Reconciliation

Inventory reports must reconcile with stock movements.

Tests must verify relationships such as:

```text
Opening Stock
+ Receipts
+ Production
+ Positive Adjustments
- Consumption
- Loss/Waste
- Negative Adjustments
± Other Valid Movements
=
Closing Stock
```

The exact formula must follow the implemented inventory model, but every included movement must be accounted for.

Tests must verify:

* current stock;
* historical movements;
* selected-day reports;
* branch reports;
* warehouse reports;
* product reports;
* discrepancy reports;
* FIFO consumption history.

---

# 28. Financial Relationship Testing

Inventory testing must verify relevant relationships with financial data without duplicating the financial test architecture.

Examples:

* purchase price is stored with the appropriate receipt;
* inventory cost calculations use the intended stock information;
* recipe changes do not rewrite historical financial meaning;
* inventory adjustments remain traceable;
* reports use consistent historical inventory state.

Financial correctness is additionally covered by `12_Financial_and_Cash_Testing.md`.

---

# 29. Authorization-Sensitive Inventory Tests

Inventory operations must respect authorization boundaries.

Tests must verify permissions for:

* creating recipes;
* modifying recipes;
* approving recipes;
* viewing restricted recipes;
* creating adjustments;
* correcting discrepancies;
* modifying prices;
* managing branch inventory;
* accessing inventory reports;
* performing privileged inventory operations.

An authorized employee in Branch 1 must not automatically gain permission to modify Branch 2 inventory.

Authorization testing must additionally follow `14_Authentication_Authorization_and_Security_Testing.md`.

---

# 30. Inventory Failure Testing

Inventory failures must be explicitly tested.

Examples:

| Failure                           | Expected Result                                  |
| --------------------------------- | ------------------------------------------------ |
| Database failure during deduction | No invalid partial state                         |
| Network failure                   | Operation follows online/offline policy          |
| Duplicate request                 | No duplicate deduction                           |
| FIFO selection failure            | Operation does not silently complete incorrectly |
| Invalid recipe                    | Operation rejected                               |
| Missing ingredient                | Operation blocked                                |
| Insufficient stock                | Operation blocked                                |
| Worker retry                      | Idempotent result                                |
| Sync conflict                     | Conflict handled according to policy             |
| Product archived                  | Historical data remains valid                    |
| Invalid adjustment                | Adjustment rejected                              |

Failure behavior must be observable and diagnosable.

---

# 31. Test Data Strategy

Inventory tests require controlled stock datasets.

A standard dataset should include:

```text
Raw ingredients:
- Meat
- Flour
- Mayonnaise
- Spices

Semi-finished:
- Meat Filling

Ready products:
- Bottled Drink

Finished products:
- Lavash
- Burger
```

The dataset should include:

* multiple branches;
* multiple warehouses where supported;
* multiple FIFO batches;
* different receipt dates;
* insufficient stock;
* zero stock;
* archived products;
* multiple recipe versions;
* yield loss;
* inventory discrepancies.

Test data must be deterministic.

---

# 32. Inventory Test Matrix

| Area                   |    Unit | Domain | Application | DB/Integration |      E2E |
| ---------------------- | ------: | -----: | ----------: | -------------: | -------: |
| Stock quantity rules   |     Yes |    Yes |         Yes |            Yes |  Limited |
| Stock movements        | Limited |    Yes |         Yes |            Yes |      Yes |
| FIFO                   |     Yes |    Yes |         Yes |            Yes | Critical |
| Recipes                |     Yes |    Yes |         Yes |            Yes |      Yes |
| Semi-finished products |     Yes |    Yes |         Yes |            Yes | Critical |
| Order deductions       | Limited |    Yes |         Yes |            Yes | Critical |
| Inventory adjustments  |     Yes |    Yes |         Yes |            Yes |      Yes |
| Discrepancies          |     Yes |    Yes |         Yes |            Yes |      Yes |
| Low stock              |     Yes |    Yes |         Yes |            Yes |      Yes |
| Shopping lists         |     Yes |    Yes |         Yes |            Yes |      Yes |
| Branch isolation       | Limited |    Yes |         Yes |            Yes | Critical |
| Offline inventory      | Limited |    Yes |         Yes |            Yes | Critical |
| Concurrency            | Limited |    Yes |         Yes |            Yes | Critical |
| Historical recipes     |     Yes |    Yes |         Yes |            Yes |      Yes |

The same business rule should not be unnecessarily duplicated at every level. Higher-level tests should focus on proving that real boundaries preserve the lower-level behavior.

---

# 33. Critical Inventory Test Suite

The release-critical inventory suite should include at minimum:

1. Create a raw ingredient.
2. Receive stock.
3. Verify stock quantity.
4. Receive multiple FIFO batches.
5. Consume from the oldest batch first.
6. Consume across multiple batches.
7. Block consumption when total stock is insufficient.
8. Prevent negative stock.
9. Create a recipe without existing stock.
10. Approve a recipe.
11. Consume recipe ingredients through an order.
12. Verify ingredient quantities after deduction.
13. Create a semi-finished product.
14. Produce the semi-finished product from raw ingredients.
15. Verify dependency-based consumption.
16. Apply yield loss.
17. Record an inventory discrepancy.
18. Apply an authorized adjustment.
19. Generate a low-stock recommendation.
20. Complete a shopping operation and receive stock.
21. Archive a recipe and verify historical orders.
22. Change a recipe and verify historical orders remain unchanged.
23. Verify branch inventory isolation.
24. Process concurrent deductions safely.
25. Retry an inventory operation without duplicate effect.
26. Perform an offline inventory operation and synchronize it.
27. Verify inventory reconciliation.
28. Verify audit/history after correction.

This suite must be stable enough to run as a mandatory release gate.

---

# 34. Regression Testing

Every defect involving inventory or recipes must produce a regression test when practical.

Examples:

```text
Bug:
FIFO consumed newest batch first.

Regression:
Verify oldest eligible batch is consumed first.
```

```text
Bug:
Repeated order deducted ingredients twice.

Regression:
Repeat the same operation and verify one inventory effect.
```

```text
Bug:
Archived recipe changed historical order consumption.

Regression:
Verify historical recipe version remains unchanged.
```

Regression tests must be retained as long as the affected business rule remains valid.

---

# 35. Performance-Aware Inventory Testing

Inventory tests must verify correctness without introducing unnecessary performance requirements.

Performance testing should focus on realistic high-value scenarios:

* large stock ledgers;
* many products;
* many recipe components;
* long FIFO batch chains;
* many branches;
* high-frequency order deductions;
* large synchronization queues;
* inventory reports over large date ranges.

Performance optimization must not bypass:

* FIFO correctness;
* stock constraints;
* branch isolation;
* idempotency;
* transaction integrity;
* auditability.

Correctness remains the primary acceptance criterion.

---

# 36. Flaky Test Management

Inventory tests must avoid nondeterministic assumptions.

Tests must not depend on:

* uncontrolled timing;
* arbitrary sleep durations;
* random stock state;
* shared mutable test databases;
* execution order;
* uncontrolled external services.

Concurrency tests may intentionally control timing to reproduce a race condition, but the race scenario itself must remain deterministic and repeatable.

---

# 37. Change Impact Testing

Changes affecting the following areas must trigger inventory test review:

* product model;
* recipe model;
* recipe approval;
* stock movement model;
* FIFO logic;
* order processing;
* inventory adjustment;
* warehouse behavior;
* branch scope;
* pricing;
* semi-finished products;
* yield/loss calculation;
* offline synchronization;
* database constraints;
* stock reports;
* archival behavior.

The required test depth must be determined by business risk, not only by the size of the code change.

---

# 38. Relationship to Other Testing Documents

Inventory and recipe testing depends on and complements the following testing layers:

### `03_Unit_Testing_Architecture.md`

Defines isolated testing techniques used to test inventory rules.

### `04_Domain_Testing_Architecture.md`

Defines business-rule and invariant testing.

### `05_Application_and_Use_Case_Testing.md`

Verifies inventory workflows and orchestration.

### `06_Repository_and_Database_Integration_Testing.md`

Verifies persistence, constraints, transactions, and stock history.

### `08_Integration_Testing_Architecture.md`

Verifies integration between inventory, orders, workers, queues, and other subsystems.

### `09_End_to_End_and_POS_Testing.md`

Verifies inventory effects as part of complete POS workflows.

### `10_Offline_and_Synchronization_Testing.md`

Defines the general offline and synchronization testing model.

### `11_Concurrency_and_Consistency_Testing.md`

Defines the general concurrency and consistency testing model.

### `12_Financial_and_Cash_Testing.md`

Covers financial consequences related to inventory where applicable.

### `14_Authentication_Authorization_and_Security_Testing.md`

Defines authorization, isolation, and security testing for inventory operations.

---

# 39. Mandatory Inventory Invariants

The following are mandatory test invariants.

### Stock

1. Valid operations must not create negative stock.
2. Every stock movement must have a valid business reason.
3. Stock belongs to the correct business and branch scope.
4. Stock history must remain traceable.
5. A failed operation must not create an unintended stock effect.

### FIFO

6. Eligible older stock is consumed before newer stock.
7. No batch can be consumed beyond its available quantity.
8. FIFO results remain deterministic.
9. Retrying a FIFO operation does not duplicate consumption.

### Recipes

10. Recipes may exist even when required stock does not exist.
11. Invalid recipes cannot become active.
12. Recipe changes require the required approval.
13. Historical orders preserve the recipe meaning applicable at their time.
14. Archived recipes remain available for historical interpretation.

### Semi-Finished Products

15. Semi-finished products preserve their component dependencies.
16. Production consumes the correct raw materials.
17. Production creates the correct semi-finished quantity.
18. Yield loss is applied according to the configured business rule.
19. Prepared-in-branch and bought-ready inventory remain distinguishable.

### Orders

20. Order-driven deductions correspond to the accepted order state.
21. Insufficient required stock blocks the operation according to business rules.
22. Recipe modifications produce the expected final inventory effect.
23. Duplicate order processing cannot duplicate inventory deduction.

### Adjustments

24. Inventory discrepancies are explicitly recorded.
25. Adjustments preserve historical information.
26. Unauthorized adjustments are rejected.
27. Corrections cannot silently rewrite the original inventory history.

### Branches and Warehouses

28. Branch inventory remains isolated.
29. Warehouse stock remains correctly scoped.
30. Cross-branch or cross-warehouse movement requires explicit authorization and business rules.

### Offline and Concurrency

31. Offline inventory operations are durable before synchronization.
32. Synchronization does not duplicate inventory effects.
33. Concurrent deductions cannot consume more stock than is validly available.
34. Inventory operations remain consistent after retries and failures.

### Reporting

35. Inventory reports reconcile with valid stock movements.
36. Historical reports remain stable after recipe or product archival.
37. Corrections are visible in the appropriate historical records.

---

# 40. Acceptance Criteria

This document is considered correctly implemented when:

* inventory business rules have explicit tests;
* stock movement behavior is verified;
* FIFO behavior is verified;
* recipe composition is tested;
* semi-finished product dependencies are tested;
* order-driven deductions are tested;
* insufficient stock is handled correctly;
* negative stock cannot be produced by valid operations;
* inventory adjustments and discrepancies preserve history;
* recipe version changes do not rewrite historical meaning;
* low-stock and shopping-list behavior is verified;
* branch and warehouse boundaries are tested;
* offline inventory behavior is covered;
* concurrency and idempotency risks are covered;
* critical inventory workflows are included in release testing;
* inventory reports reconcile with the stock ledger;
* defects produce regression tests where appropriate;
* test data is deterministic and isolated;
* inventory correctness is not sacrificed for performance.

---

# 41. Final Testing Rule

Inventory testing is not complete merely because the current stock quantity appears correct.

A correct inventory system must be able to explain:

```text
What product changed?
        ↓
How much changed?
        ↓
Why did it change?
        ↓
Which recipe or operation caused it?
        ↓
Which batch was consumed?
        ↓
Which branch/warehouse was affected?
        ↓
Was the operation authorized?
        ↓
Was it applied exactly once?
        ↓
Can the historical result still be explained?
```

The final acceptance condition is:

> **Inventory is correct only when current stock, stock movements, recipes, FIFO consumption, production, deductions, adjustments, branch scope, historical records, and related business operations all describe one consistent and traceable business state.**

