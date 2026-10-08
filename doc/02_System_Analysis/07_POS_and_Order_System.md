# POS and Order System

**Document ID:** SA-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior of the Point of Sale (POS) and Order system.

It establishes:

* POS operational context;
* Order identity;
* order creation;
* order types;
* Draft behavior;
* order acceptance;
* order context;
* table and waiter relationships;
* inventory interaction;
* order modification;
* order cancellation;
* order status boundaries;
* payment separation;
* offline order behavior;
* idempotency;
* concurrency;
* historical integrity.

The objective is to keep POS operations fast and simple while maintaining strict business correctness, inventory integrity and historical traceability.

---

## 2. POS Context

The POS operates within a specific:

* Business;
* Branch;
* Employee;
* Device;
* Cash Register;
* Cash Session where applicable.

Conceptually:

```text id="q7b5w3"
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Session
   ↓
Employee + Device
   ↓
POS
   ↓
Order
```

The POS must never operate outside a valid Business and Branch context.

---

## 3. Order Identity

Every Order has a unique Order UUID.

The Order UUID is the permanent identity of the order.

It is used for:

* order retrieval;
* synchronization;
* payment references;
* inventory references;
* audit;
* corrections;
* reporting;
* idempotency.

The Order UUID must remain unchanged throughout the order lifecycle.

---

## 4. Customer-Facing Order Number

The system also generates a customer-facing order number.

The customer-facing number is a short operational identifier intended for:

* kitchen;
* customer communication;
* order pickup;
* POS display.

The current format is a **3-digit number**.

The number resets when a new Cash Session is opened.

Therefore:

```text id="0j3y8s"
Cash Session A
→ 001
→ 002
→ 003

Cash Session B
→ 001
→ 002
```

The 3-digit number is not the permanent Order identity.

The database continues to use Order UUID.

---

## 5. Order Context

Every order must retain sufficient operational context.

The order context includes:

* Order UUID;
* Business UUID;
* Branch UUID;
* Employee UUID of creator;
* Device UUID;
* Cash Register UUID where applicable;
* Cash Session UUID where applicable;
* Order Type;
* Table context where applicable;
* Primary Waiter where applicable;
* creation timestamp;
* current lifecycle status.

Historical context must not be reconstructed only from current employee or Branch assignments.

---

## 6. Supported Order Types

The current operational system supports:

1. Hall / Dine-in;
2. Takeaway.

Phone Delivery is a future planned order type.

The system architecture must not prevent future addition of additional order types.

---

## 7. Hall / Dine-in Orders

A Hall order may be associated with:

* Branch;
* Hall;
* Table;
* Table Visit/Session;
* Primary Waiter.

The table context represents the operational location of the order.

A Hall order may remain open while the table is occupied.

---

## 8. Takeaway Orders

A Takeaway order does not require a table.

It retains:

* Business;
* Branch;
* employee;
* device;
* cash session where applicable;
* order type;
* products;
* payment context.

Takeaway orders do not create table occupancy.

---

## 9. Customer Information

The current system does not maintain a separate permanent customer database.

For supported order scenarios, customer information may be stored directly with the order.

Where needed, this may include:

* customer name;
* phone number;
* delivery address for future delivery functionality.

Such information belongs to the historical order context and must not be treated as a reusable customer master record unless a future CRM requirement is introduced.

---

## 10. Order Creation

A new order starts as a Draft.

The cashier is the current primary order-creation user.

The system validates the initial context before creating the Draft.

Required context includes:

* authenticated employee;
* Business;
* Branch;
* Device;
* valid POS access;
* order type;
* table context when required.

---

## 11. Draft State

Draft is a temporary order state.

A Draft may contain:

* products;
* quantities;
* extras;
* removals;
* order type;
* table context;
* waiter context;
* customer information where applicable;
* pricing snapshot information.

Draft behavior is intentionally lightweight.

---

## 12. Draft Editing

While an order remains Draft:

* products may be added;
* products may be removed;
* quantities may be changed;
* extras may be changed;
* applicable pricing may be recalculated.

The cashier may freely modify the Draft within the available permissions.

No operational inventory deduction is performed at Draft stage.

---

## 13. Draft and Inventory

Draft creation does not consume inventory.

Draft does not reserve inventory.

Therefore:

```text id="4qz8m1"
Draft
   ↓
No Inventory Deduction
   ↓
No Inventory Reservation
```

Inventory validation becomes authoritative when the order is accepted.

---

## 14. Draft and Table Occupancy

Creating a Draft does not make a table operationally busy.

