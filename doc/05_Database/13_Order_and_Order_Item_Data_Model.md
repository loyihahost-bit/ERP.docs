# Order and Order Item Data Model

**Document ID:** DB-13
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Orders;
* Order Items;
* Order lifecycle state;
* order types;
* tables and waiter context;
* product and Set snapshots;
* order pricing snapshots;
* order modifications;
* cancellation;
* operational order relationships;
* kitchen ticket references;
* payment relationships;
* offline order identity;
* synchronization;
* historical integrity.

The model must support fast POS operations while preserving complete historical transaction information.

---

## 2. Design Principles

The Order data model follows these principles:

1. Every Order belongs to exactly one Business and Branch.
2. Every Order has a globally unique UUID.
3. Order identity is never reused.
4. Orders retain their historical context.
5. Order Items preserve historical pricing.
6. Current Product configuration must not rewrite historical Orders.
7. Draft Orders do not consume inventory.
8. Order acceptance and inventory deduction are atomic.
9. Accepted Order modifications are controlled.
10. New products added after acceptance create separate operational tickets linked to the main Order context.
11. Payment is separate from the operational Order lifecycle.
12. Cancellation is separate from refund.
13. Paid Orders cannot be ordinarily edited.
14. Historical Orders are never physically deleted during normal operation.
15. Offline Orders use UUID identity and idempotent synchronization.
16. Server state becomes authoritative after synchronization.
17. Table occupancy is based on open operational Orders.
18. Cash Session and employee context are retained.
19. Configuration snapshots preserve historical interpretation.
20. Database constraints must protect Business and Branch isolation.

---

## 3. Order Ownership

The Order belongs to a Business and Branch.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Order
   ↓
Order Items
```

Every Order must satisfy:

```text
order.business_id = branch.business_id
```

The client must not be allowed to move an Order between Businesses.

Branch transfer is not part of the current scope.

---

## 4. Order Identity

Every Order has a UUID.

Conceptual field:

```text
id UUID
```

The UUID:

* is generated before synchronization when necessary;
* remains unchanged after synchronization;
* is used for idempotency;
* is never reused;
* is the authoritative identity of the Order.

No separate Client Transaction ID is required.

---

## 5. Order Context

An Order should retain the operational context required to reconstruct its origin.

Conceptual fields:

```text id="k0t9x2"
id
business_id
branch_id
employee_id
device_id
cash_register_id
cash_session_id
order_type
table_id
primary_waiter_id
status
created_at
accepted_at
updated_at
```

Some references may be nullable depending on lifecycle state.

---

## 6. Order Types

Current supported Order Types are:

```text
DINE_IN
TAKEAWAY
```

Phone Delivery is planned for a later stage and must not be required by the current database model.

The schema may be extensible for future order types.

---

## 7. Order Status

The operational Order lifecycle is:

```text
DRAFT
   ↓
ACCEPTED
   ↓
PREPARING
   ↓
READY
   ↓
SERVED
```

`COMPLETED` is not a current Order status.

Payment state is tracked separately.

---

## 8. Draft Orders

A Draft Order represents an in-progress POS operation.

Draft characteristics:

* fully editable;
* no inventory deduction;
* no kitchen notification;
* no table occupancy;
* no payment;
* not part of operational sales totals.

Draft data may be lost after device restart.

The database must not treat a Draft as a completed business transaction.

---

## 9. Draft Persistence

A Draft may be persisted locally and/or server-side depending on the current connectivity model.

Persistence of a Draft does not make it an accepted transaction.

The database must distinguish:

```text
Draft
```

from:

```text
Accepted Transaction
```

---

## 10. Order Acceptance

Acceptance is the transition:

```text
DRAFT → ACCEPTED
```

Acceptance requires successful validation of:

* Business;
* Branch;
* employee;
* device trust where applicable;
* permission;
* subscription entitlement;
* active Product/Set;
* Branch availability;
* current configuration;
* inventory availability.

---

## 11. Acceptance and Inventory Atomicity

Order acceptance and required inventory deduction must occur in one core transaction.

Conceptually:

```text
BEGIN

Validate Order
Validate Stock
Create/Update Accepted Order
Deduct Inventory

