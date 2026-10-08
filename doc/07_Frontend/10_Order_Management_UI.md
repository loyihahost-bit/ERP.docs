# Order Management UI

**Document ID:** FA-10
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `09_POS_Frontend_Architecture.md`
**Next Document:** `11_Cash_Register_and_Cash_Session_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture and user interface behavior for Order Management in FastFood ERP.

Order Management covers the lifecycle of an Order after it is created in POS and before, during, and after its operational processing.

The UI must make the current Order state clear while preserving:

* financial integrity;
* historical integrity;
* permission boundaries;
* Branch isolation;
* Cash Session context;
* offline continuity;
* synchronization safety;
* item-level operational visibility.

The primary principle is:

> The Order UI must make the current state obvious without allowing the interface to rewrite authoritative historical or financial information.

---

# 2. Scope

This document covers:

* Order list;
* Order search;
* Order filters;
* Order details;
* Order lifecycle;
* Order status;
* item-level status;
* Order type;
* Hall/Dine-in;
* Takeaway;
* Phone Delivery;
* Order modification;
* item modification;
* quantity changes;
* extras;
* removals;
* discounts;
* custom markup;
* cancellation;
* payment state;
* refund state;
* correction;
* kitchen status;
* print state;
* offline Orders;
* synchronization;
* conflict handling;
* permissions;
* subscription restrictions;
* historical Order display;
* audit visibility;
* performance;
* accessibility.

---

# 3. Order Management Principle

The Frontend must distinguish between:

```text id="ord101"
Draft
Open
Accepted
Preparing
Ready
Completed
Paid
Cancelled
Refunded
Corrected
```

The exact lifecycle is determined by configured Order statuses and Backend rules.

The UI must not hard-code business assumptions where the system allows configurable statuses.

---

# 4. Order Identity

Every Order has a technical identity.

The Frontend may display:

* customer-facing Order number;
* Order UUID;
* local operation identifier where relevant.

The customer-facing number is for human interaction.

The technical UUID is used for reliable data identity.

---

# 5. Order Number

Example:

```text id="ord214"
Order #127
```

The number may follow Business/Cash Session numbering rules.

The Frontend must not use the displayed number as the primary technical identity.

---

# 6. Order List

The Order list should provide:

* Order number;
* time;
* Order type;
* Branch;
* employee/cashier where relevant;
* total;
* payment state;
* Order state;
* synchronization state where relevant.

Example:

```text id="ord325"
#127   14:32   Dine-in    85,000   Paid
#126   14:28   Takeaway   42,000   Preparing
#125   14:21   Delivery   96,000   Ready
```

---

# 7. Order List Scope

Order data must respect:

* Business scope;
* Branch scope;
* employee permissions;
* selected date/period;
* subscription state.

The Frontend must never rely only on client-side filtering for authorization.

---

# 8. Order Search

Search may support:

* Order number;
* phone number where permitted;
* address where permitted;
* Product name;
* relevant employee;
* other authorized identifiers.

Sensitive information must not be unnecessarily searchable.

---

# 9. Order Search Performance

Target:

**Normal Order list/search p95 ≤300 ms** after the required API response is available.

Complex historical searches may have a higher target but should provide loading feedback.

---

# 10. Order Filters

Common filters:

```text id="ord436"
Date
Branch
Order Type
Order Status
Payment Status
Cashier
Table
Synchronization State
```

Only authorized filters should be displayed.

---

# 11. Date Filters

The UI should support:

* today;
* yesterday;
* custom period;
* configured report periods where applicable.

Business/Branch timezone must be used for user-facing dates.

---

# 12. Order Detail

The Order detail page should present:

```text id="ord547"
Order Header
Order Type / Table / Delivery
Order Status
Order Items
Financial Summary
Payment
Operational Status
Print Status
Audit / History
Actions
```

The exact sections depend on permissions and Order state.

---

# 13. Order Header

Example:

```text id="ord658"
Order #127
Dine-in
Table 12
Created 14:32
Cashier: Employee 104
Status: Preparing
```

---

# 14. Order Type

The UI must clearly identify:

* Hall/Dine-in;
* Takeaway;
* Phone Delivery.

Order type must not be inferred only from optional fields.

---

# 15. Dine-in Order

Dine-in Orders may display:

* Hall;
* Table;
* table state;
* waiter where applicable.

Example:

```text id="ord769"
Main Hall
Table 12
```

---

# 16. Takeaway Order

Takeaway Orders should display:

```text id="ord870"
Takeaway
```

No table should be implied.

---

# 17. Phone Delivery Order

Delivery Orders may display:

* phone;
* address.

Example:

```text id="ord981"
Phone
+998 XX XXX XX XX