A table becomes Busy when an appropriate accepted/open order exists according to the table rules.

Therefore:

```text id="e0y1c7"
Draft
   ↓
Table remains Available
```

This prevents abandoned drafts from permanently occupying tables.

---

## 15. Draft Persistence

Drafts may be autosaved during normal use.

However, Draft recovery after device restart is not a mandatory business guarantee.

If a device restarts unexpectedly, an unsynchronized Draft may be lost.

Draft loss must not create:

* inventory movement;
* payment;
* table occupancy;
* financial transaction.

---

## 16. Draft Acceptance

Accepting a Draft is the transition from temporary preparation to an operational order.

The system must validate:

1. Employee status;
2. Business context;
3. Branch context;
4. permission;
5. current product/menu state;
6. product availability;
7. inventory availability;
8. table state where applicable;
9. current order state;
10. subscription/entitlement where applicable.

---

## 17. Acceptance Transaction

Order acceptance and inventory deduction form one core atomic transaction.

Conceptually:

```text id="pl8yqv"
Accept Order
     ↓
Validate Order
     ↓
Validate Stock
     ↓
Deduct Inventory
     ↓
Persist Accepted Order
     ↓
Commit
```

If any core operation fails:

```text id="qz1n5c"
Transaction Failure
      ↓
Rollback
      ↓
Order remains not Accepted
      ↓
Inventory remains unchanged
```

---

## 18. Inventory Insufficiency

If required inventory is insufficient when accepting an order:

* the order is not accepted;
* inventory is not partially deducted;
* the user receives a business-level error;
* the Draft remains available for correction where possible.

The system must not create negative stock.

---

## 19. Concurrent Stock Consumption

When multiple operations attempt to consume the same limited stock:

* the server performs authoritative stock validation;
* critical inventory operations use appropriate transaction isolation/locking;
* only valid transactions succeed.

Example:

```text id="3b3j9e"
Stock = 1

Order A → attempts 1
Order B → attempts 1

Only one operation succeeds.
```

The second operation receives an appropriate business conflict/stock error.

---

## 20. Acceptance and Kitchen Notification

After successful order acceptance, the system may create the relevant kitchen operation/print event.

Kitchen printing is secondary to the core ERP transaction.

Therefore:

```text id="9q9l4f"
Order + Inventory
       ↓
Core Transaction
       ↓
Commit
       ↓
Kitchen Event
       ↓
Print / Retry
```

A kitchen printer failure must not roll back a successfully accepted order.

---

## 21. Order Lifecycle

The operational order lifecycle is:

```text id="l4p1fw"
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

There is no `Completed` operational order state.

Payment is a separate financial lifecycle and does not automatically change the operational order state.

---

## 22. Accepted State

Accepted means:

* order is operationally valid;
* inventory deduction succeeded;
* order is available to downstream operational processes;
* kitchen processing may begin.

An Accepted order may remain unpaid.

---

## 23. Preparing State

Preparing indicates that kitchen processing has started.

The exact transition may be controlled by kitchen workflow.

The system must preserve the actor/source responsible for status changes where applicable.

---

## 24. Ready State

Ready indicates that the order is prepared and available for the next operational step.

The status does not automatically imply:

* payment;
* customer pickup;
* Served state.

---

## 25. Served State

Served indicates that the operational serving process is complete.

Once an order reaches Served, previously deducted inventory remains consumed.

Served items must never be automatically returned to inventory through ordinary status changes.

Any financial correction is handled separately.

---

## 26. Payment Independence

Payment is independent from the operational order lifecycle.

Payment may be accepted from an operationally payable order state according to payment rules.

Payment does not automatically:

* mark an order Ready;
* mark an order Served;
* change the kitchen status;
* close the operational lifecycle.

Conceptually:

```text id="w4g2h1"
Order Lifecycle
Draft → Accepted → Preparing → Ready → Served

Payment Lifecycle
Pending → Completed
```

These lifecycles may progress independently.

---

## 27. Order Modification Before Payment

An unpaid Accepted order may be modified according to the order modification rules.

Permitted operations may include:

* remove existing product;
* reduce quantity;
* add permitted product;
* change permitted extras.

All modifications are subject to:

* current permission;
* current inventory;
* current order state;
* audit requirements.

---

## 28. Product Removal From Accepted Order

When an existing product is removed from an unpaid Accepted order:

1. the removed product value is deducted from the order total;
2. the system asks whether inventory should be returned;
3. if inventory return is confirmed, the inventory return is performed;
4. if inventory return is rejected, no return is performed;
5. the modification is audited.

The system must preserve the decision.

---

## 29. Quantity Reduction

Quantity reduction follows the same principle as product removal.

Example:

```text id="5e7s2a"
Original:
Product A × 3

