# Menu and Pricing UI

**Document ID:** FA-14
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `13_Products_Recipes_and_Sets_UI.md`
**Next Document:** `15_Attendance_and_Payroll_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture and user interface behavior for Business-level Menu configuration, Branch Menu availability, Product pricing, Branch price overrides, discounts, custom markup and related configuration workflows.

The main principle is:

> Menu and pricing UI must make configuration simple while preserving Branch isolation, price history and transaction integrity.

The Frontend must never treat the current menu or current price as a replacement for historical transaction data.

---

# 2. Scope

This document covers:

* Global Menu;
* Branch Menu;
* Product availability;
* Product activation;
* categories;
* standard Product price;
* Branch price override;
* price configuration;
* effective configuration;
* Cash Session boundary;
* Order price snapshot;
* discounts;
* custom markup;
* Set pricing;
* Recipe dependency;
* equipment availability;
* configuration versions;
* approval;
* concurrency;
* offline configuration;
* synchronization;
* conflicts;
* audit;
* subscription restrictions;
* historical integrity;
* accessibility;
* performance.

---

# 3. Menu Hierarchy

The Frontend must represent Menu configuration using:

```text id="mnv101"
Business
   ↓
Global Menu
   ↓
Branch Menu
   ↓
POS Availability
```

Global Product configuration is Business-scoped.

Branch availability is Branch-scoped.

---

# 4. Global Menu

Global Menu represents the Business-level commercial catalog.

The Global Menu may contain:

* Product;
* category;
* standard price;
* active state;
* image;
* Product configuration.

Creating a Product globally does not automatically make it available at every Branch.

---

# 5. Branch Menu

Branch Menu determines whether a Business Product is operationally available at a specific Branch.

Example:

```text id="mnv202"
Burger

Branch A → ACTIVE
Branch B → INACTIVE
Branch C → ACTIVE
```

Changing Branch B must not modify Branch A or Branch C.

---

# 6. Menu Context

Menu screens must clearly show the current context.

Example:

```text id="mnv303"
Business:
FastFood Group

Branch:
Branch A
```

The user must not accidentally configure another Branch.

---

# 7. Branch Selector

The Branch selector must display only Branches the employee is authorized to access.

Changing Branch must:

* recalculate permissions;
* reload Branch Menu;
* reload Branch-specific pricing;
* reload relevant operational configuration.

---

# 8. Global vs Branch Configuration

The UI should clearly distinguish:

```text id="mnv404"
Global Configuration
```

from:

```text id="mnv405"
Branch Configuration
```

A Branch-specific change must never appear as a Global change.

---

# 9. Global Menu List

The Global Menu list may display:

* Product;
* category;
* standard price;
* active state;
* Recipe readiness;
* Product type;
* updated time.

---

# 10. Branch Menu List

Branch Menu list may display:

* Product;
* Global status;
* Branch availability;
* effective price;
* standard price;
* override indicator;
* inventory status where useful.

---

# 11. Menu Search

Search should support:

* Product name;
* Product code;
* category;
* searchable configured fields.

Search must respect Business scope.

---

# 12. Menu Filters

Recommended filters:

* category;
* Product type;
* active/inactive;
* Branch availability;
* price override;
* Recipe readiness;
* inventory availability.

---

# 13. Menu Sorting

Supported sorting may include:

* Product name;
* category;
* price;
* updated date;
* active state.

---

# 14. Product Availability

The UI must distinguish Product existence from operational availability.

Example:

```text id="mnv506"
Product:
Burger

Global:
ACTIVE

Branch:
INACTIVE

Inventory:
IN STOCK
```

The Product still exists but is not currently offered by the Branch.

---

# 15. Menu Availability vs Inventory

Menu availability and inventory availability are separate states.

Possible state:

```text id="mnv607"
Menu:
ACTIVE

Inventory:
OUT OF STOCK
```

The UI must not incorrectly imply that menu activation guarantees stock availability.

---

# 16. Equipment Availability

A Product may be temporarily unavailable because required equipment is unavailable.

The UI should distinguish this from:

* Product deactivation;
* Branch Menu deactivation;
* inventory shortage.

---

# 17. Product Activation

Global Product activation is separate from Branch Menu activation.

Example:

```text id="mnv708"
Product:
ACTIVE