Address
Chilonzor, ...
```

The current system does not require a permanent Customer entity.

---

# 18. Order Items

Each Order Item should show:

* Product;
* quantity;
* base price;
* modifications;
* extras;
* removals;
* discount where applicable;
* item total;
* item status.

Example:

```text id="ord192"
Lavash
2 × 28,000

+ Cheese
- Pickles

Item total:
66,000 UZS
```

---

# 19. Item-Level Status

The system may track status per Order Item.

Example:

```text id="ord203"
Lavash ×2     Preparing
Hotdog ×1     Ready
Burger ×1     Cancelled
```

This allows the UI to represent mixed kitchen states.

---

# 20. Status Configuration

Order statuses are configurable according to Business rules.

The Frontend should render configured statuses rather than assuming a fixed set of hard-coded states.

---

# 21. Status Display

Each status should have:

* text;
* semantic meaning;
* accessible indicator.

Color may be used, but color must not be the only signal.

---

# 22. Status Transitions

The Frontend may display available transitions based on current state and permission.

Example:

```text id="ord314"
Preparing

[Mark Ready]
```

The Backend validates whether the transition is actually allowed.

---

# 23. Invalid Transition

If the transition is rejected:

```text id="ord425"
Order status could not be changed.

The Order may have changed elsewhere.
Refresh and continue.
```

The UI should reconcile the current authoritative state.

---

# 24. Order State Refresh

Order details should support:

* manual refresh;
* automatic refresh where useful;
* event-driven update where available.

Real-time mechanisms must not create unnecessary POS load.

---

# 25. Order State Priority

Operational Order updates have higher priority than:

* dashboard refresh;
* historical analytics;
* report refresh;
* background UI updates.

---

# 26. Order Modification

Order modification may be available only when:

* Order state permits;
* employee has permission;
* Cash Session/business rules allow it;
* subscription allows modification;
* no blocking payment/refund state exists.

---

# 27. Modify Action

Example:

```text id="ord536"
[Modify Order]
```

The button should be hidden or disabled when modification is not permitted.

The Backend remains authoritative.

---

# 28. Product Addition

Adding a Product to an existing Order should follow the same Product/Recipe/Menu rules as normal POS Order creation.

The UI must not bypass:

* Product availability;
* Recipe requirements;
* Set requirements;
* inventory validation;
* price configuration.

---

# 29. Product Removal

Removing an item must preserve the historical integrity of the Order.

Depending on Order state, the operation may be represented as:

* modification;
* cancellation;
* correction.

The UI must use the appropriate business operation rather than simply deleting a database row.

---

# 30. Quantity Change

Changing quantity must preserve an auditable financial history.

Example:

```text id="ord647"
Before:
Lavash ×2

After:
Lavash ×3

Reason:
Customer requested one more
```

The exact reason requirement depends on configured business rules.

---

# 31. Item Modification

Item modifications may include:

* extras;
* removals;
* permitted options;
* recipe-related modifications.

The UI must clearly show the resulting price.

---

# 32. Historical Item Snapshot

An Order Item must preserve the applicable historical information.

The Frontend should display the snapshot returned by the Backend rather than reconstructing historical values from current Product configuration.

---

# 33. Price Snapshot

The Order Item price must remain stable after creation unless an explicit business operation creates a new financial state.

Current Product price must not silently rewrite an existing Order Item.

---

# 34. Current Price vs Historical Price

Example:

```text id="ord758"
Current Product Price:
35,000 UZS

