# API POS and Order Endpoints

**Document ID:** API-13
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the API contract architecture for POS and Order operations in FastFood ERP.

The purpose is to provide stable and explicit API contracts for:

* POS order creation;
* Order item management;
* Dine-in Orders;
* Takeaway Orders;
* Phone Delivery Orders;
* table and hall context;
* Order acceptance;
* Order cancellation;
* Order modification;
* Order status management;
* per-item status visibility;
* pricing snapshots;
* Recipe and inventory validation;
* discount application;
* custom Order pricing operations;
* Cash Session association;
* offline POS operation;
* synchronization compatibility;
* kitchen/printing side effects;
* historical integrity.

This document defines **what POS and Order APIs expose**.

Generic API principles such as authentication, authorization, error architecture, idempotency, pagination and generic CRUD/command rules are defined in their dedicated documents and are referenced here rather than duplicated.

---

# 2. Scope

This document covers:

* POS context;
* Order resources;
* Order Item resources;
* Order types;
* Order lifecycle;
* Order creation;
* Order item creation;
* Order item modification;
* Order item removal;
* Order acceptance;
* Order cancellation;
* Order status;
* item status;
* hall/table context;
* delivery information;
* pricing snapshots;
* Recipe snapshots;
* Set snapshots;
* inventory validation;
* discount integration;
* custom markup integration;
* Cash Session association;
* employee/device context;
* offline POS;
* synchronization;
* kitchen printing;
* Order reads;
* POS read models;
* concurrency;
* idempotency;
* historical integrity;
* performance;
* observability;
* API invariants.

---

# 3. API Boundary

The POS API sits between the POS client and the Application layer:

```text
POS Client
    ↓
API
    ↓
Authentication / Request Context
    ↓
Authorization / Scope
    ↓
POS Use Case
    ↓
Order Domain
    ↓
Inventory / Pricing / Recipe / Cash Session
    ↓
Repository
    ↓
PostgreSQL
```

The API must not directly manipulate:

* Order database rows;
* inventory quantities;
* payment records;
* Cash Session balances;
* Recipe records;
* pricing configuration.

All authoritative business behavior is executed by Application and Domain layers.

---

# 4. POS Context

Every authenticated POS operation operates within an effective operational context.

The relevant context may include:

```text
Business
Branch
Employee
Device
Cash Register
Cash Session
Subscription State
Authorization Context
```

The server derives and validates this context.

Client-provided identifiers are context hints only.

---

# 5. POS Endpoint Groups

The POS API is logically divided into:

```text
POS Context
    ↓
Order
    ↓
Order Items
    ↓
Order Acceptance
    ↓
Order Status
    ↓
Order Modification
    ↓
Order Cancellation
    ↓
Operational Side Effects
```

Financial operations such as payment and refund are defined separately in:

`14_API_Payment_Cash_and_Financial_Endpoints.md`

---

# 6. Core Order Resource

The Order resource represents a customer transaction being processed by the Branch.

Conceptually:

```json
{
  "id": "018f...",
  "order_number": 127,
  "type": "DINE_IN",
  "status": "OPEN",
  "business_id": "018f...",
  "branch_id": "018f...",
  "cash_session_id": "018f...",
  "created_by_employee_id": "018f...",
  "created_at": "2026-10-07T08:30:00Z",
  "updated_at": "2026-10-07T08:31:00Z"
}
```

The exact response representation may include additional read-model fields.

---

# 7. Order Identity

An Order has at least two distinct identifiers:

```text
Order UUID
Order Number
```

### Order UUID

Globally identifies the Order internally and through API contracts.

### Order Number

Human-facing operational identifier used by:

* cashier;
* kitchen;
* customer-facing workflow;
* reports;
* printed receipts where applicable.

The two identifiers must never be treated as interchangeable.

---

# 8. Order Number

The human-readable Order Number may be scoped according to Business/Branch operational rules.

The API must not require clients to generate authoritative Order Numbers.

The server generates the authoritative Order Number.

Offline-created Orders may temporarily use locally assigned operational identifiers subject to synchronization rules, but the authoritative server identity remains the Order UUID and server-side Order Number policy.

---

# 9. Order Types

The API supports the currently defined Order types:

```text
DINE_IN
TAKEAWAY
PHONE_DELIVERY
```

Future Order types may be added without changing the meaning of existing types.

Clients must not invent unsupported enum values.

---

# 10. Dine-In Order

A Dine-in Order may contain:

* hall context;
* table context;
* Order Items;
* employee context;
* Branch context;
* Cash Session context.

Example:

```json
{
  "type": "DINE_IN",
  "hall_id": "018f...",
  "table_id": "018f..."
}
```

The server validates that the selected table belongs to the selected Branch.

---

# 11. Takeaway Order

A Takeaway Order does not require a table.

Example:

```json
{
  "type": "TAKEAWAY"
}
```

The API must not require irrelevant table information for Takeaway Orders.

---

# 12. Phone Delivery Order

A Phone Delivery Order may contain:

```json
{
  "type": "PHONE_DELIVERY",
  "delivery": {
    "phone": "+998...",
    "address": "..."
  }
}
```

The current system stores delivery contact information inside the Order.

It does not create a permanent Customer record.

---

# 13. Customer Data Boundary

The current Order API must not assume a permanent Customer entity.

The following are Order-level data:

* delivery phone;
* delivery address.

A future Customer/CRM system may introduce reusable customer identities without changing the historical meaning of existing Orders.

---

# 14. Order Creation Endpoint

Primary endpoint:

```http
POST /api/v1/orders
```

The endpoint creates an initial Order.

The request may include:

```json
{
  "type": "DINE_IN",
  "hall_id": "018f...",
  "table_id": "018f..."
}
```

or:

```json
{
  "type": "TAKEAWAY"
}
```

or:

```json
{
  "type": "PHONE_DELIVERY",
  "delivery": {
    "phone": "+998...",
    "address": "..."
  }
}
```

---

# 15. Order Creation Responsibilities

Order creation validates:

* authenticated employee;
* employee status;
* Business;
* Branch;
* subscription entitlement;
* device context where required;
* Cash Session requirements;
* Order type;
* table/hall context where applicable;
* Branch operational state.

Order creation must not trust client-provided:

* total;
* tax;
* inventory quantity;
* Product price;
* discount amount;
* final financial state.

---

# 16. Cash Session Association

POS Orders must be associated with the appropriate Cash Session when the business workflow requires it.

The server determines the applicable Cash Session from authoritative context.

The client must not attach an arbitrary Cash Session from another:

* Branch;
* Register;
* employee context.