Branch A:
ACTIVE

Branch B:
INACTIVE
```

---

# 18. Branch Menu Activation

Authorized users may activate or deactivate a Product for the current Branch.

The action affects only that Branch.

---

# 19. Activation Confirmation

Where an operation can have a significant operational effect, the UI should show confirmation.

Example:

```text id="mnv809"
Deactivate Burger for Branch B?

New Orders will no longer be able to add this Product after the new configuration becomes effective.

Historical Orders remain unchanged.

[Cancel] [Deactivate]
```

---

# 20. Standard Price

A Product may have a Business-level standard selling price.

The UI must clearly label it:

```text id="mnv910"
Standard Price
30,000
```

---

# 21. Selling Price vs Cost

The UI must not confuse:

* selling price;
* Last Purchase Cost;
* Average Cost;
* FIFO cost;
* Recipe cost.

These are separate concepts.

---

# 22. Price Display

Currency formatting must use the centralized Frontend formatting system.

The UI must not implement independent currency formatting rules inside individual components.

---

# 23. Standard Price Editing

Authorized users may change the standard Product price.

The form should display:

* current price;
* new price;
* effective point;
* affected scope;
* optional reason where required.

---

# 24. Price Change Preview

Before saving a price change, the UI may show:

```text id="prv101"
Product:
Burger

Current:
30,000

New:
32,000

Scope:
Global

Effective:
Next Cash Session
```

---

# 25. Branch Price Override

A Branch may override the Global standard price if the employee has the required permission.

Example:

```text id="prv202"
Global:
30,000

Branch A:
30,000

Branch B:
32,000
```

---

# 26. Branch Override Scope

A Branch override:

* affects only the selected Branch;
* does not modify Global price;
* does not modify other Branches.

---

# 27. Override Indicator

The Branch Menu should clearly indicate an override.

Example:

```text id="prv303"
Price:
32,000

Override:
Yes

Global:
30,000
```

---

# 28. Remove Branch Override

Authorized users may remove a Branch override.

The effective price then returns to the valid Global standard price according to the active configuration.

---

# 29. Remove Override Confirmation

Example:

```text id="prv404"
Remove Branch price override?

Branch B will use the Global standard price after the configuration becomes effective.

[Cancel] [Remove Override]
```

---

# 30. Price Effective Boundary

The accepted system rule is:

> New Menu and Pricing configuration becomes operational from the next Cash Session.

The Frontend must clearly communicate this boundary.

---

# 31. Active Cash Session

A price change must not silently change the configuration already used by an active Cash Session.

The UI should show:

```text id="prv505"
Pending for next Cash Session
```

when applicable.

---

# 32. New Cash Session

When a new Cash Session starts, the latest valid effective configuration becomes available.

The UI should not require the cashier to manually reload every Product price.

---

# 33. Price Configuration Status

Useful states include:

```text id="prv606"
CURRENT
PENDING
SUPERSEDED
```

Exact Backend states remain authoritative.

---

# 34. Price History

Authorized users should be able to inspect historical price changes.

History may display:

* previous price;
* new price;
* scope;
* actor;
* timestamp;
* effective configuration;
* reason.

---

# 35. Historical Price Integrity

Historical Orders must retain their original prices.

The UI must never recalculate old Order amounts from the current Product price.

---

# 36. Open Order Price

When a Product is added to an Order, the applicable price is captured in the Order Item snapshot.

Later price changes must not silently change that Order Item.

---

# 37. Open Order After Price Change

Example:

```text id="prv707"
Order created:
Burger = 30,000

New price:
32,000

Existing Order:
Burger = 30,000

New Order:
Burger = 32,000
```

---

# 38. Price and Payment

Payment uses the authoritative Order financial amount.

Changing the Product price does not change the amount already captured in an existing Order.

---

# 39. Price and Refund

Refund calculations must use the historical transaction snapshot.

Current Product price must not be used to reinterpret a historical refund.

---

# 40. Price and Cancellation

Cancellation uses the historical Order state and snapshot.

Current Menu or price configuration must not rewrite the cancelled transaction.

---

# 41. Discounts

Discounts are transaction-level financial adjustments.

A discount does not change the configured Product price.

Example:

```text id="dsc101"
Product:
30,000

Discount:
5,000

