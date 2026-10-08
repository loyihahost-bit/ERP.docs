# Order Domain

**Document ID:** DA-06
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Order domain represents the operational customer order created and processed by a Branch.

It is responsible for:

* order identity;
* order context;
* order type;
* order lifecycle;
* order items;
* item-level state;
* table relationship;
* waiter attribution;
* order acceptance;
* order modification;
* cancellation;
* kitchen ticket relationship;
* price snapshots;
* inventory transaction coordination;
* paymentability;
* offline order behavior;
* synchronization boundaries.

The Order domain does not own:

* payment settlement;
* inventory stock balances;
* cash sessions;
* recipe definitions;
* employee permissions;
* report generation.

Those concerns belong to their respective domains.

---

# 2. Order as an Operational Aggregate

The Order is a primary operational aggregate.

Conceptually:

```text id="d5k3r7"
Order
├── Order UUID
├── Business
├── Branch
├── Cash Session
├── Employee
├── Device
├── Order Type
├── Table Context
├── Waiter Context
├── Items
├── Price Snapshots
├── Status
└── Operational Metadata
```

The Order aggregate must maintain internal consistency for operations that modify the order itself.

---

# 3. Order Identity

Every Order has a stable UUID.

The Order UUID is the authoritative identity of the order.

It must remain unchanged through:

* order modification;
* payment;
* waiter reassignment;
* cashier handover;
* synchronization;
* cancellation;
* refund;
* report generation.

The system does not use a separate Client Transaction ID.

---

# 4. Order Context

Every operational Order must preserve its context.

Important context includes:

```text id="e8w1k2"
Business
Branch
Employee
Device
Cash Register
Cash Session
Order Type
Table
Primary Waiter
```

Not every context field is required for every order type.

For example, Takeaway does not require a table.

---

# 5. Order Types

The current Order domain supports:

1. Hall / Dine-in
2. Takeaway

Phone Delivery is planned for a later phase.

The domain model should remain extensible enough to add future order types without changing the identity model.

---

# 6. Order Lifecycle

The operational lifecycle is:

```text id="w5f2m9"
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Served
```

There is no `Completed` state in the current model.

Payment is a separate financial lifecycle.

An Order may therefore be:

* unpaid;
* partially paid;
* fully paid;

without changing the operational status automatically.

---

# 7. Draft State

Draft represents an order being prepared before operational acceptance.

Draft:

* is editable;
* does not deduct inventory;
* does not reserve inventory;
* does not create operational table occupancy;
* does not notify the kitchen;
* does not become a finalized operational sale.

Draft recovery after device restart is not guaranteed.

---

# 8. Draft and Tables

For Dine-in orders:

```text id="j7p4n8"
Draft
  ↓
No operational occupancy
  ↓
Table remains available
```

A Draft may contain a selected table context, but the table is not considered occupied until the order becomes operational.

---

# 9. Draft Acceptance

Acceptance is the boundary between preparation and operational order processing.

When accepting an Order, the system must validate:

* employee authorization;
* Business;
* Branch;
* table state where applicable;
* product availability;
* inventory availability;
* order validity;
* current configuration.

Inventory deduction must succeed as part of the acceptance transaction.

If inventory deduction fails:

```text id="p4n8t2"
Order remains Draft
```

The Order must not become Accepted.

---

# 10. Atomic Acceptance

Order acceptance and required inventory deduction form one core transactional boundary.

Conceptually:

```text id="r6q1w4"
Accept Order
     │
     ├── Validate Order
     ├── Validate Stock
     ├── Deduct Inventory
     └── Change Order → Accepted
```

If any core operation fails, the transaction rolls back.

Kitchen notification is secondary and must not cause the core order transaction to roll back after successful acceptance.

---

# 11. Accepted State

Accepted means the Order has entered the operational workflow.

At this point:

* inventory has been deducted;
* the kitchen may receive the order;
* table occupancy becomes operational where applicable;
* payment may be recorded;
* the order becomes subject to operational status rules.

---

# 12. Order Modification

An Accepted unpaid Order may be modified according to permission.

Allowed modifications may include:

* removing an item;
* reducing quantity;
* increasing quantity;
* adding a product;
* changing permitted extras;
* applying permitted order modifications.

Each modification must preserve historical integrity.

---

# 13. Existing Item Removal

If an existing product is removed or quantity is reduced:

1. The Order total is recalculated.
2. The system asks whether inventory should be returned.
3. If the user confirms inventory return, the applicable quantity is returned.
4. If the user declines, inventory remains deducted.
5. The decision is recorded in history/audit.

The original transaction state must remain reconstructable.

---

# 14. Modification Inventory Failure

