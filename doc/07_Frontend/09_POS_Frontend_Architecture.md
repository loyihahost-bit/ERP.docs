# POS Frontend Architecture

**Document ID:** FA-09
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `08_Dashboard_Architecture.md`
**Next Document:** `10_Order_Management_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture for the FastFood ERP Point of Sale (POS).

POS is one of the most operationally critical parts of the system.

The POS must prioritize:

* speed;
* simplicity;
* reliability;
* clear operational state;
* keyboard/touch usability;
* offline continuity;
* safe financial behavior;
* minimal unnecessary interaction.

The primary principle is:

> POS should make routine operations fast and predictable without weakening security, authorization, auditability or financial integrity.

---

# 2. POS Scope

The POS Frontend covers:

* Order creation;
* Order type selection;
* Product search;
* Product selection;
* Product categories;
* Cart;
* Quantity changes;
* Recipe-driven modifications;
* Extras/additions;
* removals;
* custom markup where authorized;
* discounts where authorized;
* table/hall selection;
* takeaway;
* phone delivery;
* Order submission;
* Order state visibility;
* payment initiation;
* Cash Session context;
* offline Order creation;
* synchronization state;
* operational errors.

Payment processing itself remains governed by the payment architecture.

---

# 3. POS Order Types

The current POS supports:

```text id="pos101"
Hall / Dine-in
Takeaway
Phone Delivery
```

Online ordering is outside the current scope.

---

# 4. POS Context

Every POS operation must have an explicit operational context:

```text id="pos214"
Business
   ↓
Branch
   ↓
Employee
   ↓
Trusted Device
   ↓
Cash Register
   ↓
Cash Session
```

Where required, the active Order is also associated with:

```text id="pos325"
Order
   ↓
Order Items
```

---

# 5. POS Screen Structure

Recommended desktop layout:

```text id="pos436"
┌─────────────────────────────────────────────────────────────┐
│ Business / Branch | Cash Session | Offline | User           │
├──────────────────────┬──────────────────────────────────────┤
│ Categories           │ Search                               │
│                      ├──────────────────────────────────────┤
│ Products             │ Product Grid                         │
│                      │                                      │
│                      │                                      │
├──────────────────────┴──────────────────────┬───────────────┤
│                                             │ Cart          │
│                                             │               │
│                                             │ Order Total   │
│                                             │ [Continue]    │
└─────────────────────────────────────────────┴───────────────┘
```

The exact visual layout follows the Design System.

---

# 6. POS Priority

The POS interaction hierarchy is:

```text id="pos547"
1. Current Order
2. Product Search
3. Product Selection
4. Quantity / Modification
5. Order Type
6. Payment / Submit
7. Secondary information
```

Secondary information must not visually dominate the current transaction.

---

# 7. POS Header

The POS header should display only operationally important information.

Recommended:

* Branch;
* Cash Register;
* Cash Session;
* employee;
* offline/sync state;
* notifications where relevant.

Example:

```text id="pos658"
Chilanzar
Register 1
Session #1042
Cashier: Ali
● Online
```

---

# 8. Business and Branch Visibility

Business and Branch context must remain visible.

The POS must never allow the cashier to operate without a known Branch context.

---

# 9. Cash Session Visibility

The active Cash Session should be visible when POS operations depend on it.

Example:

```text id="pos769"
Cash Session #1042
Open
```

If no valid Cash Session exists:

```text id="pos870"
Cash Session required

Open a Cash Session before accepting Orders.
```

The Backend remains authoritative.

---

# 10. POS Entry Guard

Before allowing operational Order creation, the Frontend should verify the locally known state of:

* authentication;
* employee status;
* Business;
* Branch;
* device;
* permission;
* subscription;
* Cash Session;
* offline authorization where applicable.

The Backend performs authoritative validation again.

---

# 11. Product Categories

Categories should provide fast navigation.

Example:

```text id="pos981"
[Burgers] [Lavash] [Pizza] [Drinks] [Desserts]
```

Category navigation should not require full-page navigation.

---

# 12. Product Grid

Products should be displayed as large, touch-friendly controls.

A product card may contain:

```text id="pos192"
[Image]

Burger
30,000 UZS