New:
Product A × 2

Difference:
1 unit removed
```

The system asks whether the corresponding inventory should be returned.

The order and inventory modification must remain consistent.

---

## 30. Inventory Return Failure During Modification

If a modification requires inventory return and the inventory transaction fails:

```text id="6j7r3q"
Order Modification
       ↓
Inventory Return
       ↓
Failure
       ↓
Rollback Entire Modification
```

The order must not be left in a partially modified state.

---

## 31. Product Increase or Addition

Adding or increasing a product in an Accepted order requires a new inventory availability check.

If sufficient stock exists:

* modification may proceed;
* required inventory is deducted;
* order total is recalculated.

If stock is insufficient:

* the entire modification is rejected;
* no partial quantity is accepted;
* no partial inventory deduction occurs.

---

## 32. New Product After Acceptance

A new product added after the original order has been Accepted is treated as a new operational order/ticket.

It has:

* its own Order UUID;
* its own operational identity;
* its own kitchen ticket;
* its own lifecycle;
* its own inventory transaction.

It remains linked to the original order/table context where applicable.

Conceptually:

```text id="7k0v2q"
Main Order
    │
    ├── Additional Order A
    └── Additional Order B
```

The exact grouping mechanism is handled by the Table and Order system.

---

## 33. Order Grouping

Related orders may belong to the same operational Table Visit/Session.

Grouping allows the system to identify:

* orders for the same table visit;
* related open orders;
* payment context;
* waiter context.

Grouping does not merge the individual Order UUIDs.

Each order retains its own identity and history.

---

## 34. Table Occupancy

For Hall orders, a table is considered Busy when at least one open/unpaid operational order exists according to the table rules.

Paid historical orders may remain visible without keeping the table Busy.

When the table is freed, the previous grouping ends.

A later visit creates a new Table Visit/Session.

---

## 35. Waiter Context

A Hall order may have a Primary Waiter.

The Primary Waiter remains associated with the order unless explicitly changed through an authorized operation.

A second waiter may temporarily assist.

The Primary Waiter may assign temporary assistance when permitted.

The system preserves waiter attribution for reporting and relevant overpayment attribution.

---

## 36. Order Visibility

An authorized cashier may view orders associated with a table, including paid historical orders where the interface permits historical access.

Visibility remains subject to:

* Business;
* Branch;
* permission;
* order scope.

A user must not access another Branch's orders through table context.

---

## 37. Order Cancellation

Cancellation is a controlled operational action.

It requires:

* appropriate permission;
* mandatory reason;
* audit record.

Cancellation does not delete the order.

The order remains historically identifiable.

---

## 38. Cancellation and Inventory

If inventory was previously deducted:

* the system may offer Return Inventory according to cancellation rules;
* the inventory return decision is recorded;
* served items must never be returned through cancellation.

Cancellation and inventory return remain explicitly linked but independently auditable.

---

## 39. Cancellation and Refund

Cancellation and refund are separate operations.

```text id="f7p2g6"
Cancellation
→ Operational Order State

Refund
→ Financial Operation
```

Cancelling an order does not automatically mean that a payment has been refunded.

Where both are required, they are separate controlled operations.

---

## 40. Paid Order Modification

A fully paid order cannot be modified through the normal order-edit workflow.

Required changes must use an appropriate:

* cancellation;
* refund;
* correction;
* other authorized financial/operational process.

The original paid transaction remains historically preserved.

---

## 41. Order Price Snapshot

Order pricing must preserve the price applicable at the time of the relevant order transaction.

Later changes to:

* global price;
* Branch override price;
* recipe;
* menu configuration

must not rewrite historical order pricing.

Open orders use the appropriate consistent pricing snapshot.

---

## 42. Discount Handling

Discounts affect the transaction total.

They do not rewrite the base product price.

Discounts require appropriate permission and are recorded separately from the standard product price.

---

## 43. Custom Order Markup

Where the system supports custom order markup, the markup is applied to the relevant cost basis according to the defined business rule.

The current rule is:

```text id="v8m7z2"
Final Price = Cost × (1 + Markup / 100)
```

Markup must remain within the permitted `0–100%` range.

The cost basis uses Last Purchase Cost.

Custom markup does not rewrite the global product price.

---

## 44. Set Products

A Set is treated as a separate sellable product/bundle.

A Set has:

* its own Order line identity;
* its own selling price;
* stable component composition.

When sold, inventory is deducted according to the Set's components.

Component substitution is not permitted during normal sale.

---

## 45. Set Configuration Changes

Changing Set composition does not silently modify existing order lines.

A Set configuration change creates a new configuration/version.

The new configuration becomes effective according to the configuration timing rule.

The current rule is:

> Recipe, menu and Set configuration changes become effective from the next Cash Session.

Existing order snapshots remain unchanged.

---

## 46. Inactive Products

An inactive product cannot be selected for a new sale through normal POS operation.

Historical order lines containing the product remain preserved.

The system must distinguish:

* product currently active;
* product currently inactive;
* historical product usage.

---

## 47. Equipment-Broken Products

A product may be temporarily unavailable because required equipment is broken.

This state is operationally distinct from permanent product inactivity.

When marked unavailable because of equipment:

* new sales are blocked;
* historical data remains unchanged;
* restoration of availability is controlled by authorized users.

---

## 48. Order and Inventory Atomicity

For accepted orders, the core relationship is:

```text id="9h7j2m"
Order Acceptance
      +