A closed Cash Session cannot receive new operational Orders.

---

# 17. Order Creation Idempotency

Order creation is a retryable state-changing operation.

The client must provide an idempotency key when required by the API contract.

Example:

```http
POST /api/v1/orders
Idempotency-Key: 018f-operation-uuid
```

If the request is retried, the server must not create a second Order.

The generic idempotency architecture is defined in:

`10_API_Idempotency_and_Concurrency.md`

---

# 18. Initial Order State

A newly created Order normally enters:

```text
OPEN
```

The exact lifecycle may contain additional configured operational states, but the API must distinguish:

* editable state;
* accepted state;
* cancelled state;
* paid/finalized state.

Clients must not arbitrarily assign lifecycle states.

---

# 19. Order Read Endpoint

Primary endpoint:

```http
GET /api/v1/orders/{order_id}
```

The response must include sufficient information for authorized POS users to continue the operational workflow.

Possible response structure:

```json
{
  "data": {
    "id": "018f...",
    "order_number": 127,
    "type": "DINE_IN",
    "status": "OPEN",
    "table": {
      "id": "018f...",
      "name": "Table 4"
    },
    "items": [],
    "totals": {},
    "cash_session_id": "018f...",
    "version": 3
  }
}
```

---

# 20. Order List Endpoint

Primary endpoint:

```http
GET /api/v1/orders
```

Supported filters may include:

```text
status
order_type
branch_id
cash_session_id
employee_id
table_id
created_from
created_to
```

All filters are subject to authorization and Branch scope.

Pagination rules follow:

`11_API_Pagination_Search_Filtering_and_Sorting.md`

---

# 21. POS Active Orders

The POS may require a specialized active Order view.

Example:

```http
GET /api/v1/pos/orders/active
```

This read model should optimize for operational use.

It may return:

* active Order number;
* Order type;
* table;
* item summary;
* current status;
* elapsed time;
* responsible employee;
* item statuses.

It should not retrieve unnecessary historical information.

---

# 22. POS Order Read Model

POS read models may be denormalized for performance.

They remain derived representations.

The authoritative source remains the transactional Order state.

A POS read model must never become the source for:

* payment;
* inventory deduction;
* refund;
* financial correction.

---

# 23. Order Item Resource

An Order Item represents one Product/Set selection inside an Order.

Conceptually:

```json
{
  "id": "018f...",
  "product_id": "018f...",
  "quantity": 2,
  "unit_price": "30000.00",
  "status": "PENDING"
}
```

The authoritative financial representation is maintained by the server.

---

# 24. Add Order Item Endpoint

Primary endpoint:

```http
POST /api/v1/orders/{order_id}/items
```

Example:

```json
{
  "product_id": "018f...",
  "quantity": 2
}
```

The server resolves:

* Product;
* effective Branch menu;
* effective price;
* Recipe Version;
* Set Version;
* required operational availability;
* applicable configuration.

---

# 25. Product Price Resolution

When an Order Item is created, the server determines the applicable selling price.

Resolution follows the established configuration model:

```text
Business Product Configuration
        ↓
Branch Configuration
        ↓
Effective Configuration Version
        ↓
Applicable Selling Price
        ↓
Order Item Price Snapshot
```

The client-provided `unit_price` must not override the authoritative price.

---

# 26. Order Item Price Snapshot

Once an Order Item is created, the applicable price is captured.

The snapshot may contain:

```text
Product UUID
Product Name Snapshot
Unit Price
Quantity
Configuration Version
Price Source
Currency
```

Historical requirements determine the exact fields.

Later Product price changes must not rewrite this snapshot.

---

# 27. Product Configuration Snapshot

The Order Item may retain sufficient configuration context to reconstruct the transaction.

Depending on Product type, this may include:

* Product identity;
* Recipe Version;
* Set Version;
* configuration version;
* pricing version;
* component information.

The exact database representation is defined by the Database section.

---

# 28. Recipe Validation

When a Product requires a Recipe, the server validates the applicable Recipe state.

Normal sale requires:

```text
Recipe exists
+
Recipe approved
+
Recipe applicable
```

An invalid or unapproved Recipe must prevent normal sale.

---

# 29. Inventory Validation

Adding an item may validate operational availability.

However, the final authoritative inventory deduction occurs at the defined Order acceptance/transaction boundary.

The API must not use cached stock as the final authority.

---

# 30. Inventory Race Protection

Two POS clients may attempt to accept Orders using the same limited inventory.

The authoritative transaction must prevent:

```text
available stock < required stock
```

from resulting in negative inventory.

The final inventory validation must occur inside the appropriate database transaction.

---

# 31. Set Validation

For a Set Product, the server validates:

* active Set;
* valid Set Version;
* mandatory components;
* Branch availability;
* Recipe requirements;
* sufficient inventory.

Component substitution is not allowed during normal sale.

---

# 32. Order Item Modification

Primary endpoint:

```http
PATCH /api/v1/orders/{order_id}/items/{item_id}
```

The operation may support permitted fields such as:

```text
quantity
allowed configuration options
```

The server recalculates affected authoritative values.

---

# 33. Quantity Modification

Changing quantity must validate:

* Order state;
* employee permission;
* Product availability;
* Recipe requirements;
* inventory requirements;
* financial calculation.

The client must not directly set the resulting Order total.

---

# 34. Order Item Removal

Primary endpoint:

```http
DELETE /api/v1/orders/{order_id}/items/{item_id}
```

Removal is allowed only while the Order remains in an editable state and the employee has the required permission.

If historical or accepted state prevents removal, the API returns the appropriate business error.

---

# 35. Modify Order Endpoint

A specialized command may be used when one user action changes multiple Order components atomically:

```http
POST /api/v1/orders/{order_id}/modify
```

Example:

```json
{
  "changes": [
    {
      "item_id": "018f...",
      "quantity": 2
    },
    {
      "item_id": "018f...",
      "action": "REMOVE"
    }
  ]
}
```

This endpoint is appropriate only when the operation must be treated as one business command.

---

# 36. Recipe Component Modification

If the business allows Order customization based on Recipe components, the POS may expose permitted operations such as:

```text
ADD
REMOVE
```

The server validates:

* component eligibility;
* inventory;
* price adjustment;
* Recipe rules;
* Product configuration.

Unsupported component modifications must be rejected.

---

# 37. Extras and Additions

Additional Product components may affect the Order price.

The server calculates the resulting price.

Client-side calculated totals are informational only.

Every financial adjustment must be represented in the authoritative Order snapshot.

---

# 38. Removal and Price Adjustment

Removing a component may affect price where the business configuration defines such behavior.