COMMIT
```

If inventory deduction fails:

```text
Order remains non-Accepted
Inventory remains unchanged
```

There must be no state where the Order is accepted but required inventory deduction was not committed.

---

## 12. Order Number

The customer-facing Order Number is separate from the Order UUID.

The customer-facing number:

* contains three digits;
* is scoped to a Cash Session;
* resets when a new Cash Session begins.

Example:

```text
Cash Session A:
001
002
003

Cash Session B:
001
002
```

The database must use the Order UUID as the permanent identity.

---

## 13. Order Number Uniqueness

The customer-facing number should be unique within its Cash Session.

Conceptual constraint:

```text
UNIQUE (cash_session_id, order_number)
```

The UUID remains globally unique.

---

## 14. Order Employee Context

The Order must retain the employee responsible for its creation/acceptance.

At minimum, the system should preserve:

* creator;
* accepting employee where different;
* current operational actor through audit events.

The original creator must remain historically identifiable.

---

## 15. Device Context

Orders created through trusted devices should retain the originating Device UUID.

This supports:

* audit;
* offline synchronization;
* troubleshooting;
* security investigation;
* reconstruction of transaction origin.

Device references must not be used as authorization by themselves.

---

## 16. Cash Register Context

An Order created through POS should retain the Cash Register context when applicable.

The Cash Register belongs to the Branch.

The database must prevent an Order from referencing a Cash Register belonging to another Branch.

---

## 17. Cash Session Context

The Order should retain the Cash Session under which the operational transaction was accepted.

This allows reports to determine:

* which cashier session accepted the Order;
* which session generated the customer-facing Order Number;
* which operational period the transaction belongs to.

Handover does not change the Order UUID.

---

## 18. Handover Relationship

When a cashier handover occurs:

```text
Order UUID
    remains unchanged
```

The original creation/acceptance context remains historical.

Later payment or operational actions may reference the new Cash Session.

Therefore, the Order model must not assume that one Order has only one Cash Session for its entire lifecycle.

---

## 19. Table Relationship

For Dine-in Orders, an Order may reference a Table.

Conceptually:

```text
Branch
  ↓
Hall
  ↓
Table
  ↓
Order
```

The Table must belong to the same Branch.

A Takeaway Order normally has no Table.

---

## 20. Table Occupancy

A Table is considered occupied when it has an open operational Order.

Paid historical Orders do not by themselves keep a Table occupied.

Conceptually:

```text
Open Order → Table Busy
No Open Order → Table Available
```

The exact table lifecycle is defined in:

`14_Table_and_Waiter_Data_Model.md`

---

## 21. Table Visit Grouping

When a Table becomes free and a new customer begins a new visit, a new Table Visit/Session grouping may be created.

Historical Orders must remain associated with their original table context.

An Order must not be silently reassigned to a later Table Visit.

---

## 22. Waiter Relationship

A Dine-in Order may reference a Primary Waiter.

The Primary Waiter remains unchanged unless an authorized operational reassignment occurs.

A second Waiter may temporarily assist with an Order.

The second Waiter does not automatically replace the Primary Waiter.

---

## 23. Waiter Attribution

Where required, Order and Payment reports must preserve:

* Primary Waiter;
* assisting Waiter where applicable;
* cashier/accepting employee.

Historical attribution must not depend on the current employee assignment.

---

## 24. Customer Information

The current system does not maintain a full customer CRM.

For current Dine-in and Takeaway Orders, a persistent customer entity is not required.

Future Phone Delivery may store:

* phone;
* address

directly on the Order.

This document does not require a full Customer domain.

---

## 25. Order Item Model

Each Order contains zero or more Order Items while in Draft and at least one valid operational item before acceptance.

Conceptually:

```text
Order
 ├── Order Item
 ├── Order Item
 └── Order Item