Order #127 Item Price:
30,000 UZS
```

The UI must not treat the historical Order price as an error.

---

# 35. Discount

Discounts are separate financial adjustments.

Example:

```text id="ord869"
Subtotal       100,000
Discount         5,000
----------------------
Total            95,000
```

The UI must not modify the Product's configured base price when displaying a discount.

---

# 36. Discount Permission

Discount actions require permission.

The UI must not expose unauthorized discount controls as active actions.

---

# 37. Custom Markup

Where authorized, Order-level custom markup may be applied within the allowed:

**0%–100%**

range.

The resulting price must be captured by the authoritative transaction state.

---

# 38. Markup Display

Example:

```text id="ord970"
Last Purchase Cost
30,000 UZS

Markup
20%

Result
36,000 UZS
```

The Frontend must not independently become the financial authority.

---

# 39. Order Total

The Order detail UI should show:

```text id="ord181"
Subtotal
100,000 UZS

Discount
10,000 UZS

Other Adjustments
0 UZS

Total
90,000 UZS
```

The authoritative values come from the Backend.

---

# 40. Financial Precision

The Frontend must use centralized money formatting.

It must not use floating-point arithmetic for authoritative financial decisions.

---

# 41. Payment State

Payment state should be distinct from Order lifecycle state.

Example:

```text id="ord292"
Order Status: Completed
Payment Status: Paid
```

Possible payment states are defined by the payment architecture.

---

# 42. Payment Amount

The payment screen should use the authoritative current Order financial amount.

The Frontend must not independently recalculate a different payable amount.

---

# 43. Paid Order

After payment:

* ordinary editing is normally restricted;
* financial state becomes historical;
* refund/correction follows separate authorized workflows.

---

# 44. Paid Order UI

Example:

```text id="ord303"
Paid

Amount:
95,000 UZS

[View Payment]
[Refund]
```

Refund availability depends on permission and business rules.

---

# 45. Refund

Refund is not the same as editing an Order.

The UI should use a separate refund workflow.

---

# 46. Refund Reason

A refund workflow must capture a required reason where defined by Business/System Analysis.

Example:

```text id="ord414"
Refund reason:
Customer returned order

[Confirm Refund]
```

---

# 47. Refund Permission

Only authorized employees may initiate or approve refunds according to the permission model.

---

# 48. Refund History

Historical refund information should remain visible where the employee has permission.

Example:

```text id="ord525"
Refund
Amount: 30,000 UZS
Reason: Customer return
By: Employee 104
Time: 15:42
```

---

# 49. Cancellation

Cancellation is a distinct Order operation.

The UI should not represent cancellation as simple deletion.

---

# 50. Cancellation Reason

Where required, cancellation should request a reason.

Example:

```text id="ord636"
Cancel Order

Reason:
Customer cancelled

[Cancel Order]
```

---

# 51. Cancelled Order

A cancelled Order remains visible in historical records.

The UI should clearly display:

```text id="ord747"
Cancelled
```

---

# 52. Order Deletion

Normal Order deletion is prohibited for authoritative historical Orders.

The Frontend should not provide a generic Delete Order action for such records.

---

# 53. Correction

Correction is used for permitted historical/business corrections.

The UI must clearly distinguish:

```text id="ord858"
Modify
Cancel
Refund
Correction
```

These are not interchangeable actions.

---

# 54. Correction Reason

Corrections should require an appropriate reason/comment where defined.

Example:

```text id="ord969"
Correction reason:
Incorrect quantity entered

[Submit Correction]
```

---

# 55. Correction History

The UI should preserve a visible correction chain where authorized.

Example:

```text id="ord181"
Original
   ↓
Correction #1
   ↓