Available
```

Where useful, show:

* name;
* price;
* image;
* availability;
* short indicator.

---

# 13. Product Availability

The UI may distinguish:

```text id="pos203"
Available
Out of Stock
Inactive
Temporarily Unavailable
Recipe Unavailable
```

The final sellability decision is Backend-authoritative.

---

# 14. Out-of-Stock Product

An out-of-stock product should normally not be selectable for a new Order.

Possible UI:

```text id="pos314"
Burger
Out of stock
```

The exact interaction depends on product policy.

---

# 15. Inactive Product

An inactive Product must not be newly added to an Order.

Historical Orders may continue displaying the Product.

---

# 16. Equipment Unavailability

A Product may be temporarily unavailable because equipment is unavailable.

The UI should show an operational state rather than implying that the Product was deleted.

---

# 17. Product Search

Product search is a critical POS interaction.

Requirements:

* fast;
* keyboard-friendly;
* touch-friendly;
* prefix/partial search where supported;
* category-aware;
* Branch-aware;
* permission-aware.

---

# 18. Search Input

The search field should be easy to focus.

Example:

```text id="pos425"
Search product...
```

Keyboard shortcut may focus search.

Recommended shortcut:

```text
/
```

provided the current control is not an editable field.

---

# 19. Search Performance

Target:

**Product search p95 ≤150 ms** for locally available/cached search data.

The user should receive immediate feedback even when server requests are involved.

---

# 20. Search Debouncing

Remote search should use bounded debouncing where necessary.

The Frontend must avoid sending one API request for every keystroke when local search or a short debounce can safely reduce traffic.

---

# 21. Search Results

Search results should contain enough information to identify the Product quickly.

Example:

```text id="pos536"
Burger Chicken
30,000 UZS
Available
```

Avoid excessive metadata.

---

# 22. Barcode / Scanner Support

If barcode input is supported later, the POS architecture should allow keyboard-like scanner input.

The scanner must not require a separate business workflow.

This feature remains optional unless explicitly enabled.

---

# 23. Product Selection

Selecting a Product should provide immediate local UI feedback.

Target:

**POS local interaction feedback p95 ≤100 ms.**

The Product should appear in the current Cart without unnecessary navigation.

---

# 24. Cart

The Cart is the central POS state.

Example:

```text id="pos647"
Burger Chicken
2 × 30,000
60,000

Lavash
1 × 28,000
28,000

----------------
Total
88,000 UZS
```

---

# 25. Cart Item

A Cart Item should support:

* Product name;
* quantity;
* applicable price;
* item total;
* modifications;
* extras;
* removals;
* validation state.

---

# 26. Quantity Changes

Quantity controls should be large and easy to operate.

Example:

```text id="pos758"
[-] 2 [+]
```

The Frontend may update the visual quantity immediately.

Authoritative inventory validation occurs through the appropriate application/API operation.

---

# 27. Quantity Validation

The Frontend may prevent obviously invalid input.

Examples:

* quantity ≤0;
* invalid numeric format;
* unreasonable maximum.

Backend validation remains authoritative.

---

# 28. Recipe-Based Modification

For products with Recipes, the POS may expose relevant components when the user chooses Modify.

Example:

```text id="pos869"
Burger

Components
✓ Meat
✓ Sauce
✓ Cheese

Extras
+ Cheese
+ Sauce

Remove
- Pickles
```

The actual available modifications follow Product/Recipe rules.

---

# 29. Additions

An authorized modification may add an extra component.

The UI must clearly show any price effect.

Example:

```text id="pos970"
+ Cheese
+5,000 UZS
```

---

# 30. Removals

Removing a component should clearly show:

```text id="pos181"
- Pickles
0 UZS
```

The operation must not silently modify unrelated components.

---

# 31. Modification Price

The Cart should display the resulting item price after valid modifications.

Example:

```text id="pos292"
Burger
30,000
+ Cheese
5,000

Item Total
35,000 UZS
```

---

# 32. Combo / Set

Set Products have their own configured selling price.

The POS should display the Set as a distinct product.

Component substitution is not allowed during normal sale.

---

# 33. Set Availability

A Set may be added only when required components are operationally available.

The UI should provide a clear explanation when a Set cannot be sold.

Example:

```text id="pos303"
Set unavailable

Chicken component is unavailable.
```

---

# 34. Custom Markup

Authorized users may use custom markup within:

**0%–100%.**

The POS UI should not expose the control to unauthorized employees.

---

# 35. Markup Display

Example:

```text id="pos414"
Custom Markup

Markup: 20%

Calculated Price:
36,000 UZS
```

The Frontend displays the calculated result supplied by or validated through the Backend.

---

# 36. Markup Validation

The UI must reject:

* negative markup;
* markup >100%;
* invalid Product;
* unavailable cost;
* unauthorized action.

Backend validation remains authoritative.

---

# 37. Discounts

Discounts are separate from Product pricing.

The POS should display:

```text id="pos525"
Subtotal
100,000 UZS

Discount
10,000 UZS

Total
90,000 UZS
```

The Product base price must remain visible where appropriate.

---

# 38. Discount Permission

Discount controls must be permission-aware.

Unauthorized employees should not receive an apparently usable discount action.

Backend authorization remains authoritative.

---

# 39. Order Type Selection

Order type should be selected early enough to determine the correct workflow.

Example:

```text id="pos636"
[Hall]
[Takeaway]
[Phone Delivery]
```

---

# 40. Hall / Dine-in

For Hall orders, the POS may require:

* Hall;
* Table.

Example:

```text id="pos747"
Hall
Main Hall