The API must use the configured pricing rule.

The client must not invent a negative or positive adjustment.

---

# 39. Custom Markup

Where authorized, the POS may request a transaction-specific custom markup.

Example endpoint:

```http
POST /api/v1/orders/{order_id}/markup
```

Request:

```json
{
  "markup_percent": 15
}
```

The server validates:

```text
0% ≤ markup ≤ 100%
```

and uses the applicable Last Purchase Cost.

The resulting transaction price is captured in the Order snapshot.

---

# 40. Markup Restrictions

Custom markup:

* does not modify Global Product price;
* does not modify Branch standard price;
* does not modify historical prices;
* does not modify inventory cost;
* requires explicit permission.

The generic pricing rules are defined in:

`18_Menu_Pricing_and_Configuration.md`

and the corresponding API pricing rules are referenced from the API section.

---

# 41. Discount Integration

Discount application is a separate business command.

Example:

```http
POST /api/v1/orders/{order_id}/discounts
```

The discount API is primarily defined in:

`14_API_Payment_Cash_and_Financial_Endpoints.md`

This document only defines the POS/Order boundary:

* discount affects the Order financial snapshot;
* Product base price remains unchanged;
* Order Item historical price remains identifiable;
* unauthorized discount attempts are rejected.

---

# 42. Order Total

The server calculates the authoritative Order total.

Conceptually:

```text
Order Item Snapshots
        +
Allowed Adjustments
        -
Discounts
        =
Authoritative Order Amount
```

The client may display a calculated preview, but the server result is authoritative.

---

# 43. Client Total

The client may send a calculated total for UX purposes where useful.

The server must never accept it as authoritative without recalculation/validation.

Example:

```json
{
  "client_total": "60000.00"
}
```

This field, if supported, is diagnostic rather than authoritative.

---

# 44. Order Acceptance Endpoint

Primary endpoint:

```http
POST /api/v1/orders/{order_id}/accept
```

Acceptance is a business command.

It is the critical boundary at which the server confirms that the Order can proceed operationally.

---

# 45. Order Acceptance Validation

Acceptance validates, as applicable:

* authenticated employee;
* Branch scope;
* permission;
* Order state;
* Cash Session;
* Product active state;
* Branch menu availability;
* Recipe validity;
* Set validity;
* inventory;
* financial calculations;
* required configuration version;
* concurrency;
* subscription state.

---

# 46. Order Acceptance Transaction

The authoritative acceptance transaction may include:

```text
Validate Order
      ↓
Validate Order Items
      ↓
Validate Inventory
      ↓
Create Inventory Transactions
      ↓
Update Order State
      ↓
Persist Financial Snapshot
      ↓
Create Audit / Outbox
      ↓
Commit
```

The exact transaction boundary is defined by the backend transaction architecture.

---

# 47. Acceptance Idempotency

Acceptance must be idempotent.

Repeated requests using the same operation UUID must not:

* deduct inventory twice;
* create duplicate kitchen jobs;
* create duplicate Order transitions;
* create duplicate financial effects.

A repeated valid acceptance request may return the existing authoritative result.

---

# 48. Acceptance Concurrency

If two employees/devices attempt to accept the same Order concurrently:

```text
Request A → accepted
Request B → conflict / already processed
```

Only one authoritative acceptance may occur.

The server must use the appropriate concurrency mechanism.

---

# 49. Kitchen Printing

Successful Order acceptance may create a kitchen-printing event.

Example:

```text
Order Accepted
      ↓
Outbox Event
      ↓
Printer Routing
      ↓
Kitchen Printer
```

Printing is a secondary effect.

Printer failure must not rollback an already committed Order acceptance.

---

# 50. Printer Routing

The printing subsystem may route Order Items based on Product configuration.

Examples:

```text
Pizza → Pizza Printer
Lavash → Lavash Printer
Drinks → Drinks Printer
```

The POS API does not directly control printer hardware.

It produces the authoritative Order event required by the printing subsystem.

---

# 51. Kitchen Receipt Contract

The kitchen event should contain sufficient information for printing, including where applicable:

* Order Number;
* Order Type;
* table;
* Order Items;
* quantities;
* item configuration;
* additions/removals;
* notes;
* Branch;
* creation/acceptance time.

The event must use the accepted Order snapshot rather than rereading mutable current Product configuration.

---

# 52. Order Notes

The API may support Order-level or Item-level notes where defined by the business.

Example:

```json
{
  "note": "No onions"
}
```

Notes must not silently change:

* Product Recipe;
* Product price;
* inventory configuration.

---

# 53. Order Status

Order status represents the lifecycle state of the transaction.

The Owner may configure operational statuses/stages.

The API must distinguish between:

```text
System lifecycle state
Operational display state
Item status
```

A client must not arbitrarily create invalid lifecycle transitions.

---

# 54. System Lifecycle States

The core system should preserve semantic states such as:

```text
OPEN
ACCEPTED
CANCELLED
PAID / FINALIZED
```

Additional operational states may be configured where supported.

The exact state machine is owned by the Domain layer.

---

# 55. Operational Status

The Business may configure Order stages.

Examples:

```text
NEW
PREPARING
READY
COMPLETED
```

The API exposes configured valid states but does not allow arbitrary state names to bypass Domain validation.

---

# 56. Order Status Endpoint

Where an explicit status command is required:

```http
POST /api/v1/orders/{order_id}/status
```

Example:

```json
{
  "status": "READY"
}
```

The server validates whether the transition is permitted.

Direct database-style:

```http
PATCH /orders/{id}
{
  "status": "READY"
}
```

must not bypass the state machine.

---

# 57. Item Status

Each Order Item may have its own operational status.

Example:

```json
{
  "product": "Lavash",
  "quantity": 2,
  "status": "PREPARING"
}
```

Another item may simultaneously be:

```text
Hotdog × 1 → READY
```

The API must support per-item operational visibility where configured.

---

# 58. Item Status Endpoint

Example:

```http
POST /api/v1/orders/{order_id}/items/{item_id}/status
```

Request:

```json
{
  "status": "READY"
}
```

Authorization must be evaluated according to the employee's role and permissions.

---

# 59. Status Visibility

The API may expose:

* Order status;
* Item status;
* status history;
* current operational stage.

Visibility depends on role, Branch scope and permissions.

A user must not receive unauthorized operational information.

---

# 60. Status History

Important status transitions should remain historically traceable.

Where history is required, the system should retain:

```text
Previous Status
New Status
Actor
Device
Timestamp
Order
Item where applicable
Reason where required
```

Historical status data must not be reconstructed solely from current state.

---

# 61. Order Cancellation