Correction #2
```

The original historical state must remain reconstructable.

---

# 56. Audit Information

Important Order changes should expose relevant audit context to authorized users:

* actor;
* time;
* operation;
* reason;
* Branch;
* device where relevant;
* previous state;
* new state.

---

# 57. Kitchen Status

Order details may display kitchen progress.

Example:

```text id="ord292"
Lavash ×2     Preparing
Burger ×1     Ready
```

The UI must support item-level state when configured.

---

# 58. Kitchen Completion

An Order may contain items in different states.

The Frontend must not assume that all items always move together.

---

# 59. Partial Readiness

Example:

```text id="ord303"
Order #127

Lavash ×2
Ready

Pizza ×1
Preparing
```

The UI should make the mixed state obvious.

---

# 60. Print State

The Order UI may show print state separately:

```text id="ord414"
Kitchen Print:
Printed

Customer Receipt:
Pending
```

Printing does not determine Order validity.

---

# 61. Printer Failure

If a print operation fails:

```text id="ord525"
Order accepted.

Kitchen print failed.

[Retry Print]
```

The Order must remain valid.

---

# 62. Order Timeline

Where useful, the detail page may provide a chronological timeline:

```text id="ord636"
14:32  Created
14:33  Accepted
14:34  Preparing
14:41  Ready
14:45  Paid
```

The timeline should use authoritative event/history data.

---

# 63. Order History

Order history should distinguish:

* lifecycle events;
* financial events;
* corrections;
* refunds;
* status changes;
* synchronization events where relevant.

---

# 64. Historical Integrity

Current configuration must not rewrite historical Order information.

The UI must display historical snapshots supplied by the authoritative data layer.

---

# 65. Order Detail after Product Deactivation

If a Product later becomes inactive:

```text id="ord747"
Burger
Status: Inactive Product
Historical Order Item
Price: 30,000 UZS
```

The historical Order remains intact.

---

# 66. Order Detail after Price Change

If the Product price changes:

```text id="ord858"
Current Product Price: 35,000
Historical Order Price: 30,000
```

No automatic historical recalculation is allowed.

---

# 67. Recipe History

If the Product Recipe changes after an Order:

* historical Order remains tied to its original transaction state;
* current Recipe must not rewrite historical Order information.

Where inventory history is shown, the applicable Recipe Version should be displayed.

---

# 68. Set History

Historical Set Orders must retain:

* Set identity;
* Set configuration/version where applicable;
* Set price;
* relevant transaction state.

Current Set composition must not rewrite historical sales.

---

# 69. Branch Scope

Order data must always remain Branch-scoped where applicable.

A Branch user must not see another Branch's Orders unless permission explicitly grants cross-Branch visibility.

---

# 70. Business Scope

Cross-Business Order access is prohibited.

The Frontend must not rely on hidden UI alone for isolation.

---

# 71. Branch Switch

When Branch context changes:

* current Order context must be validated;
* Branch-specific Order data must reload;
* previous Branch Orders must not remain visible;
* Branch-specific permissions must recalculate.

---

# 72. Active Order During Branch Switch

If an active unsaved Order exists:

```text id="ord969"
You have an unfinished Order.

Switching Branch may discard or preserve it according to the current workflow.
```

The UI must protect user work.

An active Cash Session should prevent unsafe Branch switching where required.

---

# 73. Employee Scope

Order visibility and actions depend on:

* Employee status;
* Role Permission;
* Employee Override;
* Branch Scope;
* Subscription Entitlement;
* Order state.

---

# 74. Manager Permissions

A Manager may only modify Orders within the authority granted by the Owner/business permission model.

The UI must not allow the Manager to grant themselves additional Order permissions.

---

# 75. Read-Only Subscription

When the Business is READ_ONLY:

* historical Orders remain viewable;
* allowed reports remain available;
* modifications are blocked;
* refunds/corrections follow subscription restrictions;
* exports remain available where permitted.

---

# 76. Offline Order List

Offline mode may display locally cached Orders.

The UI must clearly identify potentially stale data.

Example:

```text id="ord181"
Offline data
Last synchronized:
10:32
```

---

# 77. Offline Order Creation

New offline Orders must be clearly marked:

```text id="ord292"
Pending synchronization
```

until server synchronization confirms them.

---

# 78. Offline Modification

Offline modification is allowed only where supported by the offline authorization/business rules.

The UI must not present unsupported operations as available.

---

# 79. Offline Cancellation

Offline cancellation follows the same restriction.

If unsupported:

```text id="ord303"
Cancellation requires an online connection.
```

---

# 80. Offline Payment State

The UI must clearly distinguish:

```text id="ord414"
Locally recorded
```

from:

```text
Server confirmed
```

where the payment architecture requires such distinction.

---

# 81. Synchronization

Order synchronization states may include:

```text id="ord525"
Pending
Syncing
Synced
Conflict
Failed
```

---

# 82. Sync Conflict

If an Order changed both locally and on the server:

```text id="ord636"
Order conflict