Final:
25,000
```

---

# 42. Discount UI

The Order UI should display:

```text id="dsc202"
Base Price     30,000
Discount       -5,000
Final Amount   25,000
```

The Product configuration screen should continue showing:

```text
Product Price:
30,000
```

---

# 43. Discount Permission

Discount operations require explicit permission.

The Frontend should not expose discount actions to unauthorized users.

Backend authorization remains authoritative.

---

# 44. Discount Limits

If discount limits are configured, the UI may validate them before submission.

Final validation is performed by the Backend.

---

# 45. Custom Markup

Authorized users may apply a custom markup to an Order.

The accepted range is:

```text
0% – 100%
```

---

# 46. Markup Calculation

The Backend-defined calculation is:

```text id="mkp101"
Final Price =
Last Purchase Cost × (1 + Markup / 100)
```

The Frontend may display the calculation result returned by the Backend.

It must not become the financial authority.

---

# 47. Markup UI

Example:

```text id="mkp202"
Last Purchase Cost:
20,000

Markup:
25%

Calculated Price:
25,000
```

---

# 48. Markup Validation

The UI should reject obvious invalid values:

* below 0%;
* above 100%;
* invalid number;
* empty required value.

Backend validation remains mandatory.

---

# 49. Markup and Standard Price

Custom markup does not modify the Business-level standard Product price.

It is a transaction-level pricing operation.

---

# 50. Last Purchase Cost Visibility

Cost information may be permission-controlled.

Users without the required permission must not see restricted cost data.

---

# 51. Set Price

A Set has its own selling price.

The UI should display Set price independently from component prices.

---

# 52. Set Price Example

```text id="set101"
Combo Set:
45,000

Burger:
30,000

Fries:
10,000

Drink:
8,000
```

The component prices do not automatically determine the Set price unless a Business-defined calculation rule explicitly exists.

---

# 53. Set Configuration

Changing Set composition is a configuration operation.

Where operational behavior changes, a new Set Version must be created.

---

# 54. Set Effective Boundary

Set configuration changes follow the same effective configuration principle.

New operational configuration becomes effective from the next Cash Session where applicable.

---

# 55. Set Historical Integrity

Historical Set Orders retain:

* Set identity;
* Set configuration/version;
* Set price;
* financial snapshot.

---

# 56. Recipe Dependency

Products requiring Recipes must have a valid applicable Recipe Version before normal sale.

The Menu UI may show Recipe readiness.

Example:

```text id="rcp101"
Recipe:
READY
```

or:

```text
Recipe:
PENDING APPROVAL
```

---

# 57. Recipe Dependency Warning

A Product may be visible in Global Menu while still not being operationally sellable.

The UI should make the reason clear.

---

# 58. Product Menu Readiness

A useful status model is:

```text id="rdy101"
Product
ACTIVE

Recipe
READY

Branch Menu
ACTIVE

Inventory
IN STOCK
```

The Frontend should keep these dimensions separate.

---

# 59. Branch Menu Readiness

Branch operational availability may depend on:

* Product active state;
* Branch Menu state;
* Recipe validity;
* Set configuration;
* inventory;
* equipment availability;
* other Backend rules.

---

# 60. Menu Configuration Detail

A Product Menu detail page may show:

```text id="mnv1010"
Product
Category
Global Status
Branch Status
Standard Price
Branch Price
Recipe Status
Inventory Status
Equipment Status
Effective Configuration
```

---

# 61. Global Menu Editor

The Global Menu editor should allow authorized users to configure:

* Product;
* category;
* active state;
* standard price;
* relevant commercial settings.

---

# 62. Branch Menu Editor

The Branch Menu editor should allow authorized users to configure:

* availability;
* Branch price override;
* Branch-specific operational state.

---

# 63. Branch Menu Isolation

Every Branch mutation must contain explicit Branch context.

The UI must not reuse stale Branch state after switching.

---

# 64. Branch Switching

After switching Branch:

1. clear or invalidate Branch-specific state;
2. load new Branch context;
3. recalculate permissions;
4. load Branch Menu;
5. load Branch prices;
6. refresh operational status.

---

# 65. Unsaved Changes During Branch Switch

If the user has unsaved configuration changes, the UI must warn before switching Branch.

---

# 66. Deep Links

A URL containing a Product or Branch identifier is only navigation information.

The Frontend must request and validate the authoritative context.

---

# 67. Business Isolation

The Frontend must never intentionally display Menu data belonging to another Business.

Backend authorization remains the final protection.

---

# 68. Branch Isolation

A Branch-scoped user must not access unauthorized Branch Menu configuration.

---

# 69. Product Search Scope

Search results must be limited to the current authorized Business and applicable Branch context.

---

# 70. Bulk Menu Operations

Where supported, authorized users may perform bulk operations such as:

* activate;
* deactivate;
* update Branch availability.

Bulk actions must show affected item count before confirmation.

---

# 71. Bulk Price Changes

Bulk price modification is a high-impact operation.

If supported, the UI must require:

* explicit scope;
* affected Product list;
* old/new values;
* confirmation;
* appropriate permission;
* operation identity.

---

# 72. Bulk Operation Result

Example:

```text id="bulk101"
Updated:
46