Primary endpoint:

```http
POST /api/v1/orders/{order_id}/cancel
```

Cancellation is a business command.

Request may include:

```json
{
  "reason": "Customer cancelled"
}
```

The server validates:

* Order state;
* employee permission;
* Branch;
* Cash Session where applicable;
* financial state;
* inventory state;
* cancellation rules.

---

# 62. Cancellation After Acceptance

Cancellation after acceptance may have additional business consequences.

The API must not simply revert the Order state without executing the required business process.

Potential effects may include:

* inventory reversal;
* audit event;
* notification;
* financial adjustment.

The exact reversal behavior belongs to the Domain/Application layer.

---

# 63. Cancellation After Payment

A paid/finalized Order must not use ordinary cancellation to bypass financial controls.

The API must route such cases through the appropriate financial/refund process.

Payment/refund behavior is defined in:

`14_API_Payment_Cash_and_Financial_Endpoints.md`

---

# 64. Existing Order After Menu Change

If a Product becomes inactive after being added to an Order:

```text
Existing Order Item
→ remains valid under its snapshot

New Order Item
→ blocked when the new configuration is effective
```

Current menu state must not rewrite the existing Order.

---

# 65. Existing Order After Price Change

If the Product price changes after the Order Item was created:

```text
Existing Order Item
→ old price snapshot

New Order Item
→ new effective price
```

The API must never silently recalculate existing Order Items from current Product pricing.

---

# 66. Existing Order Across Cash Sessions

An open Order may remain open across a Cash Session boundary where business rules permit.

Its existing Order Item snapshots remain authoritative.

New configuration applies only according to the defined effective configuration rules.

---

# 67. Branch Isolation

Every Order belongs to exactly one Business and Branch.

The API must reject attempts to:

* access another Business's Order;
* modify another Branch's Order without authorized cross-Branch permission;
* attach an Order to an unrelated Branch;
* attach items from an unauthorized Branch context.

---

# 68. Employee Attribution

Important Order operations should retain the responsible employee context.

Examples:

* Order creation;
* item addition;
* item modification;
* acceptance;
* cancellation;
* discount;
* markup;
* status changes.

Historical attribution must not be overwritten by later users.

---

# 69. Device Attribution

Important POS operations should retain Device context where applicable.

This is especially important for:

* offline Orders;
* synchronization;
* security investigations;
* duplicate operation analysis.

---

# 70. Table and Hall Context

Dine-in Orders may reference:

```text
Hall
Table
```

The server validates:

* table belongs to Branch;
* table is active;
* table state permits the operation;
* employee has permission where required.

The API must not trust a client-provided table ID alone.

---

# 71. Table State

A table may be represented operationally as:

```text
AVAILABLE
OCCUPIED
WAITING
```

The exact state model is defined by the Table domain.

Order operations may cause table state changes through Application/Domain logic.

The API must not directly mutate table state as a side effect outside the appropriate use case.

---

# 72. Dine-In Table Assignment

Where supported:

```http
POST /api/v1/orders/{order_id}/table
```

Request:

```json
{
  "table_id": "018f..."
}
```

The server validates:

* Order type;
* Order state;
* Branch;
* table availability;
* permissions;
* concurrency.

---

# 73. Table Release

When the Order lifecycle permits table release, the Application layer updates the table state.

The POS API should not require the client to independently synchronize table occupancy.

Server state remains authoritative.

---

# 74. Phone Delivery Data Update

While the Order is editable, authorized users may update:

```http
PATCH /api/v1/orders/{order_id}/delivery
```

Example:

```json
{
  "phone": "+998...",
  "address": "..."
}
```

The endpoint is valid only for `PHONE_DELIVERY` Orders.

---

# 75. Delivery Data History

Changes to delivery information should not rewrite historical finalized transactions.

If historical traceability is required, changes are recorded through the normal Order history/audit mechanism.

---

# 76. Order Modification Permission

Modification requires:

* authenticated employee;
* active employee status;
* Branch scope;
* Order permission;
* valid Order state;
* subscription entitlement;
* device constraints where applicable.

Frontend visibility is not a security boundary.

---

# 77. Paid Order Modification

Once an Order is paid/finalized, ordinary modification must be blocked.

Changes requiring financial correction must use explicit correction/refund mechanisms.

The POS API must not provide a generic endpoint capable of silently modifying finalized financial state.

---

# 78. Offline Order Creation

A trusted device may create an Order while offline when its offline authorization permits POS operation.

The local operation contains:

```text
Operation UUID
Local Order UUID
Employee
Business
Branch
Device
Cash Session context
Order type
Order payload
Created-at metadata
```

The operation is queued for synchronization.

---

# 79. Offline Order Pricing

Offline POS uses the latest valid authorized local configuration.

The device must capture the effective local price/configuration snapshot at Order Item creation.

When synchronized, the server must preserve that transaction snapshot according to offline business rules.

A newer server price must not retroactively change an offline-created Order.

---

# 80. Offline Order Acceptance

Offline acceptance is allowed only if the offline authorization explicitly permits the operation.

The local client must execute local validation against its authorized state.

After synchronization, the server validates the operation against authoritative rules.

The exact offline conflict model is defined in:

`19_API_Offline_Synchronization_and_Reconciliation.md`

---

# 81. Offline Inventory

Offline inventory is based on the device's latest authorized local inventory state.

The device must not assume that local inventory is globally authoritative.

During synchronization, the server determines whether the transaction can be accepted without violating authoritative inventory rules.

---

# 82. Offline Order Conflicts

Possible server results include:

```text
ACCEPTED
ALREADY_PROCESSED
CONFLICT
REJECTED
TEMPORARY_FAILURE
```

A conflict must preserve the original client operation and server state.

The server must not silently rewrite the historical transaction.

---

# 83. Synchronization Priority

When synchronizing POS data:

```text
Order Transaction
        ↓
Order-related Inventory Transaction
        ↓
Configuration Synchronization
```

Transaction synchronization must not be invalidated merely because a newer configuration exists.

---

# 84. Order Replay Protection

Every offline state-changing operation must have a stable operation UUID.

Repeated synchronization must not duplicate:

* Order;
* Order Item;
* inventory deduction;
* status transition;
* cancellation;
* other authoritative business effects.

---

# 85. POS Synchronization Readiness

The normal online POS API should use contracts that can be represented in synchronization operations.

Where an operation cannot safely be replayed offline, the API contract must explicitly identify it as online-only.

---

# 86. POS-Only Operations

Examples of operations that may require online authority include:

* first-time device registration;
* trusted device establishment;
* security-sensitive authorization changes;
* certain financial operations;
* operations explicitly prohibited by offline authorization.