The Order was changed elsewhere.
Review the current server state before continuing.
```

The Frontend must not silently choose last-write-wins for important Order state.

---

# 83. Duplicate Order Protection

The UI must protect against:

* double-click;
* repeated submit;
* network retry duplication;
* application restart during submission.

Operation UUID/idempotency remains the Backend authority.

---

# 84. Unknown Submission Result

If the request times out after submission:

```text id="ord747"
Order result is being verified.

Do not submit again.
```

The UI should reconcile the existing operation.

---

# 85. Order Refresh

When reconciliation succeeds:

```text id="ord858"
Order #127
Accepted
```

When no operation exists:

```text id="ord969"
Order was not accepted.
You may safely continue.
```

---

# 86. Order List Pagination

Large Order lists must use:

* cursor pagination where supported;
* bounded page sizes;
* server-side filtering;
* server-side sorting.

The Frontend should not load entire historical Order datasets.

---

# 87. Sorting

Common sorting:

* newest first;
* oldest first;
* total amount;
* status;
* payment state.

Sorting must be deterministic.

---

# 88. Infinite Scroll vs Pagination

Either may be used.

The choice should prioritize:

* predictable performance;
* accessibility;
* easy navigation;
* stable URL state;
* low memory usage.

---

# 89. URL State

Where appropriate, filters and selected Order may be represented in URL state.

URL values are navigation state only.

They are never authorization evidence.

---

# 90. Deep Links

A direct Order URL must validate:

1. Authentication;
2. Business context;
3. Branch scope;
4. permission;
5. Order existence;
6. subscription state where relevant.

---

# 91. Browser Back/Forward

Order navigation should support normal browser history.

Unsaved modifications must be protected.

---

# 92. Loading State

The Order UI should distinguish:

```text id="ord181"
Initial Loading
Refreshing
Submitting
Synchronizing
```

These states must not all appear as a generic spinner.

---

# 93. Empty State

Example:

```text id="ord292"
No Orders found.

Try changing the date or filters.
```

An empty result is not necessarily an error.

---

# 94. Error State

Example:

```text id="ord303"
Orders could not be loaded.

[Retry]
```

The UI should preserve current filters when retrying.

---

# 95. Partial Failure

If one secondary section fails:

```text id="ord414"
Order details loaded.

Audit history is temporarily unavailable.
[Retry]
```

The entire Order page should not necessarily become unusable.

---

# 96. Order Action Priority

Primary actions depend on Order state.

Examples:

```text id="ord525"
Open:
[Modify] [Accept]

Preparing:
[Mark Ready]

Ready:
[Complete]