Table
12
```

Only Branch-authorized table data may be shown.

---

# 41. Table Status

Tables may show:

```text id="pos858"
Available
Busy
Waiting
```

The exact statuses follow the Table/Order architecture.

---

# 42. Busy Table

The UI should prevent conflicting use of a table where the Backend indicates that it is unavailable.

The Frontend must not assume local table availability is authoritative.

---

# 43. Takeaway

Takeaway Orders should provide a simplified workflow.

No customer record is required in the current scope.

---

# 44. Phone Delivery

Phone Delivery may capture:

* phone number;
* address.

Example:

```text id="pos969"
Phone
+998 XX XXX XX XX

Address
...
```

A permanent customer profile is not required in the current scope.

---

# 45. Delivery Validation

The Frontend may validate:

* required phone number;
* required address;
* basic input format.

Backend validation remains authoritative.

---

# 46. Order Notes

Where permitted, the cashier may add an Order note.

Notes must not be used to bypass structured Product modifications or financial rules.

---

# 47. Cart Persistence

During active POS use, the Cart may be kept in local memory/state.

For offline operation, durable local persistence may be required.

The local Cart must be associated with:

* Business;
* Branch;
* employee/device context where applicable;
* local Order UUID.

---

# 48. Cart Recovery

If the browser/application is refreshed during an unfinished transaction, the system should attempt safe recovery where supported.

Recovered state must not create a duplicate Order.

---

# 49. Local Order UUID

Every locally created Order must have a unique client-side UUID/operation identity according to the synchronization architecture.

Example:

```text id="pos181"
local_order_id:
550e8400-e29b-41d4-a716-446655440000
```

The Frontend must not use a human-facing Order number as the idempotency identifier.

---

# 50. Duplicate Prevention

Repeated submission must not create duplicate Orders.

The Frontend should:

* disable duplicate submit while processing;
* preserve operation identity;
* show current submission state;
* reconcile server response.

The Backend remains the final idempotency authority.

---

# 51. Submit Order

Recommended workflow:

```text id="pos292"
Cart
  ↓
Validate local state
  ↓
Submit Order command
  ↓
Backend validation
  ↓
Order accepted
  ↓
Show authoritative Order state
```

---

# 52. Order Submission Feedback

The UI should immediately show:

```text id="pos303"
Submitting…
```

After success:

```text id="pos414"
Order #10482 created
```

After failure:

```text id="pos525"
Order could not be accepted.

Reason:
Insufficient inventory.
```

---

# 53. Order Acceptance Errors

Common errors include:

* unauthorized;
* inactive Product;
* insufficient inventory;
* invalid Recipe;
* invalid Set;
* inactive Branch;
* closed Cash Session;
* subscription restriction;
* stale configuration;
* synchronization conflict.

Each should have a user-understandable message.

---

# 54. Inventory Failure

If inventory validation fails:

```text id="pos636"
Unable to accept Order.

Chicken:
required 2 kg
available 1 kg
```

The exact quantity information should only be shown if authorized and useful.

---

# 55. Price Conflict

If the local configuration is stale:

```text id="pos747"
Product price has changed.

Refresh the current configuration before continuing.
```

The Frontend must not silently replace an existing Cart price without user-visible handling.

---

# 56. Configuration Version

The POS should associate local product/pricing state with its configuration version.

Conceptually:

```text id="pos858"
Product
+
Price
+
Configuration Version
```

This supports deterministic synchronization and conflict handling.

---

# 57. Existing Cart and Price Changes

If a price changes after a Product was added to the Cart:

* the current Cart Item retains its captured price;
* new Product additions use the new effective configuration;
* the UI must not silently recalculate the existing item.

---

# 58. Existing Open Order

If an existing Order remains open:

* its item price snapshots remain authoritative;
* current Product price must not rewrite the Order;
* the POS should render the existing Order from authoritative Order state.

---

# 59. Payment Transition

The POS may move the Order into payment flow after successful Order creation/acceptance.

The payment workflow is defined by the Payment architecture.

The POS should not implement independent payment truth.

---

# 60. Payment Button

Example:

```text id="pos969"
Subtotal       100,000
Discount         5,000
----------------------
Total            95,000

[Proceed to Payment]
```

The displayed amount must come from the authoritative current Order financial state.

---

# 61. Payment Failure

If payment fails:

```text id="pos181"
Payment was not completed.

The Order remains in its current valid state.
```

The POS must not assume that payment succeeded because a local button was clicked.

---

# 62. Payment Success

After successful payment:

```text id="pos292"
Payment completed

Order #10482
Paid
```

The UI may then offer:

* receipt/print action;
* New Order;
* Order details.

Printing remains separate from payment transaction success.

---

# 63. Printer Independence

Order acceptance and payment must not depend on printer availability.

If printing fails:

```text id="pos303"
Order accepted.