Inventory Deduction
      =
One Atomic Core Transaction
```

This guarantees that the system cannot persist an accepted order while silently failing to deduct the required inventory.

---

## 49. Order and Secondary Services

Secondary services may include:

* kitchen printing;
* notifications;
* analytics updates;
* background processing.

Failure of these services must not roll back a successfully committed core order transaction.

Their state is tracked separately.

---

## 50. Offline Orders

Offline order operations are allowed only on trusted devices with valid offline authorization.

Offline orders retain:

* Order UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID where applicable;
* local timestamps;
* transaction UUID.

The event is later synchronized to the server.

---

## 51. Offline Order Acceptance

Offline order acceptance performs local validation within the available authorized state.

The device must enforce:

* employee authorization;
* Branch scope;
* offline entitlement;
* product/menu configuration;
* local inventory state;
* order rules.

After synchronization, the server performs authoritative validation.

---

## 52. Offline Stock Conflict

If an offline order consumed inventory that is no longer available according to authoritative server state:

* the event is not silently discarded;
* a synchronization conflict is created;
* the original event remains preserved;
* an authorized user resolves the conflict;
* the resolution is audited.

The system prioritizes historical integrity and explicit conflict resolution over silent last-write-wins behavior.

---

## 53. Offline Table Conflict

A Draft created offline does not occupy a table.

When that Draft later attempts acceptance during synchronization:

* the server rechecks current table state;
* if the table is still valid, the order may be accepted;
* if another Accepted order now occupies the table context, the offline Draft is discarded from operational acceptance;
* the server Accepted state wins.

The discarded Draft must not create inventory or payment effects.

---

## 54. Synchronization Idempotency

Order synchronization uses UUID-based identity.

If the same order/event is submitted more than once:

```text id="d3c0xq"
Same UUID
    ↓
Existing Result
    ↓
Return Existing Result
```

The system must not:

* create a duplicate order;
* deduct inventory twice;
* create duplicate payment effects;
* create duplicate operational events.

---

## 55. Order Concurrency

Concurrent operations on the same order must be controlled.

Examples:

* two modifications;
* modification and payment;
* cancellation and payment;
* acceptance and cancellation;
* status changes.

The system must use appropriate transaction and version/concurrency rules.

A stale client must not silently overwrite a newer authoritative state.

---

## 56. Order and Payment Concurrency

If a payment is being processed while another operation changes the order:

* the server determines whether the payment remains valid;
* remaining payable amount is checked;
* conflicting operations are rejected or resolved explicitly;
* duplicate financial effects are prevented.

A fully paid order must not accept ordinary additional payment beyond the defined overpayment rules.

---

## 57. Overpayment

If the final accepted payment amount is greater than the remaining order amount, the system records the excess as an Overpayment.

The excess is not treated as:

* customer debt;
* unpaid order balance;
* cashier personal income.

It belongs to the Business/Branch as additional income according to the defined business rule.

The overpayment record preserves:

* original order amount;
* accepted/entered amount;
* overpayment amount;
* payment method;
* confirmation status;
* date/time;
* cashier;
* waiter where applicable;
* relevant UUIDs/context;
* reason/comment where required.

---

## 58. POS and Overpayment Confirmation

When the cashier enters an amount greater than the order amount:

1. the system calculates the excess;
2. the system asks for confirmation;
3. the cashier confirms or rejects the overpayment;
4. only after confirmation is the excess recorded as overpayment.

The system must not silently convert an accidental excess amount into additional income.

---

## 59. Order Historical Integrity

The system must preserve original order information.

Corrections and modifications are represented through controlled state changes and audit history.

Historical information must remain sufficient to determine:

* original order;
* original creator;
* original Branch;
* original pricing;
* original inventory effects;
* subsequent modifications;
* financial operations.

---

## 60. POS Performance

POS is a primary performance-sensitive area.

Normal operations should remain fast on ordinary POS/office hardware.

The system should avoid blocking POS for:

* report generation;
* notification delivery;
* synchronization;
* kitchen printer retries;
* heavy background work.

Critical order and inventory transactions remain synchronous and authoritative where required.

---

## 61. POS Error Behavior

User-facing POS errors must be concise and business-safe.

Examples:

```text id="y6z0ae"
Insufficient stock.