The client must not infer offline permission merely because an endpoint exists.

---

# 87. Order Version

The Order should expose a concurrency version.

Example:

```json
{
  "id": "018f...",
  "version": 7
}
```

Updates may use:

```http
If-Match: "7"
```

or equivalent version semantics.

A stale update must return a conflict.

---

# 88. Concurrent Order Modification

Example:

```text
Cashier A reads Order version 7
Cashier B modifies Order
Order becomes version 8

Cashier A sends update based on version 7
        ↓
409 CONFLICT / STALE_VERSION
```

The server must not silently overwrite version 8.

---

# 89. Concurrent Acceptance and Modification

Acceptance must protect against concurrent modification.

If an Order changes while acceptance is being processed, the authoritative transaction must detect the conflict and prevent inconsistent state.

---

# 90. Order Read Consistency

A POS read immediately following a successful mutation should observe the committed authoritative state.

Read-after-write consistency is especially important for:

* Order acceptance;
* item changes;
* cancellation;
* status changes.

---

# 91. Cache Use in POS

POS may use cached read data for:

* menu;
* Product reference data;
* configuration;
* non-authoritative display data.

The server must use authoritative state for:

* final price validation;
* inventory deduction;
* Order acceptance;
* payment;
* financial state.

---

# 92. API Response After Mutation

Successful mutation endpoints should return the authoritative resulting representation where practical.

Example:

```json
{
  "data": {
    "id": "018f...",
    "status": "ACCEPTED",
    "version": 8,
    "totals": {
      "grand_total": "75000.00"
    }
  }
}
```

The client should not need to reconstruct authoritative state from its own assumptions.

---

# 93. Partial Failure After Order Commit

After Order acceptance commits, secondary operations may fail.

Examples:

* kitchen printer unavailable;
* notification provider unavailable;
* analytics processing delayed.

The API must not report the Order as uncommitted if the authoritative transaction already committed.

The response and subsequent status endpoint must reflect the committed state.

---

# 94. Printer Failure Representation

If operationally useful, the API/read model may expose:

```text
printing_status
```

such as:

```text
PENDING
SENT
FAILED
```

Printing status must not be confused with Order financial/lifecycle state.

---

# 95. Order Audit

Important Order operations should create audit context including:

```text
Order UUID
Order Number
Business UUID
Branch UUID
Employee UUID
Device UUID
Cash Session UUID where applicable
Operation UUID
Previous State
New State
Timestamp
Reason where applicable
```

Audit records are immutable.

---

# 96. Order History

Where historical visibility is required:

```http
GET /api/v1/orders/{order_id}/history
```

The endpoint may return:

* state changes;
* item changes;
* pricing changes;
* cancellation;
* status transitions;
* important corrections.

Sensitive data must be filtered according to authorization.

---

# 97. Order History Is Not Current State

The current Order resource represents authoritative current state.

History represents immutable historical events/snapshots.

The API must not require clients to reconstruct current state by replaying arbitrary history.

---

# 98. Order Search

POS and administrative users may search Orders by supported fields.

Examples:

```text
order_number
order_uuid
status
table
type
date
employee
cash_session
```

Search must remain Business/Branch scoped.

The search architecture follows:

`11_API_Pagination_Search_Filtering_and_Sorting.md`

---

# 99. POS Order Lookup

The POS may use a compact endpoint:

```http
GET /api/v1/pos/orders/{order_id}
```

or an optimized response profile.

This is appropriate when the normal administrative Order representation contains unnecessary fields.

The two representations must remain semantically consistent.

---

# 100. API Resource Profiles

The API may expose different response profiles where justified:

```text
POS profile
Administrative profile
Report profile
Synchronization profile
```

Profiles must not create different business meanings.

They only optimize representation.

---

# 101. Order Financial Boundary

The POS Order API is responsible for establishing the Order financial state.

Payment itself belongs to the financial API.

Therefore:

```text
Order API
→ Order amount and financial snapshot

Payment API
→ Payment transaction
```

The two must not be conflated.

---

# 102. Order and Payment Separation

Creating an Order does not automatically mean that payment exists.

Similarly:

```text
Order Accepted
≠
Order Paid
```

Payment endpoints establish payment state.

The Order API must expose sufficient state for the financial API to operate safely.

---

# 103. Order Finalization

When payment successfully finalizes an Order, the financial API updates the Order according to the Domain lifecycle.

The POS read model must subsequently expose the finalized state.

The POS Order API must not create duplicate finalization effects.

---

# 104. Order Cancellation and Inventory

If cancellation requires inventory reversal, the reversal must be performed through the Application/Domain transaction.

The API must not instruct the client to manually “add stock back”.

---

# 105. Order Acceptance and Inventory

Similarly, the client must not submit:

```json
{
  "stock_after": 17
}
```

as an authoritative inventory result.

The server calculates and persists the inventory effect.

---

# 106. Order and Recipe Snapshot

When a Recipe affects an Order, the relevant Recipe Version must remain identifiable.

Later Recipe changes must not reinterpret historical Order consumption.

---

# 107. Order and Set Snapshot

When a Set is sold, the applicable Set configuration/version must remain identifiable.

Later Set composition changes must not reinterpret historical Set Orders.

---

# 108. Order and Product Deactivation

Product deactivation must prevent new additions when the effective configuration applies.

Existing historical Order Items remain valid.

The API must not return a historical Order as invalid merely because its Product is currently inactive.

---

# 109. Order API and Subscription

If the Business is:

```text
ACTIVE
```

normal POS mutations may proceed subject to permissions.

If:

```text
READ_ONLY
```

new modifying POS operations must be blocked.

Historical Order reads remain available according to access rules.

Offline authorization must not bypass subscription restrictions.

---

# 110. Deleted Business

A Business in `DELETED` state cannot accept normal Order API operations.

Historical records must not be recreated by replaying old client operations.

Synchronization against a deleted Business must be rejected.

---

# 111. POS Authorization Performance

POS authorization should remain efficient.

Initial target:

```text
Authorization overhead p95 ≤ 100 ms
```

Cached authorization lookup target:

```text
p95 ≤ 20 ms
```

Security-sensitive cache misses must fall back safely to authoritative state.

---

# 112. POS API Performance SLO

Initial targets:

| Operation              |   Target |
| ---------------------- | -------: |
| POS Order creation p95 | ≤ 300 ms |
| Add Order Item p95     | ≤ 300 ms |
| Modify Order Item p95  | ≤ 300 ms |
| Remove Order Item p95  | ≤ 300 ms |
| Order acceptance p95   | ≤ 500 ms |
| Order cancellation p95 | ≤ 400 ms |
| Order read p95         | ≤ 200 ms |
| Active Orders read p95 | ≤ 250 ms |
| Item status update p95 | ≤ 300 ms |
| Table assignment p95   | ≤ 300 ms |