If a modification requires inventory return and the return operation fails:

```text id="n9k5x3"
Entire Modification
       ↓
Rollback
```

The system must not leave a partially modified Order.

---

# 15. Adding or Increasing Items

If a modification adds or increases a product:

* current stock is checked;
* required stock is validated atomically;
* insufficient stock rejects the entire modification;
* successful modification deducts the required inventory.

The Order must not enter an invalid partially modified state.

---

# 16. New Product After Acceptance

Adding a completely new product to an already Accepted Order creates a new operational ticket/event linked to the main Order context.

The new ticket has its own operational identity.

The main Order UUID remains unchanged.

Conceptually:

```text id="u4m7z1"
Main Order
   ├── Ticket 1
   ├── Ticket 2
   └── Ticket 3
```

This supports later additions without rewriting the original kitchen operation.

---

# 17. Price Snapshot

The Order must preserve the applicable price at the time the item becomes part of the operational order.

Later price configuration changes must not rewrite existing Order item prices.

Conceptually:

```text id="y3h8p5"
Product Current Price
       ↓
Order Item Price Snapshot
       ↓
Historical Price Preserved
```

---

# 18. Recipe and Configuration Snapshot

Where operational calculation depends on recipe or configuration state, the Order must retain sufficient snapshot information to reconstruct the transaction.

Later recipe or menu changes must not silently change historical Orders.

---

# 19. Order Items

Each Order contains one or more Order Items.

An Order Item should conceptually preserve:

* Product identity;
* quantity;
* applicable price;
* discount/adjustment information;
* extras/modifications;
* recipe/configuration reference where required;
* operational status;
* historical metadata.

Order Items must remain attributable to their parent Order.

---

# 20. Product Quantity

Quantity changes must be explicit.

The system must not silently rewrite the original quantity history.

A modification should preserve:

* previous quantity;
* new quantity;
* actor;
* timestamp;
* reason where required;
* inventory decision.

---

# 21. Order Status vs Payment Status

Operational status and financial status are separate.

Example:

```text id="b3t6q8"
Order:
Accepted

Payment:
Partially Paid
```

Another example:

```text id="m8v2d5"
Order:
Served

Payment:
Unpaid
```

The system must not infer one lifecycle solely from the other.

---

# 22. Paymentability

Payment may be initiated from the Accepted state according to payment rules.

Payment completion does not automatically change the Order operational lifecycle.

Payment belongs to the Payment domain.

The Order exposes the necessary state for the Payment domain to determine whether payment is allowed.

---

# 23. Fully Paid Orders

Once an Order is fully paid:

* ordinary editing is blocked;
* financial corrections use controlled correction mechanisms;
* refunds use the Refund domain;
* cancellation follows the defined cancellation rules.

Historical payment state remains preserved.

---

# 24. Cancellation

Cancellation is an operational state-changing action.

Cancellation requires:

* appropriate permission;
* mandatory reason;
* audit/history.

The Order is not deleted.

If inventory had previously been deducted, cancellation may require an explicit inventory-return decision according to the established business rules.

Served items must never be returned to inventory automatically.

---

# 25. Cancellation vs Refund

Cancellation and refund are separate concepts.

```text id="r8f3w2"
Cancellation
→ operational Order state

Refund
→ financial reversal
```

A cancelled Order may have no payment.

A paid Order may require a refund rather than simple cancellation.

---

# 26. Table Relationship

For Dine-in Orders, an Order may reference a Table.

The Table is not owned by the Order.

The Table belongs to the Branch.

The Order only establishes the operational relationship.

---

# 27. Table Occupancy

A Table becomes operationally Busy when at least one open/unpaid operational Order exists.

Paid Orders remain historical and do not keep the Table occupied.

Conceptually:

```text id="c6v1r9"
Open / Unpaid Order exists
        ↓
Table = Busy

No Open / Unpaid Order
        ↓
Table = Available
```

---

# 28. Table Visit Context

When a table becomes free and is later used again, a new Table Visit/Session grouping is created.

Historical Orders remain associated with the previous grouping.

This prevents unrelated visits from being merged into one operational history.

---

# 29. Multiple Orders on a Table

A Table may have multiple related open Orders.

Cashiers must be able to view all applicable Orders associated with the Table.

A customer may:

* pay one Order;
* pay multiple Orders;
* use split payment where supported.

The Order UUID remains independent.

---

# 30. Waiter Attribution

An Order may have a primary waiter.

A second waiter may temporarily assist.

The primary waiter remains unchanged unless authorized reassignment occurs.

Historical waiter attribution must remain available for reporting.

---

# 31. Cashier Attribution