Receipt printing failed.
[Retry Print]
```

The Order must remain accepted.

---

# 64. Print Status

The UI may show:

```text id="pos414"
Print:
Queued
Printing
Printed
Retrying
Failed
```

Printing state is separate from Order state.

---

# 65. Kitchen Receipt

When an Order reaches the relevant acceptance state, the system may create kitchen print jobs.

The Frontend should not wait for printer completion before treating the Order as accepted.

---

# 66. Offline POS

Trusted devices may continue core POS operations while offline within valid authorization bounds.

Offline POS may support:

* viewing locally available menu;
* creating Orders;
* modifying Orders;
* storing transaction operations;
* showing pending synchronization.

---

# 67. Offline Restrictions

Offline mode must not introduce new authority.

The device cannot:

* create a new trusted device;
* grant permissions;
* extend offline authorization;
* bypass subscription restrictions;
* access a newly authorized Branch;
* modify server-only configuration.

---

# 68. Offline Order Creation

Example:

```text id="pos525"
Offline

Order #Local-8A32
Pending synchronization
```

The UI must clearly distinguish local pending state from server-confirmed state.

---

# 69. Offline Order State

Recommended local states:

```text id="pos636"
DRAFT
PENDING_SYNC
SYNCING
SYNCED
CONFLICT
FAILED
```

The exact state machine follows synchronization architecture.

---

# 70. Offline Payment

Payment behavior while offline must follow the payment/business rules.

The Frontend must not assume that every payment method is available offline.

If offline payment is not supported for a method:

```text id="pos747"
This payment method is unavailable offline.
```

---

# 71. Offline Inventory

Offline inventory information may be stale.

The UI should distinguish:

```text id="pos858"
Available locally
Last synchronized
```

The Frontend must not present stale stock as guaranteed current server stock.

---

# 72. Offline Price

Offline POS uses the latest valid local price configuration.

The Frontend must not invent a new price when the server is unavailable.

---

# 73. Offline Configuration Version

Every offline-created transaction should retain the configuration version used locally where required.

---

# 74. Synchronization Priority

After reconnecting:

```text id="pos969"
Pending Transactions
        ↓
Transaction Synchronization
        ↓
Server Response
        ↓
Configuration Refresh
        ↓
Dashboard / Secondary Refresh
```

Transaction synchronization has priority over configuration refresh.

---

# 75. Sync Indicator

POS should always make pending synchronization understandable.

Example:

```text id="pos181"
● Offline
7 Orders pending sync
```

or:

```text id="pos292"
● Syncing
3 remaining
```

---

# 76. Sync Conflict

If an offline operation cannot be automatically accepted:

```text id="pos303"
Sync conflict

Order requires review.
```

The POS must not silently discard the local transaction.

---

# 77. POS Conflict Recovery

Conflict handling should provide:

* conflict identifier;
* affected Order;
* current state;
* required action;
* safe retry/review path.

The detailed workflow belongs to the synchronization UI architecture.

---

# 78. POS Keyboard Support

Keyboard support is important for desktop POS.

Recommended shortcuts may include:

```text id="pos414"
/
Focus search

Esc
Close active dialog

Enter
Confirm focused action

+
Increase quantity

-
Decrease quantity
```

Shortcuts must not interfere with text input.

---

# 79. Touch Support

Touch controls should provide sufficiently large targets.

Recommended:

* large Product buttons;
* large quantity controls;
* large primary action buttons;
* clear modal actions.

Avoid tiny icons for critical POS operations.

---

# 80. Mouse Support

The POS must remain fully usable with a mouse.

Touch support must not remove standard pointer interaction.

---

# 81. Product Image

Product images may improve recognition.

However:

* image loading must not block product selection;
* missing image must have a fallback;
* images must not dominate the screen;
* image changes do not change Product identity.

---

# 82. Product Grid Performance

Large Product menus should use:

* pagination;
* virtualization;
* bounded rendering;
* category filtering;
* local indexed search where appropriate.

The UI must avoid rendering hundreds of heavy image components unnecessarily.

---

# 83. POS Startup

Target:

**POS initial screen interactive p75 ≤2.0 seconds** under normal conditions.

Critical local state should load before secondary visual enhancements.

---

# 84. POS Local Interaction

Target:

**POS local interaction feedback p95 ≤100 ms.**

Examples:

* Product selected;
* quantity changed;
* category changed;
* Cart updated;
* modal opened.

---

# 85. POS API Latency

The Frontend should target:

**Core POS command p95 ≤500 ms** under normal network/backend conditions.

Longer operations should provide progress feedback.

---

# 86. POS Search Latency

Target:

**Product search p95 ≤150 ms** for local/cached search.

Remote search may use bounded loading indicators.

---

# 87. POS Rendering

Normal Cart and Product Grid rendering should remain responsive.

Heavy operations such as:

* report generation;
* XLSX export;
* historical analytics

must never run inside the POS rendering path.

---

# 88. POS Memory Usage

The POS should avoid unbounded in-memory growth.

The Frontend should:

* limit retained Orders;
* release unused image resources;
* paginate history;
* clean temporary operation state;
* bound offline queues according to synchronization policy.

---

# 89. POS Navigation

POS should minimize route changes.

Recommended:

```text id="pos636"
POS
 ├── Product selection
 ├── Cart
 ├── Modify
 ├── Order type
 └── Payment