This order cannot be accepted until the required quantity is available.
```

Technical details belong in logs rather than normal cashier-facing messages.

---

## 62. POS Recovery

If a core transaction fails:

* the transaction is rolled back;
* no partial order state is committed;
* inventory remains consistent;
* the user may retry when appropriate.

If a secondary service fails:

* the core order remains committed;
* the secondary event becomes Pending/Failed/Retrying as appropriate;
* background processing handles recovery.

---

## 63. System Invariants

The following invariants apply to the POS and Order system:

1. Every Order has a permanent Order UUID.
2. The customer-facing 3-digit order number is not the permanent Order identity.
3. The 3-digit order number resets per Cash Session.
4. Every operational order belongs to exactly one Business.
5. Every operational order belongs to exactly one Branch.
6. Every order preserves its original operational context.
7. Current supported order types are Hall/Dine-in and Takeaway.
8. Phone Delivery is outside the current operational scope.
9. Cashier is the primary order-creation user.
10. Draft creation does not deduct inventory.
11. Draft creation does not reserve inventory.
12. Draft creation does not make a table operationally Busy.
13. Draft recovery after device restart is not guaranteed.
14. Order acceptance requires authoritative inventory validation.
15. Order acceptance and inventory deduction form one atomic core transaction.
16. Negative stock is prohibited.
17. Concurrent stock consumption is handled server-side.
18. Kitchen printing is secondary to the core ERP transaction.
19. Kitchen failure does not roll back a committed order.
20. The operational lifecycle is Draft → Accepted → Preparing → Ready → Served.
21. There is no Completed operational state.
22. Payment has an independent financial lifecycle.
23. Payment does not automatically change operational order status.
24. Unpaid Accepted orders may be modified according to permission and business rules.
25. Removing/reducing accepted items requires an explicit inventory-return decision.
26. Failed inventory return rolls back the entire modification.
27. Insufficient stock for an increase rejects the entire modification.
28. New products added after acceptance are separate operational orders/tickets linked to the main context.
29. Related orders may share a Table Visit/Session without sharing Order UUID.
30. At least one open/unpaid order keeps the table Busy according to table rules.
31. Paid historical orders do not automatically keep the table Busy.
32. Primary waiter attribution is preserved unless explicitly changed.
33. Paid orders cannot be ordinarily edited.
34. Cancellation and refund are separate operations.
35. Cancellation does not delete the original order.
36. Served items are never returned to inventory through ordinary status changes.
37. Historical order pricing is immutable through later menu/price changes.
38. Discounts do not modify the base product price.
39. Set products use stable component composition.
40. Set configuration changes do not rewrite existing orders.
41. Inactive products cannot be sold through normal POS operation.
42. Equipment-broken availability is distinct from product inactivity.
43. Offline operations require trusted device authorization.
44. Offline orders preserve their original UUID and operational context.
45. Server validation remains authoritative after synchronization.
46. Offline conflicts are explicit and never silently overwritten.
47. Duplicate order events are prevented through UUID-based idempotency.
48. Concurrent order operations cannot silently overwrite newer state.
49. Overpayment is a separate Business/Branch financial record.
50. Overpayment is not cashier personal income.
51. Overpayment requires confirmation when entered amount exceeds the order amount.
52. Core POS transactions are prioritized for correctness and performance.
53. Secondary services must not unnecessarily block POS.
54. Technical failures must not result in silent partial business transactions.
55. Historical order context remains preserved after employee, Branch, price or configuration changes.

---

## 64. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 65. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `07_POS_and_Order_System.md`

**Next Document:** `08_Order_Lifecycle_and_Statuses.md`