Paid:
[Refund]
```

Only valid actions should be presented.

---

# 97. Action Visibility

The UI may:

* hide impossible actions;
* disable temporarily unavailable actions;
* explain why a relevant action is unavailable.

Backend authorization remains authoritative.

---

# 98. Action Confirmation

Confirmation is recommended for:

* cancellation;
* refund;
* destructive correction;
* clearing modifications.

Routine status transitions should not require unnecessary confirmation.

---

# 99. Order Detail Performance

Target:

**Normal Order detail render p95 ≤500 ms after required API response.**

Heavy history should load separately when possible.

---

# 100. Order List Performance

Target:

**Normal Order list/filter interaction p95 ≤300 ms** after required API response.

---

# 101. Order Action Feedback

Target:

**Local Order action feedback p95 ≤100 ms.**

The UI should immediately reflect:

```text
Submitting…
Processing…
Refreshing…
```

without pretending the operation succeeded.

---

# 102. Synchronization UI

Target:

**Synchronization state visible to the user within ≤2 seconds** after an authoritative synchronization event is available to the Frontend.

---

# 103. Fatal Error Target

Target:

**Order Management fatal frontend error rate <0.1% of sessions.**

---

# 104. Accessibility

Order Management must support:

* keyboard navigation;
* semantic controls;
* visible focus;
* screen-reader labels;
* accessible status indicators;
* non-color state representation;
* readable financial values;
* accessible tables;
* reduced motion.

---

# 105. Financial Accessibility

Financial values should not depend only on color.

Example:

```text
Paid
95,000 UZS
```

rather than only a green badge.

---

# 106. Status Accessibility

A status should include text.

Example:

```text
● Preparing
```

not only a colored dot.

---

# 107. Order Table Accessibility

Order lists should provide:

* column headers;
* meaningful row labels;
* keyboard navigation;
* accessible action names;
* pagination state.

---

# 108. Mobile Behavior

The Order UI should remain usable on smaller screens.

Recommended mobile order:

```text
Order Header
Status
Financial Summary
Items
Primary Actions
History
Secondary Information
```

---

# 109. Desktop Behavior

Desktop can provide:

* wider Order list;
* side-by-side detail;
* persistent filters;
* richer item-level status display.

---

# 110. POS Integration

POS creates and updates Orders through the shared Order application/API layer.

The Order Management UI must not duplicate POS business rules.

---

# 111. Shared Order Model

POS and Order Management should use the same conceptual Order model.

Differences should be presentation/workflow differences, not conflicting business definitions.

---

# 112. State Ownership

Order state ownership:

```text id="ord636"
Backend
  ↓
API/Data Layer
  ↓
Order State
  ↓
UI
```

The UI cannot become the source of truth.

---

# 113. Optimistic UI

Optimistic UI may be used for low-risk visual interactions.

It must be used carefully for:

* financial changes;
* status changes;
* cancellation;
* refunds;
* corrections.

When authoritative response conflicts with optimistic state, the authoritative result wins.

---

# 114. Order Cache

Cached Order data may improve performance.

Cache must include appropriate:

* Business scope;
* Branch scope;
* permissions;
* Order identity;
* configuration/version where relevant.

Cache is non-authoritative.

---

# 115. Cache Invalidation

Order cache should be invalidated or refreshed after:

* Order modification;
* status change;
* payment;
* refund;
* correction;
* synchronization;
* Branch switch.

---

# 116. Notification Integration

The Order UI may receive notifications for:

* Order status changes;
* kitchen readiness;
* payment issues;
* synchronization conflicts;
* correction requests.

Notifications do not replace Order state.

---

# 117. Audit Integration

Audit data is accessed through the Audit/History architecture.

The Order UI should not reconstruct audit records from ordinary Order fields.

---

# 118. Security Logging

Security events such as unauthorized access attempts are handled by the security subsystem.

They should not be mixed with ordinary Order history.

---

# 119. Order Component Structure

Recommended:

```text id="ord747"
src/
└── features/
    └── orders/
        ├── components/
        │   ├── OrderList.*
        │   ├── OrderFilters.*
        │   ├── OrderSearch.*
        │   ├── OrderTable.*
        │   ├── OrderHeader.*
        │   ├── OrderItems.*
        │   ├── OrderItem.*
        │   ├── OrderStatus.*
        │   ├── OrderTimeline.*
        │   ├── OrderFinancialSummary.*
        │   ├── OrderActions.*
        │   ├── OrderHistory.*
        │   ├── RefundDialog.*
        │   ├── CancellationDialog.*
        │   └── CorrectionDialog.*
        ├── queries/
        ├── mutations/
        ├── selectors/
        ├── validation/
        ├── permissions/
        ├── offline/
        ├── synchronization/
        └── types.*