```

These should preferably behave as focused states/panels rather than full-page navigation.

---

# 90. POS Dialogs

Dialogs should be used for:

* Product modification;
* discount;
* markup;
* table selection;
* confirmation;
* payment transition.

Avoid deep dialog nesting.

---

# 91. POS Confirmation

Confirmation should be used for operations with meaningful consequences.

Examples:

* clear Cart;
* remove important modification;
* cancel active workflow;
* switch Branch during active transaction.

Routine quantity changes should not require confirmation.

---

# 92. Cart Clearing

Clear Cart should be explicit:

```text id="pos747"
Clear current Order?

All unsaved items will be removed.

[Cancel] [Clear]
```

---

# 93. Draft Order

If draft Orders are supported locally:

```text id="pos858"
Draft
```

must be clearly distinguished from accepted Orders.

A draft must not appear as a server-confirmed Order.

---

# 94. Order Number

Customer-facing Order numbers may be displayed after authoritative creation.

The local UUID remains the technical identity.

The Frontend must not use the customer-facing number as idempotency identity.

---

# 95. Customer-Facing Number

The system may show:

```text id="pos969"
Order #127
```

The number may reset according to the Business/Cash Session rules.

The underlying database/order UUID remains separate.

---

# 96. POS Notifications

Important notifications may appear without interrupting the current Order where possible.

Example:

```text id="pos181"
Low stock:
Chicken
```

Critical security or operational events may require stronger attention.

---

# 97. Toasts

Toasts may communicate:

* successful local action;
* synchronization state;
* print result;
* non-blocking warnings.

Critical financial or destructive messages should not rely only on temporary toasts.

---

# 98. Error Message Design

POS errors should answer:

1. What happened?
2. Why?
3. What can the cashier do now?

Example:

```text id="pos292"
Order could not be accepted.

Chicken is out of stock.

Remove the item or wait for stock replenishment.
```

---

# 99. Error Codes

Technical error codes should remain available to logging/support layers but should not be the primary user-facing message.

Example:

```text id="pos303"
User message:
Product is unavailable.

Internal code:
PRODUCT_UNAVAILABLE
```

---

# 100. Security and POS Friction

Security must not unnecessarily interrupt normal POS operations.

Normal operations should not require repeated password entry.

Stronger verification may be required for:

* sensitive refunds;
* permission changes;
* configuration changes;
* device verification;
* privileged corrections.

---

# 101. Permission Changes During POS

If permissions change while the POS is open:

* new unauthorized actions must be blocked;
* existing valid Order state remains safe;
* the UI must refresh relevant permission state;
* Backend remains authoritative.

---

# 102. Employee Deactivation During POS

If the employee becomes inactive:

```text id="pos414"
Access has been disabled.

Current operations are being secured.
```

The application must follow authentication/session policy.

---

# 103. Subscription Expiry During POS

If subscription changes to READ_ONLY:

* existing valid state should not be corrupted;
* new modifying operations are blocked;
* viewing remains available where allowed;
* pending offline transactions follow synchronization/lifecycle rules.

---

# 104. Branch Deactivation During POS

If the active Branch becomes unavailable:

* new operations must be blocked;
* existing unsaved local state should be protected where possible;
* user should be directed to an authorized active Branch;
* Backend state remains authoritative.

---

# 105. Accessibility

POS must support:

* keyboard navigation;
* visible focus;
* semantic buttons;
* accessible labels;
* screen reader state;
* non-color status indicators;
* sufficient touch targets;
* reduced motion.

---

# 106. Screen Reader Considerations

Dynamic POS changes should announce important events:

```text id="pos525"
Product added to Order.
Quantity changed to 2.
Order submitted.
Payment completed.
```

Routine visual updates should not create excessive announcements.

---

# 107. Reduced Motion

POS animations must respect:

```text
prefers-reduced-motion
```

Animation must never be required to understand:

* price;
* Order state;
* payment state;
* synchronization state;
* errors.

---

# 108. State Architecture

POS state should be separated into:

```text id="pos636"
POS Context State
Order Draft State
Product Query State
Cart State
Modification State
Payment Transition State
Offline State
Synchronization State
UI State
```

---

# 109. Server State vs Local State

Server-authoritative data includes:

* Product configuration;
* prices;
* Order state;
* payment state;
* inventory result;
* Cash Session;
* permissions;
* subscription.

Local UI state includes:

* search input;
* selected category;
* modal visibility;
* temporary layout state.

The two categories must not be confused.

---

# 110. POS State Persistence

Safe local persistence may include:

* unfinished Cart;
* pending offline operations;
* synchronization queue;
* local menu snapshot;
* local pricing snapshot.

Sensitive state must use encrypted/trusted-device-bound storage according to security architecture.

---

# 111. POS Cache

POS cache may store:

* Product definitions;
* categories;
* menu;
* valid price configuration;
* approved local configuration;
* images;
* limited reference data.

Cache is not authoritative.

---

# 112. Cache Invalidation

POS configuration cache must be invalidated after:

* Branch switch;
* Business switch;
* configuration synchronization;
* permission changes;
* device revocation;
* subscription changes where relevant.

---

# 113. Product Search Cache

Search cache should be:

* Branch-aware;
* Business-aware;
* configuration-version-aware.

Example:

```text id="pos747"
business_id
+
branch_id
+
configuration_version
+
query
```

---

# 114. Duplicate Request Protection

The Frontend must prevent accidental repeated:

* Order submission;
* payment submission;
* discount application;
* correction submission.

The Backend remains the final idempotency authority.

---

# 115. Network Failure

If a request fails due to network interruption:

```text id="pos858"
Connection lost.