The cashier creating or operating on an Order is preserved in the operational history.

After cash handover:

* the Order UUID remains unchanged;
* later operations may be performed by the new cashier;
* the original actor/session remains historically attributable.

---

# 32. Cash Session Relationship

An Order may be created and processed within a Cash Session context.

Cash handover does not move the Order to a new UUID.

Instead:

```text id="v7p4d2"
Order UUID
   ↓
Original Cash Session history
   +
Later Cash Session actions
```

This preserves operational continuity across cashier shifts.

---

# 33. Offline Draft Synchronization

Offline Drafts may synchronize because they do not create operational table occupancy or inventory deduction.

When the Draft is later accepted, the server revalidates:

* table state;
* inventory;
* product availability;
* authorization;
* configuration.

---

# 34. Offline Table Conflict

If an offline Draft references a Table that has since received an Accepted Order:

```text id="m2n9x6"
Offline Draft
     ↓
Sync
     ↓
Table already operationally occupied
     ↓
Draft discarded / conflict according to sync policy
```

The server Accepted state wins.

The Draft must not overwrite the existing operational state.

---

# 35. Offline Accepted Order

An authorized trusted device may accept an Order offline if all offline authorization and local domain requirements are satisfied.

The event retains:

* Order UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID;
* local timestamp;
* transaction identity.

The server revalidates the transaction during synchronization.

---

# 36. Offline Inventory Conflict

An offline acceptance may discover during synchronization that the server's inventory state differs from the local state.

The system must not silently overwrite stock.

The result becomes an explicit synchronization conflict or rejection according to the synchronization policy.

The original offline transaction remains identifiable.

---

# 37. Synchronization Order

Order-related synchronization must respect dependencies.

For example:

```text id="f8r2m5"
Configuration
   ↓
Order Creation
   ↓
Order Acceptance
   ↓
Inventory Transaction
   ↓
Payment
```

The exact synchronization event graph is owned by the Synchronization domain.

Order events must provide the required dependency information.

---

# 38. Idempotency

Order operations must be idempotent where retries are possible.

Repeated processing of the same Order UUID or event UUID must not create:

* duplicate Orders;
* duplicate inventory deductions;
* duplicate kitchen tickets;
* duplicate operational changes.

Lost network responses must not cause duplicate Orders.

---

# 39. Concurrent Order Creation

Two devices may attempt to create Orders concurrently.

Each Order receives a unique UUID.

If both are valid independent Orders, both may exist.

If they compete for a shared resource such as a Table state or inventory, the applicable domain concurrency rules determine which operation succeeds.

---

# 40. Concurrent Order Acceptance

Two operations may attempt to accept conflicting Orders.

The server must enforce transactional consistency.

For inventory:

```text id="q7n4c8"
Available Stock = 1

Order A requires 1
Order B requires 1

Only one acceptance succeeds.
```

The other must be rejected or become a conflict.

Negative stock is forbidden.

---

# 41. Order and Inventory Boundary

The Order domain requests inventory operations.

The Inventory domain owns stock state.

The Order domain must not directly manipulate inventory quantities outside the defined transactional interface.

This prevents duplicated inventory logic.

---

# 42. Order and Payment Boundary

The Order domain exposes order state relevant to payment.

The Payment domain owns:

* payment identity;
* payment lifecycle;
* payment method;
* payment portions;
* repayment;
* payment correction;
* refund.

The Order domain must not directly become a financial ledger.

---

# 43. Order and Kitchen Boundary

The Order domain produces operational information for the Kitchen domain.

Kitchen printing is secondary to successful Order acceptance.

If the printer fails:

* the Order remains Accepted;
* printer state records the failure;
* retry is possible;
* the Order transaction is not rolled back.

---

# 44. Order and Inventory Atomicity

For acceptance:

```text id="x3q7n1"
Order Acceptance
       +
Required Inventory Deduction
       =
One Core Transaction
```

Kitchen printing and notifications are secondary operations.

They must not break the core transactional integrity.

---

# 45. Order and Reports

Reports consume Order data.

The Order domain does not calculate report versions.

Historical Order data must be sufficient to reconstruct:

* order amount;
* items;
* quantities;
* prices;
* discounts;
* waiter;
* cashier;
* Branch;
* status history;
* relevant operational context.

---

# 46. Order History

Important changes must preserve historical state.

Examples:

* item added;
* item removed;
* quantity changed;
* price adjustment;
* waiter reassignment;
* cancellation;
* status transition;
* inventory-return decision.

History must identify:

* actor;
* timestamp;
* previous state;
* new state;
* reason where applicable;
* transaction/event UUID.

---

# 47. Domain Services

Potential Order domain services include:

```text id="v2p5k8"
Order Creation Service
Order Acceptance Service
Order Modification Service
Order Cancellation Service
Order Status Service
Table Order Context Service
Order Snapshot Service
Order Synchronization Service
```

These are logical services.

They do not imply separate microservices.

---

# 48. Domain Events

Potential Order events include:

```text id="r5m8c2"
OrderCreated
OrderAccepted
OrderModified
OrderItemAdded
OrderItemRemoved
OrderQuantityChanged
OrderCancelled
OrderStatusChanged
OrderWaiterAssigned
OrderWaiterChanged
OrderOperationalTicketCreated
```

Events represent facts.

The Order aggregate remains authoritative for its state.

---

# 49. Aggregate Boundary

The Order aggregate should remain focused.

It should not directly contain:

* Inventory;
* Payment;
* Cash Session;
* Employee;
* Recipe;
* Report;
* Notification.

References to these concepts should normally be represented by stable identifiers and controlled domain interactions.

---

# 50. Order Invariants

### Identity

1. Every Order has one stable UUID.
2. Order identity never changes.
3. Client Transaction ID is not part of the authoritative Order identity.
4. Every Order belongs to exactly one Business.
5. Every operational Order belongs to exactly one Branch.

### Lifecycle

6. Draft is fully editable.
7. Draft does not deduct inventory.
8. Draft does not create operational table occupancy.
9. Accepted requires successful core validation.
10. Accepted requires successful required inventory deduction.
11. Inventory failure prevents acceptance.
12. Operational status follows the defined lifecycle.
13. There is no Completed state in the current model.
14. Payment status is independent from operational status.

### Modification

15. Accepted unpaid Orders may be modified according to permission.
16. Insufficient stock rejects the entire required inventory modification.
17. Inventory-return failure rolls back the whole modification.
18. Price snapshots remain historically stable.
19. Existing item removal preserves the inventory-return decision.
20. Quantity reduction follows the same inventory-return policy.
21. New products added after acceptance create separate operational ticket identity.

### Tables

22. Tables belong to Branches, not Orders.
23. Draft Orders do not make tables operationally Busy.
24. Open/unpaid operational Orders make a table Busy.
25. Paid Orders do not keep tables Busy.
26. New table visits create new grouping contexts.
27. Orders from previous visits remain historical.

### Attribution

28. Original cashier attribution remains preserved.
29. Original waiter attribution remains preserved.
30. Cash handover does not change Order UUID.
31. Later actions may be attributed to a new cashier/session.

### Cancellation and Financial State

32. Cancellation does not delete an Order.
33. Cancellation requires appropriate permission.
34. Cancellation requires a reason.
35. Cancellation and refund are separate operations.
36. Paid Orders require controlled financial correction/refund rather than ordinary editing.

### Offline and Synchronization

37. Offline Orders retain stable UUIDs.
38. Offline operations preserve Business and Branch context.
39. Offline Drafts may synchronize.
40. Offline Draft acceptance requires server revalidation.
41. Server Accepted state wins over conflicting Draft state.
42. Offline authorization cannot bypass Order rules.
43. Synchronization is idempotent.

### Inventory and Kitchen

44. Order acceptance and required inventory deduction form one core transaction.
45. Kitchen printing is secondary.
46. Printer failure does not roll back a successful Order acceptance.
47. Negative stock is forbidden.
48. Inventory is owned by the Inventory domain.

### Historical Integrity

49. Historical Order state remains reconstructable.
50. Current Product configuration must not rewrite historical Orders.
51. Historical price snapshots remain unchanged.
52. Important Order changes are auditable.

### Concurrency

53. Concurrent inventory consumption is server-controlled.
54. Only one operation may consume the final available stock.
55. Duplicate network retries must not create duplicate Orders.
56. Conflicting Table operations must be resolved explicitly.
57. Server concurrency rules are authoritative.

### Security

58. Order operations require valid authentication.
59. Order operations require applicable permission.
60. Branch scope must be validated server-side.
61. Subscription entitlement must be validated where applicable.
62. Client-provided authorization state is never trusted.

---

# 51. Completion Criteria

The Order domain is considered complete when:

* Order identity is defined;
* Order lifecycle is defined;
* Draft behavior is defined;
* acceptance boundary is defined;
* inventory atomicity is defined;
* modification behavior is defined;
* cancellation is defined;
* table relationship is defined;
* waiter attribution is defined;
* cashier/session attribution is defined;
* payment boundary is defined;
* kitchen boundary is defined;
* offline behavior is defined;
* synchronization behavior is defined;
* concurrency rules are defined;
* historical integrity is defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/11_Kitchen_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