```

Each Order Item represents a Product or Set selected for sale.

---

## 26. Product vs Set Item

An Order Item may reference:

* Product;
* Set.

The database must prevent an ambiguous item that references both.

Conceptually:

```text
Product Item → product_id
Set Item     → set_id
```

Exactly one sellable source must be identified.

---

## 27. Order Item Identity

Each Order Item should have its own UUID.

This supports:

* partial cancellation;
* item-level modification;
* quantity reduction;
* item-level refund;
* audit;
* synchronization;
* historical reconstruction.

The Order Item UUID must never be reused.

---

## 28. Product Snapshot

An Order Item must preserve enough information to identify what was sold at the time of transaction.

Recommended snapshot fields include:

```text id="x0t4x8"
product_id
product_name_snapshot
product_code_snapshot
category_name_snapshot
```

The current Product record may later be renamed or archived.

Historical Order display must remain understandable.

---

## 29. Set Snapshot

For a Set Order Item, the system should preserve:

```text
set_id
set_name_snapshot
set_code_snapshot
set_version_id
```

The Set Version identifies the historical composition.

---

## 30. Set Composition Snapshot

Because Set composition may change over time, a Set Order Item must retain the composition applicable to the sale.

Conceptually:

```text
Set Version
    ↓
Component Snapshot
    ↓
Order Item
```

This prevents later Set changes from rewriting historical sales interpretation.

---

## 31. Recipe Snapshot

If a Product is sold through a Recipe Version, the accepted Order Item may retain the relevant Recipe Version identity.

This is particularly important when:

* inventory was consumed through a recipe;
* recipe versions changed later;
* reports need historical reconstruction.

Recipe changes must not rewrite previous consumption history.

---

## 32. Quantity

Order Item quantity must use an exact numeric database type.

Quantity must be positive for a normal sale item.

A separate correction/return transaction must be used for negative operational effects.

Conceptually:

```text
quantity > 0
```

for ordinary Order Items.

---

## 33. Unit Price

Each Order Item stores the unit selling price applicable at the time of transaction.

Example:

```text
unit_price
quantity
```

The current Product price must never be required to calculate the historical Order total.

---

## 34. Discount Snapshot

If a discount is applied, the Order Item should preserve the applied discount information.

Possible fields:

```text
discount_amount
discount_type
discount_reference
```

The exact Discount model is defined by the Payment/Discount domain.

Historical discount data must remain stable.

---

## 35. Markup Snapshot

If custom markup is applied, the Order Item should preserve:

```text
markup_percent
markup_amount
pricing_cost_snapshot
```

This allows the system to reconstruct how the final selling price was produced.

---

## 36. Line Total

The Order Item should store a calculated line total.

Conceptually:

```text
line_total =
(quantity × unit_price)
- discount_amount
+ applicable markup adjustment
```

The exact calculation must follow the authoritative pricing rules.

The stored value provides historical stability and efficient reporting.

---

## 37. Order Total

The Order should preserve the transaction-level total.

Conceptually:

```text
order_total =
SUM(valid operational line totals)
```

The total must be calculated and persisted through controlled transaction logic.

Historical totals must not be recalculated from current Product prices.

---

## 38. Rounding

All monetary calculations must use the centrally defined database precision and application rounding policy.

The same rounding policy must be used consistently across:

* Order Items;
* Orders;
* Discounts;
* Payments;
* Refunds;
* Reports.

Floating-point arithmetic must not be used for authoritative financial values.

---

## 39. Order Modification

Accepted Orders may be modified only according to permission and state rules.

Allowed operations may include:

* removing an unpaid item;
* reducing quantity;
* adding a new product through a separate operational ticket;
* other explicitly authorized modifications.

Paid Orders cannot be ordinarily edited.

---

## 40. Removing an Accepted Item

When an existing accepted item is removed or its quantity is reduced:

1. The system determines the inventory effect.
2. The user is asked whether inventory should be returned.
3. If returned, an inventory return transaction is created.
4. If not returned, no inventory return occurs.
5. The operation is audited.

The database must preserve the original historical state and the modification chain.

---

## 41. Modification Atomicity

If an accepted Order modification requires inventory validation:

```text
Validate modification
Validate inventory
Apply Order change
Apply inventory change
Commit
```

If any required step fails, the entire modification is rejected.

Partial modification is not allowed.

---

## 42. Adding Products After Acceptance

Adding a new product after an Order has been accepted creates a separate operational Order/Order Ticket linked to the original operational context.

The new ticket has its own:

* Order UUID;
* Order Item UUIDs;
* kitchen ticket;
* inventory transaction references.

The system may group these operational records under the same table visit/bill context.

---

## 43. Main Order Context

A linked operational ticket may reference:

```text
parent_order_id
table_visit_id
business_id
branch_id
```

This allows the system to preserve one customer-facing bill context while maintaining separate operational identities.

The exact billing grouping is defined by the Payment model.

---

## 44. Payment Relationship

Payment is a separate domain.

An Order may have:

```text
0 payments
1 payment
multiple payments
```

depending on:

* partial payment;
* split bill portions;
* mixed payment;
* debt;
* corrections.

The Order model must not embed the entire Payment lifecycle.

---

## 45. Payment Status

The system should derive or store a controlled payment state such as:

```text
UNPAID
PARTIALLY_PAID
PAID
OVERPAID
```

Payment state must not replace the operational Order status.

Example:

```text
Order Status = READY
Payment Status = PAID
```

is valid.

---

## 46. Paid Order Editing

Once an Order is fully paid:

* ordinary item editing is blocked;
* price editing is blocked;
* quantity editing is blocked.

Changes require an authorized cancellation, refund, or correction flow.

Original payment and Order history remain intact.

---

## 47. Cancellation

Cancellation is a separate operation.

A cancelled Order is not physically deleted.

The system must retain:

* original Order;
* cancellation actor;
* timestamp;
* reason;
* inventory decision;
* resulting state.

---

## 48. Cancellation State

The database may represent cancellation through a controlled terminal status or separate cancellation record.

The implementation must preserve the original lifecycle history.

A cancelled Order must not be treated as a normal active sale in operational reports.

---

## 49. Cancellation Inventory

If an Order had already consumed inventory, cancellation may offer inventory return.

The return decision must be explicitly recorded.

Served items must not automatically return to inventory.

The database must preserve:

```text
inventory_return_requested
inventory_return_result
```

or an equivalent correction/transaction reference.

---

## 50. Refund Relationship

Refund is separate from Order cancellation.

A refund may be:

* full;
* partial;
* item-level;
* quantity-level.

The original Order and Payment remain historically intact.

Refund records reference the original transaction.

---

## 51. Kitchen Relationship

An accepted Order may generate a Kitchen Ticket or kitchen event.

The Order database must not depend on printer success for transaction success.

Conceptually:

```text
Order Accepted
      ↓