The system will retry safely where supported.
```

The UI must distinguish:

* request not sent;
* request pending;
* request succeeded;
* result unknown.

---

# 116. Unknown Result

A particularly important state is:

```text id="pos969"
Result unknown
```

For example, the network may fail after the server accepted an Order.

The Frontend must not blindly retry a non-idempotent operation.

It should reconcile using operation UUID/status query where supported.

---

# 117. Reconciliation

Recommended:

```text id="pos181"
Submit
  ↓
Timeout
  ↓
Unknown Result
  ↓
Check operation status
  ↓
Confirmed / Retry Safely / Conflict
```

---

# 118. POS Testing

Testing should cover:

### Product

* category;
* search;
* availability;
* selection.

### Cart

* add;
* remove;
* quantity;
* modifications;
* extras;
* discounts;
* markup.

### Orders

* Hall;
* Takeaway;
* Delivery;
* submission;
* duplicate prevention.

### Cash

* active session;
* closed session;
* Branch switching.

### Offline

* offline creation;
* local persistence;
* reconnect;
* synchronization;
* conflict.

### Security

* unauthorized actions;
* Branch isolation;
* Business isolation;
* subscription restrictions;
* device restrictions.

---

# 119. POS Performance Testing

Performance tests should include:

* large menu;
* hundreds of Products;
* rapid Product selection;
* rapid quantity changes;
* repeated search;
* simultaneous synchronization;
* slow network;
* temporary backend failure;
* ordinary POS hardware.

---

# 120. POS Observability

The Frontend should expose useful metrics such as:

* Product search latency;
* Cart interaction latency;
* Order submission latency;
* payment transition latency;
* synchronization latency;
* offline queue size;
* duplicate submission prevention;
* UI error rate;
* print status where integrated.

Sensitive business data must not be placed in telemetry unnecessarily.

---

# 121. POS Logging

Logs should contain technical context such as:

* request ID;
* operation ID;
* Business context where permitted;
* Branch context where permitted;
* device context;
* error code;
* timing.

Do not log:

* passwords;
* tokens;
* payment secrets;
* unnecessary personal data.

---

# 122. POS Module Structure

Recommended:

```text id="pos292"
src/
└── features/
    └── pos/
        ├── components/
        │   ├── PosShell.*
        │   ├── PosHeader.*
        │   ├── CategoryList.*
        │   ├── ProductGrid.*
        │   ├── ProductSearch.*
        │   ├── Cart.*
        │   ├── CartItem.*
        │   ├── ModifierDialog.*
        │   ├── OrderTypeSelector.*
        │   ├── TableSelector.*
        │   ├── DeliveryForm.*
        │   ├── DiscountDialog.*
        │   ├── MarkupDialog.*
        │   ├── PaymentTransition.*
        │   └── SyncIndicator.*
        ├── state/
        │   ├── cart.*
        │   ├── draft-order.*
        │   ├── pos-context.*
        │   └── ui.*
        ├── queries/
        ├── mutations/
        ├── selectors/
        ├── validation/
        ├── offline/
        └── types.*
```

Exact framework-specific file extensions remain implementation-defined.

---

# 123. Dependency Rules

POS components should depend on:

```text id="pos303"
POS Feature
   ↓
Application/API Layer
   ↓
Backend
```

POS components must not directly:

* access PostgreSQL;
* implement authorization;
* modify inventory;
* calculate authoritative financial state;
* communicate directly with printers as business authority.

---

# 124. Printer Integration Boundary

If the Frontend interacts with a local print agent:

```text id="pos414"
POS
 ↓