Rejected:
4

Conflicts:
2

[View Details]
```

Partial success must not be presented as full success.

---

# 73. Configuration Version

Menu and pricing changes must reference configuration versions.

The UI may display:

```text id="cfg101"
Configuration Version:
v42

Status:
PENDING EFFECTIVE
```

---

# 74. Configuration History

Authorized users may inspect:

* version;
* creator;
* creation time;
* effective point;
* previous version;
* status;
* affected Product/Branch.

---

# 75. Configuration Approval

Where approval is required, the UI must clearly distinguish:

```text
Draft
Approved
Pending Effective
Effective
Superseded
```

---

# 76. Approval Permission

Approval requires appropriate authority.

Editing a configuration does not automatically grant approval permission.

---

# 77. Configuration Conflict

Conflict can occur when:

* two users edit the same Product;
* Branch price changes concurrently;
* offline configuration is stale;
* another configuration version became effective.

---

# 78. Conflict UI

Example:

```text id="cfg202"
Configuration conflict

Current server version:
v43

Your version:
v42

The current configuration has changed.

[Review]
[Discard Changes]
```

---

# 79. Conflict Resolution

Conflict resolution must:

* show current authoritative state;
* preserve historical values;
* identify conflicting versions;
* identify resolving actor;
* create a valid new configuration where required.

Silent last-write-wins is prohibited for important configuration.

---

# 80. Optimistic Concurrency

Configuration mutations should include the expected configuration version.

Stale mutations must be rejected as conflicts.

---

# 81. Duplicate Configuration Requests

Retrying the same configuration command must not create duplicate:

* price changes;
* Branch overrides;
* configuration versions;
* approvals.

---

# 82. Operation UUID

Retryable configuration commands should use operation UUIDs.

The UI should track operation state until authoritative completion.

---

# 83. Unknown Mutation Result

If the request times out:

```text id="cfg303"
The result is unknown.

Checking configuration status...
```

The UI should reconcile before offering another mutation.

---

# 84. Offline Menu

Trusted devices may use the latest valid local Menu configuration according to offline authorization.

---

# 85. Offline Price

An offline device uses the latest valid locally authorized price configuration.

A new server price must not be assumed locally before synchronization.

---

# 86. Offline Transaction

Offline-created Orders retain the local price snapshot used at creation time.

Later synchronization must not rewrite the original transaction price.

---

# 87. Configuration Synchronization Priority

Transaction synchronization has priority over configuration synchronization.

Example:

```text id="syn101"
Offline Order
Price Version A
       ↓
Transaction Sync
       ↓
Price Version B Sync
```

---

# 88. Offline Configuration Mutation

If Menu/Pricing configuration mutation is not supported offline, the UI must explicitly require an online connection.

It must not create a fake local success state.

---

# 89. Synchronization Status

Menu/Pricing pages may show:

```text
Synced
Pending
Syncing
Conflict
Offline
```

---

# 90. Stale Configuration

If local configuration is old, the UI should make freshness visible when it matters operationally.

Example:

```text id="syn202"
Using configuration from:
10:42

Connection:
Offline
```

---

# 91. Subscription Read-Only

When the Business enters read-only state:

* current Menu remains viewable;
* current prices remain viewable;
* historical configuration remains viewable;
* modifications are blocked.

---

# 92. Read-Only UI

The UI should clearly communicate:

```text id="sub101"
Business is in read-only mode.