Kitchen Event / Ticket
      ↓
Printer
```

Printer failure is handled by the Kitchen/Printing subsystem.

---

## 52. Kitchen Ticket Identity

Kitchen Tickets should have their own identity.

An Order may produce multiple kitchen tickets due to:

* initial acceptance;
* additional products;
* controlled reprint;
* routing differences.

The Order UUID remains the parent business transaction identity.

---

## 53. Order Status History

Operational status changes should be historically traceable.

Conceptual model:

```text
OrderStatusHistory
------------------
id
order_id
from_status
to_status
actor_id
device_id
cash_session_id
reason
created_at
```

Status history is append-only.

The current Order status remains directly queryable for POS performance.

---

## 54. Order Modification History

Important Order changes should be represented through a dedicated history/correction mechanism.

Examples:

* quantity reduction;
* item removal;
* price correction;
* authorized status correction;
* cancellation.

The original Order Item state must not be silently overwritten without preserving the change history.

---

## 55. Order Configuration Snapshot

An accepted Order may retain relevant configuration references such as:

* Menu configuration version;
* Price Version;
* Branch Price Override Version;
* Recipe Version;
* Set Version.

These references provide reconstruction context.

Historical values stored directly on the transaction remain authoritative.

---

## 56. Order Database Tables

The logical model may include:

```text
orders
order_items
order_item_modifications
order_status_history
order_cancellations
order_context_links
```

Kitchen Tickets, Payments, Refunds, Inventory Transactions, and Audit Events remain separate domain tables.

---

## 57. Suggested `orders` Fields

```text id="4m8b7x"
id
business_id
branch_id
order_number
order_type
status
payment_status
employee_id
accepted_by_employee_id
device_id
cash_register_id
cash_session_id
table_id
table_visit_id
primary_waiter_id
parent_order_id
total_amount
created_at
accepted_at
served_at
updated_at
```

Additional fields may be introduced for future Delivery support.

---

## 58. Suggested `order_items` Fields

```text id="v2x5l4"
id
order_id
product_id
set_id
product_name_snapshot
product_code_snapshot
set_name_snapshot
set_code_snapshot
set_version_id
recipe_version_id
quantity
unit_price
discount_amount
discount_type
markup_percent
markup_amount
pricing_cost_snapshot
line_total
created_at
updated_at
```

Exactly one of `product_id` or `set_id` should be populated for a normal sellable item.

---

## 59. Suggested `order_status_history` Fields

```text id="y0y0s3"
id
order_id
from_status
to_status
actor_id
device_id
cash_session_id
reason
created_at
```

The history is append-only.

---

## 60. Suggested `order_item_modifications` Fields

```text id="2q0u1w"
id
order_id
order_item_id
modification_type
previous_quantity
new_quantity
previous_amount
new_amount
inventory_return_requested
inventory_return_transaction_id
actor_id
reason
created_at
```

The exact structure may be expanded for item replacement and correction workflows.

---

## 61. Suggested `order_cancellations` Fields

```text id="7o4q2m"
id
order_id
actor_id
reason
inventory_return_requested
inventory_return_transaction_id
created_at
```

The cancellation record must remain immutable after creation except through an authorized correction mechanism.

---

## 62. Database Constraints

Important constraints include:

```text
UNIQUE (cash_session_id, order_number)
```

for customer-facing numbers.

Business ownership constraints must ensure:

```text
order.business_id = branch.business_id
```

and:

```text
order_item.order_id.business_id
=
referenced Product/Set.business_id
```

Equivalent composite constraints or controlled database mechanisms may be used.

---

## 63. Item Source Constraint

An Order Item must not simultaneously reference both a Product and a Set.

Conceptually:

```text
(product_id IS NOT NULL)
XOR
(set_id IS NOT NULL)
```

A database CHECK constraint should enforce this rule.

---

## 64. Quantity Constraints

Normal Order Items must satisfy:

```text
quantity > 0
```

Negative quantities are represented through controlled refund, cancellation, or inventory correction mechanisms.

---

## 65. Monetary Constraints

Normal Order monetary values must satisfy:

```text
unit_price >= 0
discount_amount >= 0
line_total >= 0
```

Any exceptional financial adjustment must be represented through its dedicated controlled domain operation.

---

## 66. Order State Constraints

Only valid lifecycle transitions are allowed.

Examples:

```text
DRAFT → ACCEPTED
ACCEPTED → PREPARING
PREPARING → READY
READY → SERVED
```

Invalid transitions must be rejected.

The database may enforce part of the state model through constraints, while complete transition validation remains in application/domain logic.

---

## 67. Payment State Separation

Order operational state and Payment state must remain separate.

The database must allow combinations such as:

```text
ACCEPTED + UNPAID
READY + PARTIALLY_PAID
READY + PAID
SERVED + PAID
```

Payment completion must not automatically force an operational status transition.

---

## 68. Table Scope Constraint

If `table_id` is present:

```text
table.branch_id = order.branch_id
```

A Dine-in Order must not reference a Table from another Branch.

---

## 69. Waiter Scope Constraint

If a Primary Waiter is assigned:

```text
waiter.business_id = order.business_id
waiter has access to order.branch_id
```

The database and application authorization layers must enforce this.

---

## 70. Cash Session Scope Constraint

If a Cash Session is assigned:

```text
cash_session.branch_id = order.branch_id
cash_session.cash_register.branch_id = order.branch_id
```

Cross-Branch Cash Session references are invalid.

---

## 71. Device Scope Constraint

If a Device is assigned:

```text
device.business_id = order.business_id
device.branch_id = order.branch_id
```

where Branch scope applies.

Device trust itself does not authorize the Order operation.

---

## 72. Offline Order Identity

Offline-created Orders use the same Order UUID model as online Orders.

The device generates the UUID before synchronization.

After synchronization:

```text
offline_order.id == server_order.id
```

The server must not generate a second identity for the same transaction.

---

## 73. Offline Idempotency

Repeated synchronization of the same Order UUID must not create duplicate Orders.

The database must provide a unique identity boundary:

```text
UNIQUE(order.id)
```

and the synchronization layer must treat an already-known UUID as an idempotent retry.

---

## 74. Offline Validation

When an offline Order is synchronized, the server validates:

* Business;
* Branch;
* employee;
* device;
* offline authorization;
* permission;
* subscription;
* configuration;
* Product/Set availability;
* price;
* inventory;
* state transition.

Invalid Orders must not silently become accepted transactions.

---

## 75. Offline Stock Conflict

If an offline Order consumed stock that was also consumed elsewhere, synchronization may discover a stock conflict.

The Order must not silently overwrite server inventory.

The system creates an explicit conflict record or rejects the operation according to synchronization rules.

Conflict resolution is permission-controlled and audited.

---

## 76. Configuration Conflict

If an offline Order was created using an older configuration, the server determines whether that configuration was valid for the transaction.

The server must not blindly replace the historical price or Product configuration.

If invalid, synchronization produces an explicit conflict or rejection.

---

## 77. Draft Synchronization

Draft synchronization is not equivalent to transaction synchronization.

Draft data may be treated as temporary state.

An accepted transaction requires full server validation and idempotent synchronization.

---

## 78. Concurrent Order Acceptance

If multiple devices attempt to create competing accepted Orders against the same final inventory quantity:

```text
First successful transaction
        ↓