```

---

# 120. Dependency Rules

Order UI components may depend on:

```text id="ord858"
Order Feature
   ↓
Application/API/Data Layer
   ↓
Backend
```

They must not directly access:

* database;
* inventory repository;
* payment database;
* Cash Session database;
* audit database.

---

# 121. Order Business Logic Boundary

Frontend logic may handle:

* presentation;
* input validation;
* local state;
* interaction state;
* navigation;
* optimistic visual state.

Backend remains authoritative for:

* Order lifecycle;
* financial totals;
* inventory;
* permissions;
* payment;
* refund;
* correction;
* historical state.

---

# 122. Order Management Testing

Tests should cover:

### List

* filters;
* search;
* pagination;
* Branch isolation;
* Business isolation.

### Detail

* items;
* prices;
* statuses;
* financial state;
* history.

### Modification

* quantity;
* add/remove;
* extras;
* discount;
* markup.

### Lifecycle

* status transitions;
* cancellation;
* completion;
* payment.

### Financial

* refund;
* correction;
* historical price.

### Offline

* local Order;
* synchronization;
* conflict;
* recovery.

### Security

* unauthorized actions;
* inactive employee;
* read-only subscription;
* Branch switching.

---

# 123. Performance Testing

Performance tests should include:

* large Order lists;
* many Order Items;
* frequent status updates;
* rapid filtering;
* concurrent synchronization;
* slow network;
* repeated action clicks;
* large historical datasets.

---

# 124. Observability

The Frontend should measure:

* Order list latency;
* search latency;
* detail render latency;
* action feedback latency;
* submission latency;
* synchronization latency;
* error rate;
* conflict rate;
* duplicate submission prevention.

---

# 125. Telemetry Privacy

Telemetry must avoid unnecessary:

* phone numbers;
* delivery addresses;
* payment secrets;
* sensitive personal information;
* full financial payloads.

Use identifiers and technical metadata where possible.

---

# 126. Order Management Invariants

The following invariants apply:

1. Every Order belongs to exactly one Business.
2. Branch-scoped Orders remain within their Branch.
3. Cross-Business Order access is prohibited.
4. Cross-Branch access requires explicit authority.
5. Customer-facing Order number is not the technical Order identity.
6. Order UUID remains stable.
7. Local operation UUID remains distinct from Order number.
8. Order lifecycle is Backend-authoritative.
9. Configured Order statuses are not silently replaced by hard-coded frontend assumptions.
10. Invalid status transitions are rejected.
11. Existing historical Orders remain viewable where authorized.
12. Historical Order data is not rewritten by current configuration.
13. Historical prices remain immutable snapshots.
14. Current Product price cannot rewrite historical Order Item price.
15. Current Recipe cannot rewrite historical Order data.
16. Current Set configuration cannot rewrite historical Set Orders.
17. Order modification is permission-controlled.
18. Order cancellation is permission-controlled.
19. Refund is permission-controlled.
20. Correction is permission-controlled.
21. Discount is permission-controlled.
22. Custom markup is permission-controlled.
23. Custom markup is limited to 0–100%.
24. Discounts remain separate from base Product pricing.
25. Payment state is separate from Order lifecycle state.
26. Payment success must be Backend-confirmed.
27. Payment failure must not be shown as success.
28. Refund is not equivalent to Order editing.
29. Cancellation is not equivalent to deletion.
30. Historical Orders must not be physically deleted through normal UI operations.
31. Correction preserves historical traceability.
32. Correction requires reason where configured.
33. Refund requires reason where configured.
34. Cancellation requires reason where configured.
35. Order item quantity changes remain auditable where required.
36. Item-level status may differ between items.
37. Mixed item statuses must remain visible.
38. Product deactivation does not remove historical Order Items.
39. Product price changes do not rewrite existing Order Items.
40. Branch switching recalculates Order access.
41. Business switching clears incompatible Order state.
42. Active Cart state must be protected during context changes.
43. Cash Session state remains explicit where required.
44. Order operations cannot bypass Cash Session rules.
45. Read-only subscription blocks unauthorized modifications.
46. Historical viewing remains available where subscription permits.
47. Offline Orders are visibly distinguishable from server-confirmed Orders.
48. Offline data may be stale.
49. Offline state does not grant additional authority.
50. Offline cancellation follows offline authorization rules.
51. Offline modification follows offline authorization rules.
52. Synchronization state remains visible.
53. Synchronization conflicts are explicit.
54. Important Order conflicts are not silently resolved by last-write-wins.
55. Duplicate Order submission is prevented.
56. Duplicate actions cannot create duplicate authoritative transactions.
57. Unknown submission results are reconciled.
58. Non-idempotent operations are not blindly retried.
59. Order list pagination is bounded.
60. Historical datasets are not loaded unnecessarily.
61. Server-side filtering is used for large datasets.
62. Search respects Business and Branch scope.
63. Search does not expose unauthorized sensitive information.
64. Deep links validate authorization.
65. URL identifiers are not authorization evidence.
66. Browser navigation does not bypass access checks.
67. Loading states distinguish initial loading from mutation.
68. Empty results are not treated as errors.
69. Partial secondary failures do not necessarily block the whole page.
70. Financial values use centralized formatting.
71. Frontend does not become financial authority.
72. Frontend does not become inventory authority.
73. Frontend does not become payment authority.
74. Frontend does not become authorization authority.
75. Frontend does not become audit authority.
76. Order cache is non-authoritative.
77. Cache keys preserve Business isolation.
78. Cache keys preserve Branch isolation.
79. Cache invalidation occurs after relevant state changes.
80. POS and Order Management use compatible Order concepts.
81. Order Management does not duplicate conflicting business rules.
82. Order history is loaded through the appropriate history architecture.
83. Security events remain separate from ordinary Order history.
84. Printer failure does not invalidate an accepted Order.
85. Print status is separate from Order status.
86. Kitchen status is separate from payment state.
87. Payment state is separate from print state.
88. Order state is separate from synchronization state.
89. Order state is separate from UI loading state.
90. Accessibility does not depend only on color.
91. Statuses have textual representation.
92. Critical financial values remain readable.
93. Keyboard navigation is supported.
94. Screen reader state is meaningful.
95. Reduced motion is respected.
96. User work is protected during navigation.
97. Destructive actions are confirmed where appropriate.
98. Routine operations avoid unnecessary confirmation.
99. Error messages explain cause and recovery.
100. Technical error codes are not the primary user message.
101. Sensitive data is not unnecessarily logged.
102. Order Management remains responsive on ordinary hardware.
103. Normal Order detail render targets p95 ≤500 ms after required API response.
104. Normal Order list/filter targets p95 ≤300 ms after required API response.
105. Local Order action feedback targets p95 ≤100 ms.
106. Synchronization UI updates target ≤2 seconds after authoritative update availability.
107. Fatal Order Management frontend error rate target is <0.1% of sessions.
108. Background reporting does not block Order operations.
109. Dashboard updates do not block Order operations.
110. XLSX generation does not block Order operations.
111. Heavy history queries do not block routine Order interaction.
112. Historical integrity takes priority over UI convenience.
113. Security takes priority over client-side convenience.
114. Backend authoritative state wins over stale optimistic UI state.
115. Order identity remains reconstructable across synchronization.
116. Order history remains reconstructable after correction.
117. Order financial state remains reconstructable after refund.
118. Branch identity remains reconstructable.
119. Business identity remains reconstructable.
120. Order operations remain attributable to the responsible actor where required.
121. Device context is preserved where required.
122. Operation identity is preserved where required.
123. Order Management remains modular.
124. Feature components do not directly access persistence.
125. API/data access remains centralized.
126. Order Management supports future scaling without requiring premature complexity.

---

# 127. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`
* `docs/04_Architecture/07_Frontend/21_Frontend_API_and_Data_Layer.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
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

# 128. Status

**Document:** `10_Order_Management_UI.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `09_POS_Frontend_Architecture.md`

**Next Document:** `11_Cash_Register_and_Cash_Session_UI.md`