Menu and pricing configuration cannot be modified until the subscription is active.
```

---

# 93. Subscription Restrictions

Offline state must not bypass subscription restrictions.

---

# 94. Employee Status

Inactive employees must not create new Menu/Pricing modifications.

---

# 95. Permission Model

Menu/Pricing UI must respect:

* Employee status;
* Role Permission;
* Employee Override;
* Branch Scope;
* Business Scope;
* Subscription Entitlement;
* configuration state.

---

# 96. Permission Examples

Possible permissions include:

```text
menu.view
menu.edit
menu.activate
menu.branch_configure
pricing.view
pricing.edit
pricing.branch_override
discount.apply
markup.apply
set.configure
```

Exact permission identifiers remain Backend-authoritative.

---

# 97. Sensitive Price Data

Cost-related information should be hidden from unauthorized users.

Selling price and cost must not be treated as the same sensitivity class.

---

# 98. Audit

Important Menu/Pricing operations must be auditable.

Examples:

* Product activation;
* Branch Menu activation;
* Branch Menu deactivation;
* standard price change;
* Branch price override;
* discount;
* markup;
* Set configuration;
* approval;
* conflict resolution.

---

# 99. Audit Display

Authorized users may see:

```text id="aud101"
Actor:
Employee A

Branch:
Branch B

Product:
Burger

Old:
30,000

New:
32,000

Time:
2026-10-05 14:32
```

---

# 100. Historical Configuration

Historical configuration must remain reconstructable.

Frontend history screens must not expose an action that overwrites old versions.

---

# 101. Error States

Menu/Pricing UI must distinguish:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

---

# 102. Validation Error

Example:

```text id="err101"
Price must be greater than or equal to 0.
```

---

# 103. Authorization Error

Example:

```text id="err202"
You do not have permission to change Branch pricing.
```

---

# 104. Conflict Error

Example:

```text id="err303"
This configuration was changed by another user.
Refresh the current configuration before continuing.
```

---

# 105. Business Rule Error

Example:

```text id="err404"
This Product cannot be activated because the required Recipe is not approved.
```

---

# 106. Temporary Error

Example:

```text id="err505"
The server is temporarily unavailable.

Your current configuration has not been changed.
```

---

# 107. Recovery

Safe recovery actions may include:

* retry;
* refresh;
* reload current configuration;
* review conflict;
* return to previous page.

Blind retry must not be offered for unknown non-idempotent operations.

---

# 108. Loading States

Menu/Pricing pages should provide:

* initial loading;
* table loading;
* detail loading;
* mutation progress;
* synchronization progress.

---

# 109. Empty States

Example:

```text id="emp101"
No Products are available in this Menu.

[Create Product]
```

The action must only appear if permitted.

---

# 110. Partial Data

If secondary information fails to load, the main configuration should remain usable where possible.

Example:

```text
Price loaded successfully.