Backend / Print Job
 ↓
Print Agent
 ↓
Printer
```

The Frontend must not treat printer success as Order acceptance.

---

# 125. Business Logic Boundary

The Frontend may provide:

* input validation;
* visual calculations;
* optimistic interaction;
* presentation logic.

The Frontend must not become the authoritative source for:

* inventory deduction;
* payment completion;
* Cash Session state;
* discount authorization;
* final Order totals;
* historical financial state.

---

# 126. POS Navigation Guard

The POS should guard against accidental navigation when there is:

* unsaved Cart;
* active modification dialog;
* pending critical submission.

The guard should not prevent legitimate navigation when no user work would be lost.

---

# 127. POS Reset

After successful Order completion, the POS may reset the Cart:

```text id="pos525"
Current Order
      ↓
Completed
      ↓
New Empty Order
```

The reset must occur only after the authoritative state is known.

---

# 128. Multiple Orders

If the Business supports multiple simultaneously open Orders at the POS, each local draft must have independent identity.

The architecture should not assume only one in-memory Order forever.

However, the initial UI may optimize for one active Cart at a time.

---

# 129. POS Session Recovery

After application restart:

1. Authenticate/restore valid session.
2. Validate device.
3. Restore Business/Branch context.
4. Restore Cash Session context where valid.
5. Restore safe local Cart/pending operations.
6. Reconcile pending operations.
7. Continue normal POS.

---

# 130. POS and Cash Handover

During Cash Handover:

* new Order acceptance may be restricted according to Cash Session state;
* active Cart should be protected;
* the UI should clearly show handover state;
* no new Cash Session should be assumed until authoritative confirmation.

---

# 131. POS and Cash Session Close

When Cash Session is closing:

```text id="pos636"
Cash Session closing