Targets exclude unavoidable external printing latency.

---

# 113. POS Availability

The API should support the broader backend availability target:

**≥ 99.9% monthly**

Offline capability provides operational continuity when network connectivity is temporarily unavailable, subject to trusted-device authorization and offline business rules.

---

# 114. POS Payload Size

POS responses should remain compact.

A normal Order response should not unnecessarily include:

* full audit history;
* full Recipe history;
* unrelated employee data;
* complete inventory history;
* report data;
* unrelated Business configuration.

Large historical information should use dedicated endpoints.

---

# 115. POS Network Efficiency

Normal POS workflows should minimize:

* unnecessary round trips;
* repeated configuration downloads;
* oversized JSON;
* synchronous external integrations.

A successful Order acceptance should not require the POS client to separately perform every secondary action.

---

# 116. Batch Item Addition

Where useful, the API may support bounded item batches:

```http
POST /api/v1/orders/{order_id}/items/batch
```

Example:

```json
{
  "items": [
    {
      "product_id": "018f...",
      "quantity": 2
    },
    {
      "product_id": "018f...",
      "quantity": 1
    }
  ]
}
```

The batch must have a strict maximum size.

The business transaction semantics must be explicit.

---

# 117. Batch vs Single Item Semantics

A batch request must not silently become an unbounded transaction.

The API must document whether:

```text
all items succeed
```

or:

```text
per-item results are returned
```

For normal POS item addition, atomicity is preferred when the user expects one operation.

---

# 118. POS Prefetch

The POS client may preload:

* effective menu;
* Product reference data;
* Branch configuration;
* pricing configuration;
* operational statuses.

Prefetch is a performance optimization.

The server remains authoritative.

---

# 119. POS Configuration Version

POS read responses should expose relevant configuration versions where useful.

Example:

```json
{
  "configuration_version": 12,
  "pricing_version": 7
}
```

This allows clients to detect stale local state without treating the version itself as authorization.

---

# 120. POS Context Switching

When the user switches Branch context, the API/session context must be recalculated.

The POS must not continue using:

* previous Branch menu;
* previous Branch price;
* previous Branch permissions;
* previous Cash Session

after the context becomes invalid.

---

# 121. POS Device Context

A trusted POS device may be associated with:

```text
Business
Branch
Employee/session
Device identity
```

The API validates the relationship.

Device identity does not replace employee authentication.

---

# 122. POS Security Events

The API should expose or generate security/audit events for important anomalies such as:

* unauthorized Order modification;
* repeated failed acceptance;
* stale offline operation;
* device mismatch;
* invalid synchronization;
* suspicious repeated operation UUID;
* unauthorized cross-Branch access attempt.

These events should be processed according to the security architecture.

---

# 123. Error Codes

POS/Order-specific errors may include:

```text
ORDER_NOT_EDITABLE
ORDER_ALREADY_ACCEPTED
ORDER_ALREADY_CANCELLED
ORDER_ALREADY_PAID
ORDER_NOT_FOUND
ORDER_TYPE_INVALID
TABLE_NOT_AVAILABLE
TABLE_BRANCH_MISMATCH
CASH_SESSION_REQUIRED
CASH_SESSION_CLOSED
PRODUCT_NOT_AVAILABLE
PRODUCT_INACTIVE
PRODUCT_BRANCH_DISABLED
RECIPE_NOT_APPROVED
RECIPE_NOT_AVAILABLE
SET_NOT_AVAILABLE
SET_COMPONENT_UNAVAILABLE
INSUFFICIENT_STOCK
ORDER_VERSION_CONFLICT
INVALID_ORDER_STATUS_TRANSITION
ITEM_NOT_FOUND
ITEM_NOT_EDITABLE
MARKUP_OUT_OF_RANGE
MARKUP_NOT_ALLOWED
DELIVERY_DATA_NOT_ALLOWED
OFFLINE_OPERATION_NOT_ALLOWED
OFFLINE_CONFIGURATION_EXPIRED
SYNC_ORDER_CONFLICT
```

Generic authentication, authorization and infrastructure errors remain defined by the API error architecture.

---

# 124. POS Error Behavior

For operational errors, the client should receive enough information to recover without exposing internal implementation.

Example:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "The selected product cannot be accepted because required stock is insufficient.",
    "request_id": "01J...",
    "details": {
      "item_id": "018f..."
    }
  }
}
```

The API should not expose internal SQL, stack traces or private inventory implementation details.

---

# 125. Retry Rules

Typical retry behavior:

```text
Network Timeout
→ Retry with same idempotency key

503 Service Unavailable
→ Retry with bounded backoff

STALE_VERSION
→ Refresh Order and retry after user decision

INSUFFICIENT_STOCK
→ Do not blindly retry

ORDER_NOT_EDITABLE
→ User action required

ALREADY_PROCESSED
→ Use returned authoritative result
```

---

# 126. Observability

POS API metrics should include:

```text
order_create_count
order_accept_count
order_cancel_count
order_item_add_count
order_item_modify_count
order_item_remove_count
order_status_change_count
order_conflict_count
order_idempotency_replay_count
order_sync_conflict_count
```

Metrics should avoid uncontrolled Business/Product UUID labels.

---

# 127. POS Tracing

A trace may connect:

```text
HTTP Request
    ↓
Order Use Case
    ↓
Inventory Validation
    ↓
Inventory Transaction
    ↓
Order Transaction
    ↓
Outbox Event
    ↓
Printer Worker
```

This allows operators to diagnose POS latency without treating secondary effects as part of the core transaction.

---

# 128. POS Audit vs Logging

API request logs answer:

> What request was received?

Order audit answers:

> What important Order state changed?

Both may reference:

* Request ID;
* Operation UUID;
* Employee;
* Device;
* Business;
* Branch.

---

# 129. API Contract Testing

POS endpoints must have automated contract tests covering at least:

* request schema;
* response schema;
* authentication;
* authorization;
* Branch isolation;
* Order lifecycle;
* pricing snapshot;
* inventory validation;
* idempotency;
* concurrency;
* offline compatibility;
* error codes;
* pagination where applicable.

---

# 130. End-to-End POS Scenarios

The test suite should cover:

### Scenario A — Dine-In

```text
Create Order
→ Select Table
→ Add Items
→ Modify Item
→ Accept
→ Kitchen Event
→ Pay
→ Finalize
```

### Scenario B — Takeaway

```text
Create Order
→ Add Items
→ Accept
→ Pay
→ Finalize
```

### Scenario C — Phone Delivery

```text
Create Delivery Order
→ Add Phone/Address
→ Add Items
→ Accept
→ Pay
→ Finalize
```

### Scenario D — Offline

```text
Create Offline Order
→ Accept Offline
→ Queue
→ Synchronize
→ Server Validation
→ Authoritative Result
```

---

# 131. Concurrency Test Scenarios

Tests should include:

```text
Two users modify same Order