Consumes available stock

Later transaction
        ↓
Stock validation fails
```

The database must serialize the relevant inventory state.

---

## 79. Concurrent Order Modification

Two employees must not silently overwrite the same Order modification.

Optimistic versioning or equivalent concurrency control should be used.

Example:

```text
Order Version 5
       ↓
Employee A reads Version 5
Employee B updates → Version 6
Employee A updates Version 5
       ↓
Rejected as stale
```

---

## 80. Order Version

The `orders` table should include an optimistic concurrency version where required.

Conceptually:

```text
version BIGINT
```

The version increments on controlled state changes.

The version is not a replacement for Order UUID.

---

## 81. Historical Integrity

The following must remain historically reconstructable:

* Order identity;
* Order type;
* Branch;
* creator;
* accepting employee;
* Device;
* Cash Session context;
* Table;
* Waiter;
* Product/Set identity;
* Product/Set name snapshot;
* quantity;
* price;
* discount;
* markup;
* line total;
* Order total;
* status history;
* cancellation;
* modification history.

---

## 82. Reporting

Reports may use the Order model for:

* sales;
* order count;
* product performance;
* Set performance;
* cashier performance;
* waiter performance;
* branch performance;
* status analysis;
* cancellation;
* payment reconciliation.

Reports must use historical Order values rather than current Product configuration.

---

## 83. Audit Relationship

Important Order events must create audit records.

Examples:

* Order accepted;
* Order status changed;
* item removed;
* quantity reduced;
* inventory return selected;
* cancellation;
* payment-related correction;
* manual correction;
* conflict resolution.

Audit data is separate from Order operational state.

---

## 84. Data Lifecycle

During subscription expiry:

* existing Orders remain readable;
* historical Orders remain available;
* new modifying transactions may be blocked;
* allowed reports remain available;
* permitted Excel exports remain available.

During Business deletion:

* Orders are removed only through the controlled Business deletion lifecycle;
* dependent records are processed in dependency order;
* deletion is idempotent;
* deleted UUIDs are never reused.

---

## 85. Indexing Strategy

Important indexes include:

```text
orders(business_id, branch_id, created_at)
orders(branch_id, status)
orders(cash_session_id, order_number)
orders(table_id, status)
orders(primary_waiter_id, created_at)
orders(employee_id, created_at)
orders(device_id, created_at)