History could not be loaded.
[Retry History]
```

---

# 111. Optimistic UI

Optimistic updates may be used for low-risk local interactions.

Important financial/configuration mutations should not be presented as authoritative until server confirmation.

---

# 112. Double Submission Protection

Save/activate/deactivate buttons must prevent accidental duplicate submissions.

---

# 113. Button State

During an authoritative mutation:

```text
Saving...
```

or:

```text
Applying...
```

The user must receive clear completion or failure feedback.

---

# 114. Price Input

Price input should:

* accept valid numeric input;
* format currency appropriately;
* reject invalid values;
* avoid accidental precision loss.

---

# 115. Percentage Input

Markup and discount percentage fields should:

* support valid decimal precision where configured;
* prevent values outside allowed limits;
* display `%` clearly.

---

# 116. Category Selection

Category selectors must use authorized Business-level categories.

---

# 117. Product Selector

Product selectors must respect:

* Business scope;
* allowed Product types;
* active state where required;
* permission.

---

# 118. Configuration Comparison

Where version comparison is supported, differences should be displayed explicitly.

Example:

```text id="cmp101"
Field          Old       New
Price          30,000    32,000
Branch Status  Active    Inactive
```

---

# 119. Menu Preview

The UI may provide a Branch Menu preview.

The preview must clearly indicate that it represents configuration, not necessarily current inventory availability.

---

# 120. POS Relationship

The Menu/Pricing frontend is configuration-oriented.

The POS frontend consumes the effective configuration.

POS must not independently redefine Menu/Pricing rules.

---

# 121. POS Price Snapshot

The POS captures applicable price into the Order Item snapshot.

Menu/Pricing UI must preserve this architectural boundary.

---

# 122. Historical Report Relationship

Reports use historical transaction/configuration snapshots as required.

Current Menu changes must not rewrite historical reports.

---

# 123. Dashboard Relationship

Dashboard widgets may consume Menu/Pricing data but must not mutate authoritative configuration unless an explicit authorized workflow exists.

---

# 124. Performance

Targets:

* Menu search p95 ≤150 ms;
* Menu list p95 ≤300 ms after API response;
* Product price detail p95 ≤300 ms;
* Branch Menu load p95 ≤500 ms after required API response;
* local price input feedback p95 ≤100 ms;
* configuration mutation UI feedback p95 ≤100 ms;
* configuration reconciliation UI update ≤2 s after authoritative result.

---

# 125. Initial Page Performance

Targets:

* Global Menu first useful content p75 ≤1.5 s;
* Branch Menu first useful content p75 ≤1.5 s;
* Menu detail interactive p75 ≤2.0 s;
* Pricing editor interactive p75 ≤2.0 s.

---

# 126. Fatal Error Rate

Target:

**Fatal Menu/Pricing UI error rate <0.1% sessions.**

---

# 127. Accessibility

Menu/Pricing UI must support:

* keyboard navigation;
* semantic controls;
* visible focus;
* accessible labels;
* screen reader-compatible status;
* accessible dialogs;
* non-color-only state communication.

---

# 128. Price Accessibility

Prices must remain understandable to screen readers.

Example:

```text
32,000 UZS
```

must not depend only on visual formatting.

---

# 129. Status Accessibility

Status such as:

```text
Active
Inactive
Pending
Conflict
```

must be represented through text or accessible labels, not color alone.

---

# 130. Responsive Behavior

Menu/Pricing configuration is primarily desktop/admin-oriented but must remain usable on smaller screens.

Tables may reflow or use local horizontal scrolling when required.

---

# 131. State Management

Frontend state should separate:

```text id="state101"
Business Context
Branch Context
Menu Query
Menu Data
Pricing Data
Configuration Version
Form State
Permission State
Subscription State
Sync State
Conflict State
UI State
```

---

# 132. Authoritative State

Backend is authoritative for:

* Product availability;
* effective price;
* Branch override;
* configuration version;
* permissions;
* subscription;
* historical state;
* financial values.

---

# 133. Local UI State

Frontend may own:

* selected Product;
* filters;
* sorting;
* modal state;
* form draft;
* comparison selection;
* tab state.

---

# 134. Cache

Menu/Pricing read models may be cached.

Cache must not be treated as authoritative for financial transactions.

---

# 135. Cache Isolation

Cache keys must include:

* Business;
* Branch where applicable;
* configuration version.

---

# 136. Cache Invalidation

Cache invalidation must occur after relevant authoritative changes.

Changes include:

* Product activation;
* Branch Menu change;
* price change;
* Branch override;
* Set configuration;
* Recipe configuration where Menu readiness changes;
* synchronization.

---

# 137. Testing

Tests must cover:

### Global Menu

* Product activation;
* Product deactivation;
* category;
* search;
* filtering.

### Branch Menu

* Branch activation;
* Branch deactivation;
* Branch isolation;
* Branch switching.

### Pricing

* standard price;
* Branch override;
* override removal;
* effective boundary;
* history.

### Discounts

* permission;
* limits;
* transaction display.

### Markup

* 0%;
* 100%;
* invalid values;
* cost visibility.

### Configuration

* versioning;
* approval;
* conflicts;
* idempotency.

---

# 138. Security Testing

Test:

* Business isolation;
* Branch isolation;
* unauthorized price modification;
* unauthorized Branch override;
* unauthorized discount;
* unauthorized markup;
* unauthorized configuration approval;
* subscription read-only enforcement.

---

# 139. Offline Testing

Test:

* offline Menu read;
* stale configuration;
* offline price snapshot;
* synchronization;
* conflict;
* unknown mutation result;
* subscription restriction.

---

# 140. Visual Testing

Visual regression coverage should include:

* Global Menu;
* Branch Menu;
* Product price editor;
* Branch override editor;
* configuration history;
* configuration comparison;
* conflict dialog;
* read-only mode;
* mobile/reflowed views.

---

# 141. Observability

Frontend telemetry may track:

* Menu load latency;
* Pricing load latency;
* mutation latency;
* configuration conflict rate;
* synchronization failures;
* permission failures;
* fatal UI errors.

Sensitive financial/configuration details should not be unnecessarily included in telemetry.

---

# 142. Menu/Pricing Invariants

The following invariants are mandatory:

1. Global Menu is Business-scoped.
2. Branch Menu is Branch-scoped.
3. Branch Menu cannot cross Business boundaries.
4. Branch configuration does not affect another Branch.
5. Product identity remains stable.
6. Product existence does not imply Branch availability.
7. Global Product activation does not automatically activate all Branches.
8. Menu availability is separate from inventory availability.
9. Menu availability is separate from equipment availability.
10. Standard selling price is separate from inventory cost.
11. Standard price is Business-level.
12. Branch price override is Branch-level.
13. Branch override does not modify Global price.
14. Branch override does not modify another Branch.
15. Price changes have a deterministic effective boundary.
16. New Menu/Pricing configuration becomes effective from the next Cash Session.
17. Active Cash Sessions do not silently switch configuration.
18. New Cash Sessions use the latest valid effective configuration.
19. Existing Order Item prices remain unchanged.
20. Historical Order prices remain unchanged.
21. Current Product price cannot reinterpret historical transactions.
22. Current Product price cannot reinterpret historical refunds.
23. Current Product price cannot reinterpret historical cancellations.
24. Discounts do not modify Product base price.
25. Discount is a transaction-level financial adjustment.
26. Discount requires appropriate permission.
27. Custom markup is limited to 0–100%.
28. Custom markup uses applicable Last Purchase Cost.
29. Custom markup does not modify Global standard price.
30. Set has its own selling price.
31. Set price is separate from component prices.
32. Historical Set Orders retain historical price.
33. Set configuration changes are versioned where operational behavior changes.
34. Set component substitution is prohibited during normal sale.
35. Required Recipe conditions must be satisfied before normal sale where applicable.
36. Recipe readiness does not guarantee inventory availability.
37. Product readiness does not guarantee Branch availability.
38. Product readiness does not guarantee equipment availability.
39. Important configuration changes are versioned.
40. Configuration history remains available.
41. Historical configuration cannot be silently overwritten.
42. Approval is separate from editing where approval is required.
43. Approval requires appropriate permission.
44. Stale configuration updates are rejected.
45. Silent last-write-wins is prohibited for important configuration.
46. Configuration mutations use operation UUID where retryable.
47. Duplicate mutations do not create duplicate configuration versions.
48. Unknown mutation results are reconciled.
49. Conflict resolution is explicit.
50. Conflict resolution preserves historical values.
51. Conflict resolution is attributable.
52. Important Menu/Pricing changes are audited.
53. Audit records are immutable.
54. Branch switching recalculates effective configuration.
55. Branch switching cannot carry stale Branch configuration into another Branch.
56. Unauthorized Branches cannot be selected.
57. URL Branch/Product IDs are not authorization.
58. Backend remains final authorization authority.
59. Subscription read-only blocks modifying Menu/Pricing configuration.
60. Offline mode cannot bypass subscription restrictions.
61. Offline mode uses only authorized local configuration.
62. Offline configuration cannot assume unavailable server changes.
63. Offline-created Order prices retain local snapshots.
64. Transaction synchronization has priority over configuration synchronization.
65. Cached configuration is not authoritative.
66. Cache keys include Business scope.
67. Branch-specific cache includes Branch scope.
68. Cache invalidation follows authoritative changes.
69. Product cost data is permission-controlled where required.
70. Selling price and cost are not conflated.
71. Financial values use centralized formatting.
72. Client-side calculation does not become financial authority.
73. Backend-provided authoritative financial values are displayed as such.
74. Menu UI does not directly mutate historical Orders.
75. Pricing UI does not directly mutate historical payments.
76. Menu UI does not independently determine inventory truth.
77. Product activation does not delete history.
78. Branch deactivation does not delete Product identity.
79. Product archive preserves historical data.
80. Menu configuration remains attributable to an actor.
81. Device context is retained for important configuration changes.
82. Employee deactivation blocks new modifications.
83. Permission changes are reflected in the UI.
84. Backend rejects stale unauthorized actions.
85. Bulk operations identify their exact scope.
86. Bulk operations expose partial failures.
87. Bulk price operations require explicit confirmation.
88. Large Menu lists use pagination.
89. Search respects Business and Branch scope.
90. Search target is p95 ≤150 ms.
91. Menu list target is p95 ≤300 ms after API response.
92. Branch Menu load target is p95 ≤500 ms after required API response.
93. Local interaction target is p95 ≤100 ms.
94. Configuration reconciliation target is ≤2 s after authoritative result.
95. Global Menu first useful content target is p75 ≤1.5 s.
96. Branch Menu first useful content target is p75 ≤1.5 s.
97. Menu detail interactive target is p75 ≤2.0 s.
98. Pricing editor interactive target is p75 ≤2.0 s.
99. Fatal Menu/Pricing UI error rate target is <0.1% sessions.
100. Accessibility is mandatory.
101. Status is not communicated by color alone.
102. Keyboard navigation is supported.
103. Screen reader labels are provided.
104. Unsaved configuration changes are protected.
105. Duplicate submissions are prevented.
106. Temporary failures provide safe recovery.
107. Unknown results are reconciled before retry.
108. Permanent failures are not blindly retried.
109. Historical reports are not rewritten by current Menu changes.
110. Dashboard does not become a second source of truth.
111. POS consumes effective Menu/Pricing configuration.
112. POS captures price snapshots at Order Item creation.
113. Current configuration cannot reinterpret historical transactions.
114. Menu configuration supports offline-first architecture.
115. Menu configuration supports synchronization architecture.
116. Menu configuration supports audit architecture.
117. Menu configuration supports Business/Branch isolation.
118. Menu configuration supports future multi-register architecture.
119. Menu/Pricing configuration prioritizes correctness over UI convenience.
120. Backend remains the final authority for operational Menu/Pricing state.

---

# 143. Recommended Frontend Structure

```text
frontend/
└── src/
    ├── features/
    │   ├── menu/
    │   │   ├── pages/
    │   │   ├── components/
    │   │   ├── forms/
    │   │   ├── queries/
    │   │   ├── mutations/
    │   │   ├── validation/
    │   │   └── types/
    │   │
    │   ├── pricing/
    │   │   ├── pages/
    │   │   ├── components/
    │   │   ├── forms/
    │   │   ├── queries/
    │   │   ├── mutations/
    │   │   ├── conflicts/
    │   │   └── types/
    │   │
    │   ├── products/
    │   ├── recipes/
    │   └── sets/
    │
    ├── entities/
    │   ├── product/
    │   ├── menu/
    │   ├── pricing/
    │   ├── recipe/
    │   └── set/
    │
    ├── synchronization/
    ├── state/
    ├── api/
    └── shared/
```

---

# 144. Dependency Rules

The Frontend must follow:

```text
Page
  ↓
Feature Component
  ↓
Feature Query / Mutation
  ↓
API / Data Layer
  ↓
Backend
```

Components must not directly access persistence or construct authoritative financial state.

---

# 145. AI-Agent Development Rules

AI-assisted implementation must:

1. preserve Business/Branch boundaries;
2. preserve configuration versioning;
3. preserve historical price snapshots;
4. preserve permission checks;
5. preserve subscription restrictions;
6. avoid client-side financial authority;
7. avoid silent last-write-wins;
8. use existing shared components;
9. use centralized currency/number formatting;
10. add tests for important configuration changes;
11. update related documentation when architecture changes;
12. avoid creating duplicate Product/Recipe/Set abstractions;
13. preserve offline/synchronization boundaries.

---

# 146. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/13_Products_Recipes_and_Sets_UI.md`
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
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/12_Products_and_Recipes.md`
* `docs/02_System_Analysis/13_Menu_and_Pricing.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 147. Status

**Document:** `14_Menu_and_Pricing_UI.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `13_Products_Recipes_and_Sets_UI.md`

**Next Document:** `15_Attendance_and_Payroll_UI.md`