Two users accept same Order

Price changes while Order remains open

Product becomes inactive while Order is open

Inventory is consumed concurrently

Duplicate acceptance request

Duplicate offline synchronization

Cash Session closes while Order is being modified
```

---

# 132. Historical Integrity Tests

The system must verify that:

```text
Current Product Price
does not alter
Historical Order Item Price
```

and:

```text
Current Recipe
does not alter
Historical Recipe Version
```

and:

```text
Current Set Configuration
does not alter
Historical Set Order
```

---

# 133. API Contract Compatibility

Changes to POS endpoints must consider:

* Web POS;
* future desktop POS;
* offline clients;
* synchronization;
* printer workers;
* reports;
* financial APIs.

Breaking changes require API versioning or an explicit migration strategy.

---

# 134. API Documentation Requirements

Each POS endpoint must document:

* method;
* path;
* purpose;
* authentication;
* required permission;
* Business scope;
* Branch scope;
* request schema;
* response schema;
* idempotency;
* concurrency;
* errors;
* retry behavior;
* offline availability;
* side effects.

---

# 135. Recommended Endpoint Map

The initial POS/Order endpoint map is:

```text
Orders

POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}

POS

GET    /api/v1/pos/orders/active
GET    /api/v1/pos/orders/{order_id}

Order Items

POST   /api/v1/orders/{order_id}/items
PATCH  /api/v1/orders/{order_id}/items/{item_id}
DELETE /api/v1/orders/{order_id}/items/{item_id}

Order Commands

POST   /api/v1/orders/{order_id}/modify
POST   /api/v1/orders/{order_id}/accept
POST   /api/v1/orders/{order_id}/cancel
POST   /api/v1/orders/{order_id}/status

Item Commands

POST   /api/v1/orders/{order_id}/items/{item_id}/status

Table Context

POST   /api/v1/orders/{order_id}/table

Delivery

PATCH  /api/v1/orders/{order_id}/delivery

Pricing Operations

POST   /api/v1/orders/{order_id}/markup

History