order_items(order_id)
order_items(product_id, created_at)
order_items(set_id, created_at)

order_status_history(order_id, created_at)
order_item_modifications(order_id, created_at)
```

Indexes should support POS and reporting queries without excessive write overhead.

---

## 86. POS Query Requirements

Common POS queries must efficiently support:

* active Orders;
* current Table Orders;
* Order Items;
* unpaid Orders;
* current Order status;
* current payment state;
* Cash Session Orders;
* cashier Orders;
* waiter Orders.

Historical reporting queries should not require scanning unrelated Business data.

---

## 87. Soft Deletion

Normal Order deletion is prohibited.

Historical Orders remain available through lifecycle rules.

If technical deletion is required during Business deletion, it must occur through the controlled data lifecycle process.

---

## 88. Cache

Current active Order state may be cached for read performance where useful.

Cache is never authoritative.

Database state remains authoritative for:

* Order acceptance;
* inventory;
* payment;
* cancellation;
* synchronization.

---

## 89. Transaction Boundary

The following are core transactional operations:

### Accept Order

```text
Validate Order
Validate Stock
Persist Accepted State
Persist Inventory Consumption
Commit
```

### Modify Accepted Order

```text
Validate Permission
Validate Current Version
Validate Stock/Return
Persist Order Modification
Persist Inventory Effect
Commit
```

### Cancel Order

```text
Validate Permission
Persist Cancellation
Persist Inventory Return if selected
Commit
```

Kitchen notification and printing are secondary processing.

---

## 90. Failure Handling

If database transaction fails:

```text
No partial Order acceptance
No partial inventory deduction
```

If kitchen printing fails:

```text
Order remains accepted
Print state becomes Failed/Pending/Retrying
```

If payment creation fails:

```text
Order remains in its previous operational state
```

If synchronization response is lost:

```text
Retry using same Order UUID
```

The server must process the retry idempotently.

---

## 91. Security Requirements

The Order database model must support:

* tenant isolation;
* Branch isolation;
* employee attribution;
* device attribution;
* Cash Session attribution;
* permission checks;
* subscription entitlement;
* offline authorization;
* audit;
* synchronization validation.

The client must never be trusted to determine authoritative Business or Branch ownership.

---

## 92. Performance Requirements

Orders are among the highest-frequency operational entities.

Therefore:

* current Order state must be directly queryable;
* historical status must be append-only;
* current status must not require scanning history;
* Order Item reads must be indexed;
* UUID lookup must be efficient;
* POS transactions must use short database transactions;
* reporting must not block normal POS operations;
* heavy historical queries should run through appropriate background/reporting paths.

---

## 93. Cross-Domain Relationships

### Product

Defines sellable Product identity.

### Set

Defines fixed product combinations.

### Recipe

Defines production and inventory consumption.

### Inventory

Provides stock validation and consumption.

### Menu and Pricing

Provides current configuration and price.

### Cash

Provides Register and Session context.

### Payment

Tracks financial settlement separately.

### Table

Provides Dine-in occupancy context.

### Waiter

Provides staff attribution.

### Kitchen

Receives operational preparation events.

### Audit

Records important Order changes.

### Synchronization

Transfers offline transactions.

### Subscription

Controls whether modifying operations are permitted.

### Reports

Reads historical Order data for reporting.

---

## 94. Database Invariants

The following invariants are mandatory:

1. Every Order belongs to exactly one Business.
2. Every Order belongs to exactly one Branch.
3. Branch and Business ownership must match.
4. Every Order UUID is globally unique.
5. Order UUIDs are never reused.
6. Customer-facing Order Numbers are unique within a Cash Session.
7. Order Numbers reset across Cash Sessions.
8. Order Number is not the permanent transaction identity.
9. Supported current Order Types are Dine-in and Takeaway.
10. Draft Orders do not consume inventory.
11. Draft Orders do not trigger kitchen processing.
12. Draft Orders do not create payment obligations.
13. Order acceptance requires authorization.
14. Order acceptance validates current configuration.
15. Order acceptance validates inventory.
16. Order acceptance and inventory deduction are atomic.
17. Failed inventory deduction prevents acceptance.
18. Order Items have unique UUIDs.
19. Order Item UUIDs are never reused.
20. Each normal Order Item references exactly one Product or Set.
21. Product and Set belong to the same Business as the Order.
22. Order Item quantity is positive.
23. Negative operational quantities are not stored as normal sale items.
24. Order Item unit price cannot be negative.
25. Order Item historical price is immutable.
26. Current Product price cannot rewrite historical Order Item price.
27. Product name changes cannot rewrite historical Order snapshots.
28. Set composition changes cannot rewrite historical Set snapshots.
29. Recipe changes cannot rewrite historical Recipe references.
30. Discount history remains preserved.
31. Markup history remains preserved.
32. Line totals are stored using authoritative monetary calculations.
33. Order totals are historically stable.
34. Payment state is separate from Order operational state.
35. Payment completion does not automatically change operational status.
36. Paid Orders cannot be ordinarily edited.
37. Paid Order changes require controlled correction/refund/cancellation flows.
38. Cancellation is not physical deletion.
39. Cancellation requires authorization.
40. Cancellation requires a reason.
41. Inventory return during cancellation is explicit.
42. Refund does not automatically return inventory.
43. Existing accepted item removal uses controlled inventory return logic.
44. Accepted Order modifications requiring inventory changes are atomic.
45. Failed Order modification rolls back all required changes.
46. Adding a Product after acceptance creates a separate operational ticket.
47. Linked operational tickets retain their own identities.
48. Linked tickets may share Table Visit/Bill context.
49. Order UUID remains stable across cashier handover.
50. Cash Session history is never silently rewritten.
51. Table references must belong to the same Branch.
52. Waiter references must belong to the same Business.
53. Assigned Waiter must have access to the Order Branch.
54. Cash Register must belong to the Order Branch.
55. Cash Session must belong to the Order Branch.
56. Device must belong to the correct Business and Branch scope.
57. Trusted Device does not replace permission checks.
58. Offline Orders use the same UUID model as online Orders.
59. Repeated synchronization of an Order UUID is idempotent.
60. Synchronization must not create duplicate Orders.
61. Offline configuration must be validated on the server.
62. Offline stock conflicts must be explicit.
63. Offline price/configuration conflicts must be explicit.
64. Synchronization must not silently overwrite server state.
65. Server state is authoritative after synchronization.
66. Concurrent stock consumption must be serialized.
67. Concurrent Order modifications cannot silently overwrite each other.
68. Optimistic concurrency versions must reject stale updates.
69. Order status transitions must be valid.
70. Invalid status transitions must be rejected.
71. Current Order status must be directly queryable.
72. Status history is append-only.
73. Important modifications are historically traceable.
74. Order cancellation history is immutable.
75. Historical actor identity must remain available.
76. Historical Device identity must remain available.
77. Historical Cash Session context must remain available.
78. Historical Table/Waiter context must remain reconstructable.
79. Reports must use historical Order values.
80. Current Product pricing must not determine historical reports.
81. Cache must never be the authoritative Order state.
82. Database transaction failure must not leave partial acceptance.
83. Kitchen printer failure must not roll back an accepted Order.
84. Lost synchronization response must be safely retryable.
85. Business isolation must apply to every Order query.
86. Branch isolation must apply to every operational Order query.
87. Subscription expiry must not delete Orders.
88. Subscription downgrade must not delete historical Orders.
89. Business deletion must follow the controlled lifecycle.
90. Deletion operations must be idempotent.
91. Deleted Business data must not become accessible through stale devices.
92. Deleted UUIDs must never be reused.
93. Order history must remain immutable under ordinary operations.
94. Audit records must remain separate from operational Order state.
95. Order and inventory core operations must use short atomic transactions.
96. Heavy reporting queries must not block normal POS operations.
97. Historical Order data must remain available for required retention.
98. Database constraints and application validation must enforce the same ownership boundaries.
99. No Client Transaction ID is required as a second authoritative identity.
100. Order UUID is the permanent identity of the transaction.

---

## 95. Related Documents

### Database

* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `08_Product_and_Category_Data_Model.md`
* `09_Recipe_and_Recipe_Version_Data_Model.md`
* `10_Set_and_Set_Version_Data_Model.md`
* `11_Inventory_and_Warehouse_Data_Model.md`
* `12_Menu_and_Pricing_Data_Model.md`
* `14_Table_and_Waiter_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`

### Domain

* `06_Order_Domain.md`
* `07_Cash_Domain.md`
* `09_Payment_Domain.md`
* `10_Menu_and_Pricing_Domain.md`
* `11_Kitchen_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `07_POS_and_Order_System.md`
* `08_Order_Lifecycle_and_Statuses.md`
* `09_Table_and_Waiter_Management.md`
* `10_Kitchen_and_Printing.md`
* `11_Payment_System.md`
* `27_System_Wide_Consistency_and_Concurrency.md`

### Architecture

* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 96. Final Rule

The Order database model must make POS operations fast while preserving complete historical transaction integrity.

The central rule is:

```text
Order identity is permanent.
Order history is immutable.
Current configuration may change.
Historical transaction values must not change.
```

Order acceptance, inventory consumption, payment, cancellation, refund, kitchen processing, synchronization, and reporting must remain explicitly connected but independently controlled database concerns.