Complete or safely preserve current Order before finalizing the session.
```

The exact blocking rules follow Cash Session architecture.

---

# 132. POS and Historical Orders

Historical Orders should be accessible through the Order module.

The POS should not load large historical datasets into the primary transaction screen.

---

# 133. POS and Reports

Reports must remain separate from the POS transaction path.

The POS may provide links to relevant reports but must not execute heavy report generation synchronously.

---

# 134. POS and Notifications

Operational notifications may appear in POS but must not unnecessarily interrupt transaction flow.

Examples:

* low stock;
* printer failure;
* synchronization warning;
* subscription warning.

Critical security events may require stronger handling.

---

# 135. POS Security Invariants

The POS must preserve:

1. Business isolation.
2. Branch isolation.
3. Employee authentication.
4. Permission enforcement.
5. Subscription enforcement.
6. Device trust.
7. Offline authorization.
8. Operation idempotency.
9. Historical financial integrity.
10. Server authority.

---

# 136. POS Invariants

The following invariants are mandatory:

1. POS always operates within a valid Business context.
2. POS always operates within a valid Branch context.
3. POS operational actions require valid employee authentication.
4. POS operational actions require applicable permission.
5. Backend remains authoritative.
6. Client UI is not a security boundary.
7. Unauthorized Products cannot be sold.
8. Inactive Products cannot be newly sold.
9. Out-of-stock Products cannot be accepted when inventory rules block sale.
10. Required Recipe conditions must be satisfied.
11. Required Set component availability must be satisfied.
12. Set component substitution is prohibited during normal sale.
13. Product selection must provide immediate local feedback.
14. Product search target is p95 ≤150 ms for local/cached search.
15. Local POS interaction target is p95 ≤100 ms.
16. POS initial interactive target is p75 ≤2.0 s.
17. Core POS command target is p95 ≤500 ms.
18. Product search is Branch-aware.
19. Product search is Business-aware.
20. Product search respects effective configuration.
21. Cart items retain captured applicable prices.
22. Current Product price cannot rewrite an existing Cart Item.
23. Current Product price cannot rewrite historical Order Items.
24. Discounts remain separate from Product base prices.
25. Custom markup is limited to 0–100%.
26. Custom markup does not change global Product price.
27. Order totals remain Backend-authoritative.
28. Payment state remains Backend-authoritative.
29. Printer success is not payment success.
30. Printer success is not Order acceptance.
31. Printer failure does not automatically roll back an accepted Order.
32. Order submission is idempotent.
33. Payment submission is idempotent where applicable.
34. Duplicate clicks cannot create duplicate authoritative operations.
35. Customer-facing Order number is not idempotency identity.
36. Local Order UUID is separate from human-facing Order number.
37. Network timeout does not automatically imply operation failure.
38. Unknown operation results must be reconciled safely.
39. Non-idempotent operations must not be blindly retried.
40. Offline transactions use valid local authorization.
41. Offline transactions use valid local configuration.
42. Offline transactions preserve configuration identity where required.
43. Offline mode cannot grant new permissions.
44. Offline mode cannot create new trusted devices.
45. Offline mode cannot extend authorization.
46. Offline mode cannot bypass subscription restrictions.
47. Offline mode cannot create new Branch access.
48. Offline inventory is clearly distinguished as potentially stale.
49. Offline pricing uses the latest valid local configuration.
50. Transaction synchronization has priority over configuration synchronization.
51. Sync conflicts are explicit.
52. Sync conflicts cannot silently discard local transactions.
53. Branch switching invalidates Branch-scoped POS state.
54. Business switching invalidates Business-scoped POS state.
55. Branch switching cannot silently detach an active Cash Session.
56. Active Cart must be protected during context changes.
57. Unsaved modifications must be protected.
58. Cash Register context remains explicit.
59. Cash Session context remains explicit.
60. POS cannot accept Orders without required Cash Session state.
61. Cash Session closure follows Backend rules.
62. Cash handover follows Backend rules.
63. POS does not independently implement Cash Session authority.
64. POS does not independently implement inventory authority.
65. POS does not independently implement payment authority.
66. POS does not independently implement authorization authority.
67. POS does not independently implement historical financial truth.
68. Menu state is configuration-version-aware.
69. Price state is configuration-version-aware.
70. Stale configuration is handled explicitly.
71. Existing Open Orders are not invalidated by unrelated price changes.
72. Existing Order Items retain their historical price snapshots.
73. Historical Orders retain their original financial state.
74. Payment failures do not imply Order deletion.
75. Payment failures do not imply payment success.
76. Cart clearing is explicit.
77. Destructive actions may require confirmation.
78. Routine POS operations should not require unnecessary confirmation.
79. Security must not create unnecessary friction for routine operations.
80. Sensitive operations may require stronger authentication.
81. Permission changes affect future unauthorized actions.
82. Employee deactivation affects active POS access.
83. Device revocation affects active POS access.
84. Subscription expiry affects modifying operations.
85. READ_ONLY state does not necessarily block viewing.
86. POS state remains reconstructable after application restart where supported.
87. Local persistent state is encrypted where required.
88. Local state is associated with the correct Business and Branch.
89. Cross-Business local state leakage is prohibited.
90. Cross-Branch local state leakage is prohibited.
91. Product images do not block critical interaction.
92. Product grid rendering remains bounded.
93. Search requests are bounded.
94. Background work does not block POS interaction.
95. Reports do not block POS interaction.
96. XLSX generation does not block POS interaction.
97. Notifications do not unnecessarily block Order creation.
98. Dashboard refresh does not block POS.
99. Synchronization does not block normal local POS interaction.
100. POS remains usable on ordinary POS hardware.
101. Keyboard interaction is supported.
102. Touch interaction is supported.
103. Mouse interaction is supported.
104. Keyboard shortcuts do not interfere with text input.
105. Drag-and-drop is never the only critical interaction method.
106. Accessibility is preserved.
107. Reduced motion is respected.
108. Color is not the only status signal.
109. Dynamic state changes are accessible.
110. Error messages explain what happened and what the user can do.
111. Technical error codes are not the primary user-facing explanation.
112. POS errors must not expose sensitive technical details.
113. Sensitive data is not unnecessarily logged.
114. Operation IDs are retained where required for reconciliation.
115. POS metrics must not expose unnecessary personal data.
116. POS architecture remains modular.
117. POS business logic remains outside presentation components.
118. Feature modules use centralized API/data boundaries.
119. POS does not access the database directly.
120. POS does not directly control authoritative printer state.
121. POS does not directly control authoritative Cash Session state.
122. POS does not directly control authoritative inventory state.
123. POS does not directly control authoritative payment state.
124. POS configuration cache is non-authoritative.
125. Cache keys preserve Business and Branch isolation.
126. Configuration invalidation is explicit.
127. Context switching remains deterministic.
128. POS session recovery follows authentication and device validation.
129. Historical integrity takes priority over UI convenience.
130. Security takes priority over client-side convenience.
131. Correctness takes priority over optimistic visual state when authoritative results conflict.
132. POS must remain fast without weakening correctness.
133. POS must remain simple without hiding important state.
134. POS must remain reliable during temporary network failure.
135. POS must preserve transaction identity across retries.
136. POS must preserve transaction history across synchronization.
137. POS must preserve Branch identity across synchronization.
138. POS must preserve Business identity across synchronization.
139. POS must not silently change transaction meaning.
140. POS architecture must support future scaling without requiring immediate complexity.

---

# 137. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`
* `docs/04_Architecture/07_Frontend/21_Frontend_API_and_Data_Layer.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_Caching_and_Performance.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_Security.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

---

# 138. Status

**Document:** `09_POS_Frontend_Architecture.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `08_Dashboard_Architecture.md`

**Next Document:** `10_Order_Management_UI.md`