GET    /api/v1/orders/{order_id}/history
```

Payment, refund and Cash Session financial operations are intentionally defined in the financial endpoint document.

---

# 136. Endpoint Classification

| Endpoint           | Type    | Idempotency            | Financial Authority         |
| ------------------ | ------- | ---------------------- | --------------------------- |
| Create Order       | Command | Required               | No                          |
| Add Item           | Command | Required               | No                          |
| Modify Item        | Command | Required               | No                          |
| Remove Item        | Command | Required               | No                          |
| Accept Order       | Command | Required               | Order financial snapshot    |
| Cancel Order       | Command | Required               | No direct payment authority |
| Change Status      | Command | Required               | No                          |
| Change Table       | Command | Required               | No                          |
| Update Delivery    | Update  | Required where retried | No                          |
| Apply Markup       | Command | Required               | Transaction pricing         |
| Read Order         | Query   | N/A                    | Read only                   |
| Read Active Orders | Query   | N/A                    | Read only                   |
| Read History       | Query   | N/A                    | Read only                   |

The exact idempotency requirement is governed by the generic idempotency policy and may vary for safe operations.

---

# 137. Architectural Guardrails

The POS API must prohibit:

* client-authoritative Order totals;
* client-authoritative Product prices;
* client-authoritative inventory;
* direct database access from routes;
* arbitrary Order status assignment;
* arbitrary financial modification of paid Orders;
* cross-Business Order access;
* cross-Branch Order access without explicit authority;
* duplicate acceptance;
* duplicate offline replay;
* silent stale Order overwrite;
* current configuration rewriting historical Orders;
* printer failure rolling back committed Orders;
* notification failure rolling back committed Orders;
* frontend-only authorization;
* cache as final inventory authority;
* cache as final financial authority.

---

# 138. System Invariants

The following invariants apply to POS and Order APIs:

1. Every Order belongs to exactly one Business.
2. Every Order belongs to exactly one Branch.
3. Order UUID and Order Number are separate identities.
4. Order Number is server-authoritative.
5. Client-provided Business ID is never sufficient authorization.
6. Client-provided Branch ID is never sufficient authorization.
7. Client-provided Employee ID is never sufficient authentication.
8. Client-provided Device ID is never sufficient authentication.
9. Dine-in Orders may require Hall/Table context.
10. Takeaway Orders do not require a Table.
11. Phone Delivery Orders may contain phone and address.
12. Current implementation does not require a permanent Customer entity.
13. Delivery contact information belongs to the Order.
14. New Orders require valid operational context.
15. Closed Cash Sessions cannot accept new applicable POS Orders.
16. Order creation is idempotent where retryable.
17. Duplicate Order creation must not create duplicate Orders.
18. Order Item creation uses server-authoritative Product configuration.
19. Client-provided Product price is never authoritative.
20. Client-provided Order total is never authoritative.
21. Server calculates the authoritative Order amount.
22. Order Item price is captured as a historical snapshot.
23. Later Product price changes do not modify existing Order Item prices.
24. Historical Orders do not depend on current Product prices.
25. Required Recipe approval must exist before normal sale.
26. Current Recipe changes do not reinterpret historical Order consumption.
27. Set sales retain the applicable Set configuration/version.
28. Set component substitution is prohibited during normal sale.
29. Branch menu availability is evaluated for new sales.
30. Product deactivation does not invalidate historical Order Items.
31. Inventory is authoritative in PostgreSQL.
32. Cached inventory is never final authority for acceptance.
33. Inventory deduction occurs through the authoritative transaction boundary.
34. Negative inventory is prohibited.
35. Concurrent inventory consumption cannot create negative stock.
36. Order acceptance validates authoritative inventory.
37. Order acceptance is idempotent.
38. Duplicate acceptance cannot duplicate inventory deduction.
39. Duplicate acceptance cannot duplicate Order transition.
40. Duplicate acceptance cannot duplicate core business effects.
41. Order acceptance validates Order state.
42. Order acceptance validates Product state.
43. Order acceptance validates Recipe requirements.
44. Order acceptance validates Set requirements.
45. Order acceptance validates applicable configuration.
46. Order acceptance respects subscription entitlement.
47. Order acceptance respects employee permission.
48. Order acceptance respects Branch scope.
49. Order acceptance respects device restrictions where required.
50. Concurrent acceptance of the same Order cannot produce two successful authoritative transitions.
51. Stale Order updates are rejected.
52. Order versions provide optimistic concurrency protection where required.
53. Generic PATCH cannot bypass lifecycle rules.
54. Order status transitions are Domain-controlled.
55. Clients cannot assign arbitrary lifecycle states.
56. Operational Order statuses are validated against configured stages.
57. Item status may differ from Order status.
58. Item status transitions are authorized.
59. Important status changes remain historically traceable.
60. Existing Orders are not invalidated by later menu changes.
61. Existing Orders retain historical price snapshots.
62. Existing Orders retain historical configuration context where required.
63. Paid/finalized Orders cannot be modified through ordinary Order APIs.
64. Paid/finalized changes use explicit financial correction mechanisms.
65. Cancellation is a business command.
66. Cancellation requires appropriate permission.
67. Cancellation cannot bypass financial controls.
68. Payment is separate from Order creation.
69. Order acceptance is not equivalent to payment.
70. Payment state is managed by the financial API.
71. Refund state is managed by the financial API.
72. Order cancellation cannot silently create an unauthorized refund.
73. Custom markup is limited to 0–100%.
74. Custom markup uses the applicable Last Purchase Cost.
75. Custom markup does not modify Product standard price.
76. Custom markup does not modify historical prices.
77. Discount does not modify Product base price.
78. Discount remains a transaction-level financial adjustment.
79. Dine-in table references must belong to the same Branch.
80. Table assignment is concurrency-safe.
81. Client cannot independently determine authoritative table state.
82. Order table state changes are handled by the Application/Domain layer.
83. Printer output is a secondary effect.
84. Printer failure cannot rollback committed Order acceptance.
85. Notification failure cannot rollback committed Order acceptance.
86. Kitchen events use the accepted Order snapshot.
87. Current Product configuration cannot reinterpret historical kitchen events.
88. Employee attribution of important Order operations is retained.
89. Device attribution of important POS operations is retained.
90. Offline Orders require trusted-device authorization.
91. Offline authorization must explicitly permit the operation.
92. Offline devices cannot extend their own authorization.
93. Offline Order prices use the latest valid authorized local configuration.
94. New server prices do not retroactively change offline-created Order Items.
95. Offline operations have stable operation UUIDs.
96. Replayed offline operations do not duplicate business effects.
97. Synchronization remains server-authoritative.
98. Synchronization cannot resurrect a deleted Business.
99. Synchronization cannot bypass subscription restrictions.
100. Synchronization cannot bypass Branch authorization.
101. Synchronization conflicts remain explicit.
102. POS read models are derived representations.
103. POS read models are not financial authority.
104. POS read models are not inventory authority.
105. API cache is not authoritative Order state.
106. Order history is separate from current Order state.
107. Historical Order state cannot be silently overwritten.
108. Important Order changes are auditable.
109. Audit records are immutable.
110. API responses contain only authorized data.
111. Order search remains Business/Branch scoped.
112. Pagination remains bounded.
113. POS payloads remain optimized for operational performance.
114. Large historical data is not unnecessarily returned in normal POS responses.
115. POS API performance must remain within defined SLO targets.
116. Authorization must fail closed.
117. Cache failure must not create unauthorized Order access.
118. Cache failure must not create duplicate financial effects.
119. Database remains the authoritative transactional source.
120. API routes do not contain core Order business logic.
121. API routes do not directly modify PostgreSQL.
122. Order behavior is executed through Application use cases.
123. Domain invariants remain independent of HTTP.
124. API contracts must remain compatible with offline synchronization.
125. API changes must consider POS clients.
126. API changes must consider printer/event consumers.
127. API changes must consider financial APIs.
128. API changes must consider reporting.
129. Breaking POS API changes require explicit versioning or migration.
130. Contract tests are required for critical POS workflows.
131. Concurrency tests are required for critical Order operations.
132. Historical integrity tests are required for pricing and Recipe behavior.
133. Security isolation tests are required for Business and Branch boundaries.
134. Idempotency tests are required for retryable POS commands.
135. Offline synchronization tests are required for offline POS operations.
136. Current configuration cannot reinterpret historical Orders.
137. Current menu cannot reinterpret historical Order Items.
138. Current price cannot reinterpret historical financial values.
139. Current Recipe cannot reinterpret historical inventory effects.
140. Current Set configuration cannot reinterpret historical Set Orders.
141. Order acceptance commits authoritative state before secondary effects are processed.
142. Secondary failures are observable without corrupting committed state.
143. Core POS operations must remain usable on ordinary Branch hardware.
144. POS performance optimization must not weaken security.
145. POS performance optimization must not weaken historical integrity.
146. POS performance optimization must not weaken Business isolation.
147. POS performance optimization must not weaken Branch isolation.
148. POS API must preserve the modular monolith application boundary.
149. Server-side state remains authoritative after synchronization.
150. POS API contracts must remain predictable for frontend and offline clients.

---

# 139. Recommended Implementation Structure

```text
backend/
└── app/
    └── api/
        └── v1/
            ├── pos/
            │   ├── routes.py
            │   └── schemas.py
            │
            └── orders/
                ├── routes.py
                ├── schemas.py
                └── responses.py
```

Application layer:

```text
app/
└── application/
    └── orders/
        ├── create_order.py
        ├── add_order_item.py
        ├── modify_order.py
        ├── remove_order_item.py
        ├── accept_order.py
        ├── cancel_order.py
        ├── change_order_status.py
        ├── change_item_status.py
        ├── assign_table.py
        └── update_delivery.py
```

Domain layer:

```text
app/
└── domain/
    └── orders/
        ├── entities/
        ├── value_objects/
        ├── services/
        ├── policies/
        └── state_machine/
```

The exact implementation structure may evolve without changing the public API contract.

---

# 140. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/14_Table_and_Waiter_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/06_Backend/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/14_API_Payment_Cash_and_Financial_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

---

# 141. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `13_API_POS_and_Order_Endpoints.md`

**Previous Document:** `12_API_CRUD_and_Command_Endpoint_Architecture.md`

**Next Document:** `14_API_Payment_Cash_and_Financial_Endpoints.md`

---

## Final Principle

> The POS API must make daily Order operations fast and predictable while keeping pricing, inventory, Order state, authorization, concurrency and historical integrity authoritative on the server.

