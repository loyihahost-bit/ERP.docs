# Products, Recipes and Sets UI

**Document ID:** FA-13
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `12_Inventory_and_Warehouse_UI.md`
**Next Document:** `14_Menu_and_Pricing_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture and user interface behavior for:

* Products;
* Product Categories;
* Raw Materials;
* Semi-Finished Products;
* Finished Products;
* Recipes;
* Recipe Versions;
* Recipe approval;
* Sets;
* Set Versions;
* Product configuration;
* Recipe dependencies;
* Set component dependencies.

The main principle is:

> Product configuration must be simple to manage, while Recipe and Set changes must preserve historical and operational integrity.

---

# 2. Scope

This document covers:

* Product list;
* Product detail;
* Product creation;
* Product editing;
* Product activation/deactivation;
* Product archive;
* Product categories;
* Product types;
* Recipe creation;
* Recipe editing;
* Recipe versions;
* Recipe approval;
* Recipe history;
* Recipe visibility;
* Recipe permissions;
* Semi-Finished Products;
* Finished Products;
* Sets;
* Set composition;
* Set pricing relationship;
* component availability;
* inventory dependency indicators;
* menu dependency;
* historical integrity;
* offline configuration;
* synchronization;
* conflict handling;
* audit;
* accessibility;
* performance.

---

# 3. Product Model

The Product UI represents a Business-level Product identity.

The basic hierarchy is:

```text
Business
   ↓
Product Category
   ↓
Product
   ├── Recipe
   └── Set Configuration
```

Branch-specific availability and pricing are handled by the Menu and Pricing architecture.

---

# 4. Product Identity

A Product has a stable identity.

Changing:

* name;
* image;
* category;
* description;
* activation state;
* Recipe Version

must not create an unrelated Product identity unless the business explicitly creates a new Product.

---

# 5. Product Types

The UI must distinguish relevant Product types.

Initial types include:

```text
RAW_MATERIAL
SEMI_FINISHED
FINISHED_PRODUCT
SET
```

The exact technical enum remains Backend-authoritative.

---

# 6. Product Category

Every Product belongs to exactly one menu category according to the accepted Product model.

Category selection is required where applicable.

---

# 7. Product List

The Product list should display:

* Product name;
* code;
* category;
* Product type;
* active state;
* Recipe state;
* Set state where applicable;
* updated time.

---

# 8. Product Search

Search should support:

* Product name;
* Product code/SKU;
* configured searchable fields.

Search must respect:

* Business scope;
* permissions;
* active context.

---

# 9. Product Filters

Recommended filters:

* category;
* Product type;
* active/inactive;
* Recipe status;
* Set status;
* archived;
* menu availability where applicable.

---

# 10. Product Sorting

Supported sorting may include:

* name;
* code;
* category;
* updated date;
* Product type;
* active state.

---

# 11. Pagination

Product lists must use pagination for large Business catalogs.

Cursor pagination should be preferred where appropriate.

---

# 12. Product Creation

Recommended workflow:

```text id="prd101"
Create Product
      ↓
Basic Information
      ↓
Product Type
      ↓
Category
      ↓
Unit
      ↓
Optional Recipe/Set configuration
      ↓
Review
      ↓
Create
```

---

# 13. Product Basic Information

The form may include:

* Product name;
* Product code;
* category;
* description;
* image;
* Product type;
* unit;
* active state where permitted.

---

# 14. Product Code

Product codes must be generated or validated according to Backend rules.

If the system automatically generates a code, the Frontend must not independently generate an authoritative code.

---

# 15. Product Image

Product images are presentation data.

Changing an image must not change:

* Product identity;
* historical Orders;
* Recipe history;
* Inventory history.

---

# 16. Product Unit

The unit must be selected from supported units.

Examples:

```text id="prd212"
kg
g
l
ml
pcs
```

The actual supported unit registry is authoritative on the Backend.

---

# 17. Product Description

Description is non-financial configuration.

Changing description must not affect:

* stock;
* Recipe;
* historical Order prices;
* historical transactions.

---

# 18. Product Activation

Authorized users may activate or deactivate Products.

Deactivation must not delete the Product.

---

# 19. Product Inactive State

An inactive Product:

* cannot be newly sold where the Backend prohibits sale;
* remains visible in historical data;
* remains available for authorized historical inspection;
* retains Inventory history;
* retains Recipe history;
* retains Set history.

---

# 20. Product Archive

Products with historical or dependency relationships should be archived rather than deleted.

Archive is a lifecycle state, not physical data deletion.

---

# 21. Delete Restrictions

The UI must not offer ordinary Delete when the Product has protected historical/dependency data.

Instead:

```text
Archive Product
```

should be presented.

---

# 22. Product Detail

Product detail should provide tabs or sections such as:

```text
Overview
Recipe
Sets
Inventory
Menu
History
Audit
```

Visibility depends on permission.

---

# 23. Product Overview

Example:

```text id="prd323"
Burger

Type:
Finished Product

Category:
Burgers

Unit:
pcs

Status:
ACTIVE
```

---

# 24. Product Dependencies

The Product detail may show:

* Recipe;
* Recipe Versions;
* Set membership;
* Inventory usage;
* Menu usage;
* historical usage.

---

# 25. Dependency Warning

Before deactivation/archive, the UI should explain relevant dependencies.

Example:

```text
This Product is used by:

3 Recipes
2 Sets
4 Branch Menus
```

The exact count must come from authoritative data.

---

# 26. Recipe

A Recipe defines the component composition required for a Product.

Example:

```text id="prd434"
Burger Recipe

Bread       1 pcs
Meat        150 g
Sauce       30 g
Vegetables  50 g
```

---

# 27. Recipe Components

Recipe components may include:

* Raw Materials;
* Semi-Finished Products;
* other supported Product types.

The Frontend must follow the Backend's allowed dependency rules.

---

# 28. Recipe Quantity

Each component requires:

* Product;
* quantity;
* unit;
* optional relevant configuration.

Quantity must respect supported precision.

---

# 29. Recipe Unit

The UI should clearly show component units.

Example:

```text
Meat
150 g

Sauce
30 g
```

---

# 30. Recipe Creation

Workflow:

```text id="prd545"
Create Recipe
      ↓
Select Product
      ↓
Add Components
      ↓
Enter Quantities
      ↓
Validate
      ↓
Save Draft
      ↓
Submit for Approval
```

---

# 31. Recipe Draft

A Recipe may initially exist as a Draft.

Draft changes do not automatically become operational.

---

# 32. Recipe Approval

Where approval is required:

```text
Draft
  ↓
Submitted
  ↓
Approved
  ↓
Effective
```

Exact state names remain Backend-authoritative.

---

# 33. Approval Permission

Only authorized employees may approve Recipes.

The Frontend must hide or disable approval actions when the user lacks authority.

---

# 34. Separation of Editing and Approval

The user who edits a Recipe does not automatically gain approval authority.

The UI must represent editing and approval as separate operations.

---

# 35. Recipe Version

Every operationally meaningful Recipe change must be represented by a Recipe Version.

Example:

```text id="prd656"
Recipe Version 4

Status:
EFFECTIVE

Previous:
Version 3
```

---

# 36. Recipe Version History

The Recipe history should show:

* version;
* status;
* created by;
* created at;
* approved by;
* approved at;
* effective point;
* changes.

---

# 37. Recipe Version Comparison

Authorized users may compare versions.

Example:

```text id="prd767"
Version 3
Meat: 150 g
Sauce: 30 g

Version 4
Meat: 170 g
Sauce: 25 g
```

---

# 38. Historical Recipe Integrity

Historical inventory deductions must remain associated with the Recipe Version used at the time.

The Frontend must not reinterpret old inventory transactions using the current Recipe.

---

# 39. Recipe Change

Changing a Recipe must not silently modify an already effective historical version.

Instead:

```text
Current Version
       ↓
New Draft
       ↓
Approval
       ↓
New Effective Version
```

---

# 40. Recipe Approval Warning

Before approval, the UI should display a review summary.

Example:

```text
Approve Recipe Version 4?

Changes:
Meat: 150 g → 170 g
Sauce: 30 g → 25 g

This version will become effective according to configuration rules.
```

---

# 41. Recipe Rejection

If approval is rejected:

* the draft remains traceable;
* rejection reason is displayed;
* historical versions remain unchanged.

---

# 42. Recipe Rejection Reason

A rejection reason should be required where defined by business rules.

---

# 43. Recipe Archive

Old Recipe Versions should be retained.

They should not be physically deleted merely because a newer version becomes effective.

---

# 44. Effective Recipe

The UI should clearly distinguish:

```text
DRAFT
APPROVED
EFFECTIVE
SUPERSEDED
ARCHIVED
```

Only Backend-valid states are authoritative.

---

# 45. Recipe Operational Availability

A Product requiring a Recipe must have a valid applicable Recipe Version before normal sale.

The UI may show:

```text
Recipe:
Missing / Pending Approval / Ready
```

---

# 46. Recipe Warning in Product

Example:

```text
Product:
Burger

Recipe:
Pending Approval

Sale:
Not operationally available
```

The exact sale restriction is determined by Backend rules.

---

# 47. Recipe Dependency Indicator

Product list may show:

```text
Recipe:
Ready
```

or:

```text
Recipe:
Needs Approval
```

---

# 48. Recipe Visibility

Recipe visibility is permission-controlled.

An employee may be able to:

* sell a Product;
* view inventory;
* but not view Recipe composition.

---

# 49. Recipe Modification Permission

Recipe modification requires explicit permission.

---

# 50. Recipe Approval Permission

Recipe approval requires explicit permission separate from ordinary editing where applicable.

---

# 51. Recipe Cost Visibility

Recipe cost may be restricted.

The UI must not expose component costs to users without the required permission.

---

# 52. Semi-Finished Product

A Semi-Finished Product is an intermediate Product produced from components.

Example:

```text id="prd878"
Marinated Meat

Type:
SEMI_FINISHED
```

---

# 53. Semi-Finished Recipe

A Semi-Finished Product may have its own Recipe.

Example:

```text
1 kg Meat
200 g Mayonnaise
Spices
```

---

# 54. Recipe Chain

The UI should support navigating:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

---

# 55. Recipe Chain Protection

The UI must prevent creating invalid circular Recipe relationships where Backend rules prohibit them.

Backend validation remains authoritative.

---

# 56. Recipe Dependency Preview

Before saving a Recipe, the UI may show its dependency structure.

Example:

```text
Burger
 ├── Bread
 ├── Marinated Meat
 │    ├── Meat
 │    ├── Mayonnaise
 │    └── Spices
 └── Sauce
```

---

# 57. Deep Dependency

Large Recipe dependency trees should use lazy loading rather than loading the entire graph immediately.

---

# 58. Recipe Search

Component search should support:

* Product name;
* Product code;
* allowed Product type.

Unauthorized Products should not appear as selectable components.

---

# 59. Component Selection

When adding a Recipe component, the UI should show:

* Product name;
* type;
* unit;
* availability indicator where useful.

---

# 60. Insufficient Stock

A Recipe may exist even when required inventory is currently unavailable.

The UI must distinguish:

```text
Recipe Valid
```

from:

```text
Current Stock Available
```

---

# 61. Recipe vs Inventory

Recipe configuration and inventory state are separate.

A valid Recipe does not guarantee current stock.

---

# 62. Recipe vs Menu

A valid Recipe does not automatically make a Product available at every Branch.

Menu availability remains separate.

---

# 63. Recipe and Branches

Recipes are Business-level configuration according to the accepted product model.

The same approved Recipe can be used by permitted Branches.

---

# 64. Branch Context

When viewing a Recipe, the UI should distinguish Business-level configuration from Branch-specific operational availability.

---

# 65. Set

A Set is a Product composed of multiple configured components.

Example:

```text id="prd989"
Combo Set

Burger
Fries
Drink
```

---

# 66. Set Identity

A Set has a stable Product identity.

Changing Set composition creates a new configuration/version where required.

---

# 67. Set Composition

Set composition defines:

* component Product;
* quantity;
* mandatory/optional status where supported;
* relevant configuration.

---

# 68. Set Pricing

A Set has its own selling price.

Component Product price changes do not automatically rewrite historical Set prices.

---

# 69. Set Version

Operational Set composition changes should create a new Set Version where required.

---

# 70. Set Version Flow

```text
Draft
  ↓
Review
  ↓
Approved
  ↓
Effective
  ↓
Superseded
```

---

# 71. Set Approval

If approval is required, only authorized employees may approve a Set Version.

---

# 72. Set Component Substitution

Normal Set sale does not permit component substitution.

The UI must not present a generic “replace component” action.

---

# 73. Set Component Availability

The Set can be operationally available only when mandatory components satisfy relevant conditions.

These may include:

* active component;
* Branch availability;
* valid configuration;
* sufficient inventory.

---

# 74. Set Availability Indicator

Example:

```text id="prd191"
Combo Set

Status:
AVAILABLE

Components:
3/3 available
```

---

# 75. Set Unavailability

Example:

```text
Combo Set

Unavailable

Reason:
Fries component is out of stock.
```

---

# 76. Set Dependency Navigation

The Set detail should allow authorized users to inspect component Products.

---

# 77. Set History

Historical Set Orders must remain associated with the applicable Set configuration/version.

---

# 78. Set Configuration Changes

Changing Set composition must not rewrite existing Orders.

---

# 79. Product and Set Relationship

A Product may be:

* standalone;
* Recipe-based;
* Set component;
* Set itself;
* used in multiple Sets.

---

# 80. Dependency Overview

Product detail should make important dependencies discoverable.

Example:

```text
Used In

Recipes: 4
Sets: 2
Branches: 5
```

---

# 81. Product Deactivation

Before deactivation, the UI should show important operational dependencies.

The user should understand the effect before confirming.

---

# 82. Product Archive Confirmation

Example:

```text
Archive Product?

Burger is referenced by:
4 Recipes
2 Sets
5 Branch Menus

Historical data will remain available.

[Cancel] [Archive]
```

---

# 83. Historical Orders

Changing Product configuration must not change:

* historical Order Item price;
* historical Product identity;
* historical Recipe Version;
* historical Set Version.

---

# 84. Product Category Change

Changing category does not create a new Product.

Historical reports requiring historical category context must use appropriate historical/report snapshots.

---

# 85. Product Image Change

Changing image does not alter historical transaction identity.

---

# 86. Product Name Change

Changing Product name does not create a new Product identity.

Historical reporting may use historical snapshots where required.

---

# 87. Product Configuration Audit

Important Product operations should be audited:

* creation;
* activation;
* deactivation;
* archive;
* category change;
* unit change;
* Recipe creation;
* Recipe modification;
* Recipe approval;
* Set configuration;
* Set approval.

---

# 88. Audit Detail

Authorized users may see:

* actor;
* timestamp;
* Business;
* Branch where applicable;
* Device;
* old state;
* new state;
* reason;
* operation UUID.

---

# 89. Offline Product Configuration

Trusted devices may use the latest valid Product/Recipe/Set configuration available locally according to offline authorization.

---

# 90. Offline Configuration Changes

Configuration-changing operations should not be assumed safe to apply offline unless explicitly allowed by the System Analysis rules.

The Frontend must follow the server-provided capability.

---

# 91. Offline Read

Offline read may use cached:

* Products;
* Categories;
* valid Recipe configuration;
* valid Set configuration.

Freshness should be visible where relevant.

---

# 92. Offline Mutation

If offline Product/Recipe/Set mutation is not supported:

```text
This action requires an online connection.
```

The UI should not simulate a successful server configuration change.

---

# 93. Synchronization

Configuration synchronization follows:

```text id="prd292"
Local State
    ↓
Sync Queue
    ↓
Server Validation
    ↓
Accepted / Rejected / Conflict
    ↓
Local State Reconciliation
```

---

# 94. Configuration Conflict

Conflict may occur when:

* another user changed the Product;
* another user created a newer Recipe Version;
* another user changed Set composition;
* local configuration became stale.

---

# 95. Conflict UI

Example:

```text
Configuration conflict

Recipe Version 4 was changed by another user.

Your local version is based on Version 3.

[Review Current Version]
[Discard Local Draft]
```

---

# 96. Conflict Resolution

Conflict resolution must:

* show current authoritative state;
* preserve the user's draft where technically possible;
* never silently overwrite newer configuration;
* require explicit resolution.

---

# 97. Optimistic Concurrency

Product/Recipe/Set configuration mutations should include the expected version.

Stale updates must return a conflict rather than silently overwriting newer data.

---

# 98. Duplicate Mutation

Repeated configuration commands must not create duplicate:

* Products;
* Recipe Versions;
* approvals;
* Set Versions.

---

# 99. Operation UUID

Retryable configuration mutations should use operation UUIDs.

The UI should retain operation identity until authoritative completion.

---

# 100. Unknown Result

If a mutation times out:

```text
The result of this operation is unknown.

Checking current configuration...
```

The Frontend should reconcile before offering a retry.

---

# 101. Subscription

Product, Recipe and Set configuration operations are subject to subscription entitlement.

When Business is read-only:

* configuration remains viewable;
* history remains viewable;
* modifications are blocked.

---

# 102. Permission UI

Actions should be determined by:

* employee status;
* role;
* permission;
* Branch scope;
* Business scope;
* subscription;
* current configuration state.

---

# 103. Hidden vs Disabled

Sensitive actions may be hidden when the user has no permission.

Important workflow actions may be shown disabled with an explanation where useful.

---

# 104. Permission Change During Session

If permissions change while the page is open:

* new permissions must be reflected;
* stale mutation actions must be rejected by Backend;
* sensitive controls should update promptly.

---

# 105. Employee Deactivation

If the employee becomes inactive:

* new configuration mutations must be blocked;
* existing historical actions remain attributed.

---

# 106. Search and Filtering Performance

Targets:

* Product search p95 ≤150 ms;
* Product list p95 ≤300 ms after API response;
* Recipe component search p95 ≤150 ms;
* Product detail p95 ≤300 ms;
* dependency navigation p95 ≤500 ms where API response is available.

---

# 107. Form Interaction Performance

Targets:

* local field feedback p95 ≤100 ms;
* component addition p95 ≤100 ms;
* local Recipe recalculation/display update p95 ≤100 ms;
* mutation acknowledgement UI p95 ≤100 ms.

Authoritative calculations remain Backend-controlled.

---

# 108. Initial Page Performance

Targets:

* Product page first useful content p75 ≤1.5 s;
* Product detail interactive p75 ≤2.0 s;
* Recipe editor interactive p75 ≤2.0 s;
* Set editor interactive p75 ≤2.0 s.

---

# 109. Error Rate

Target:

**Fatal Product/Recipe/Set UI error rate <0.1% sessions.**

---

# 110. Accessibility

Product, Recipe and Set UI must support:

* keyboard navigation;
* semantic forms;
* visible focus;
* accessible labels;
* screen reader-compatible state;
* accessible dialogs;
* accessible tables;
* non-color status indicators.

---

# 111. Recipe Editor Accessibility

Component rows must have accessible labels such as:

```text
Component Product
Quantity
Unit
Remove Component
```

---

# 112. Set Editor Accessibility

Set component rows must expose:

* Product;
* quantity;
* mandatory state;
* remove action where allowed.

---

# 113. Unsaved Changes

The UI must warn before leaving a modified Product/Recipe/Set form.

---

# 114. Draft Recovery

Where supported, temporary drafts may be retained locally.

Draft recovery must never be confused with an authoritative server configuration.

---

# 115. Product Form Validation

Client-side validation may catch:

* empty required fields;
* invalid quantity;
* invalid unit;
* duplicate component rows;
* unsupported Product type.

Backend validation remains authoritative.

---

# 116. Duplicate Recipe Components

If duplicate components are not allowed, the UI should detect them before submission.

---

# 117. Circular Dependency

The UI may warn about obvious circular dependency attempts.

The Backend must perform final dependency validation.

---

# 118. Recipe Component Removal

Removing a Recipe component from a draft does not alter the currently effective Recipe until the new version is approved/effective.

---

# 119. Set Component Removal

Removing a Set component affects only the draft/new Set Version until effective.

Historical Set Orders remain unchanged.

---

# 120. Product Detail Loading

The Product detail should load critical information first.

Secondary information such as:

* full history;
* audit;
* dependency analytics

may load later.

---

# 121. History Loading

Historical versions should use pagination where needed.

---

# 122. Large Recipe

Large Recipes should use efficient component rendering.

The Frontend should avoid unnecessary full-tree rerenders when editing one component.

---

# 123. Recipe Dependency Visualization

For complex Recipe chains, the UI may use a collapsible hierarchy.

The visualization must remain readable on ordinary screens.

---

# 124. Cost Display

If cost information is available, the UI must distinguish:

```text
Component Cost
Recipe Cost
Selling Price
```

These are different concepts.

---

# 125. Recipe Cost Calculation

The Frontend may display Backend-provided calculated cost.

It must not become the authoritative source for accounting/inventory cost.

---

# 126. Set Price

Set price belongs to the Set configuration.

Current component prices must not automatically rewrite historical Set Order prices.

---

# 127. Menu Relationship

A Product may exist without being active in a Branch Menu.

Product existence does not imply Branch sale availability.

---

# 128. Inventory Relationship

A Product may exist without current stock.

Product configuration does not imply inventory availability.

---

# 129. Operational Readiness

A Product may have the following separate states:

```text
Product:
ACTIVE

Recipe:
APPROVED

Menu:
ACTIVE

Inventory:
OUT OF STOCK
```

The UI should not collapse these into one misleading status.

---

# 130. Product Readiness Summary

A useful summary may display:

```text
Product
  ACTIVE

Recipe
  READY

Menu
  ACTIVE

Inventory
  LOW STOCK
```

---

# 131. Set Readiness Summary

Example:

```text
Set:
ACTIVE

Configuration:
EFFECTIVE

Components:
3/3 AVAILABLE

Menu:
ACTIVE
```

---

# 132. Component Availability

Availability must respect:

* Branch;
* Product state;
* Menu state;
* Inventory;
* Recipe requirements;
* equipment status where relevant.

---

# 133. No Silent State Changes

Frontend must not silently convert:

* inactive → active;
* draft → approved;
* approved → effective;
* archived → active.

These are authoritative state transitions.

---

# 134. Product Import

If future bulk import is implemented, the import UI must:

* validate rows;
* show errors;
* support preview;
* identify duplicate Products;
* preserve Business scope;
* produce an auditable operation.

---

# 135. Product Export

Product/Recipe/Set export must respect:

* permission;
* Business scope;
* Branch scope;
* subscription state.

Export should be asynchronous for large datasets.

---

# 136. Import Failure

Partial import must clearly show:

```text
Created:
94

Rejected:
6

[View Errors]
```

No partial import should be reported as fully successful.

---

# 137. Product History

History may include:

* name changes;
* category changes;
* activation changes;
* archive;
* Recipe changes;
* Set changes;
* menu/pricing references where available.

---

# 138. History Integrity

History must remain append-only according to Backend rules.

Frontend must not expose a normal action that overwrites historical versions.

---

# 139. State Ownership

Frontend state categories:

```text id="prd303"
Product Context
Product Query State
Product Form State
Recipe Draft State
Recipe Version State
Set Draft State
Permission State
Synchronization State
UI State
```

---

# 140. Authoritative State

Backend remains authoritative for:

* Product identity;
* Product lifecycle;
* Recipe Version;
* Recipe approval;
* Set Version;
* component validity;
* operational configuration;
* permission;
* subscription;
* historical state.

---

# 141. Local State

Frontend may own:

* form fields;
* temporary draft;
* selected components;
* filters;
* sorting;
* tabs;
* dialogs.

---

# 142. Cache

Product/Recipe/Set read models may be cached.

Cache must not become the source of truth.

---

# 143. Cache Invalidation

Relevant configuration caches must be invalidated after:

* Product update;
* Product activation;
* Recipe approval;
* Recipe Version creation;
* Set Version creation;
* category change;
* synchronization;
* Branch context change.

---

# 144. Business Isolation in Cache

Cache keys must include Business scope.

---

# 145. Branch Isolation in Cache

Where Branch-specific data is involved, Branch scope must be included.

---

# 146. Testing

Frontend tests should cover:

### Product

* creation;
* editing;
* activation;
* deactivation;
* archive;
* category changes;
* search;
* filters.

### Recipe

* draft;
* component management;
* versioning;
* approval;
* rejection;
* history;
* permission.

### Set

* composition;
* versioning;
* approval;
* component availability;
* no substitution.

### Security

* Business isolation;
* Branch isolation;
* permission;
* subscription.

### Offline

* cached configuration;
* mutation restriction;
* synchronization;
* conflict.

---

# 147. Integration Testing

Integration tests should verify:

* Product API contracts;
* Recipe API contracts;
* Set API contracts;
* permission responses;
* version conflict handling;
* audit integration;
* synchronization behavior.

---

# 148. Visual Testing

Important screens should have visual regression coverage:

* Product list;
* Product detail;
* Product form;
* Recipe editor;
* Recipe approval;
* Recipe history;
* Set editor;
* dependency display.

---

# 149. Observability

Frontend telemetry may track:

* Product page latency;
* Recipe editor latency;
* Set editor latency;
* mutation failures;
* conflict rate;
* approval failures;
* synchronization failures;
* fatal errors.

Sensitive Recipe/cost information must not be unnecessarily sent to telemetry.

---

# 150. Product/Recipe/Set Invariants

The following invariants are mandatory:

1. Product identity is stable.
2. Product belongs to one Business.
3. Product category is Business-scoped.
4. Product category does not create a new Product identity.
5. Product activation does not create a new Product identity.
6. Product deactivation does not delete historical data.
7. Product archive preserves historical data.
8. Historical Orders retain Product identity.
9. Historical inventory transactions retain Product identity.
10. Product image changes do not alter Product identity.
11. Product name changes do not alter Product identity.
12. Product type is Backend-authoritative.
13. Product unit is Backend-authoritative.
14. Product code is Backend-authoritative.
15. Product search respects Business scope.
16. Product search respects permissions.
17. Product lists are paginated.
18. Product mutations require authorization.
19. Inactive employees cannot create Product mutations.
20. Subscription read-only blocks Product modification.
21. Recipe composition is Backend-authoritative.
22. Recipe Versions preserve historical configuration.
23. Effective Recipe cannot be silently overwritten.
24. New Recipe changes create a new version where operational behavior changes.
25. Draft Recipe does not automatically become effective.
26. Approval is an explicit state transition.
27. Approval requires appropriate permission.
28. Editing permission does not automatically imply approval permission.
29. Rejected Recipe versions remain traceable where required.
30. Historical Recipe Versions remain available.
31. Historical inventory deductions retain their Recipe Version.
32. Current Recipe cannot reinterpret historical inventory transactions.
33. Recipe validity and stock availability are separate.
34. Recipe validity and Menu availability are separate.
35. Recipe visibility is permission-controlled.
36. Recipe cost visibility may be permission-controlled.
37. Semi-Finished Products may have Recipes.
38. Finished Products may have Recipes.
39. Raw Materials may participate in Recipes.
40. Recipe chains are validated by Backend.
41. Circular Recipe dependencies are not accepted where prohibited.
42. Unauthorized Products cannot be selected as Recipe components.
43. Recipe quantities respect supported precision.
44. Recipe units are explicit.
45. Recipe component removal from a draft does not alter effective history.
46. Set identity is stable.
47. Set composition is configuration data.
48. Set operational changes are versioned where required.
49. Set approval is permission-controlled.
50. Set price is separate from component Product prices.
51. Historical Set Orders retain historical Set configuration.
52. Historical Set Orders retain historical price.
53. Set component substitution is prohibited during normal sale.
54. Mandatory unavailable components block Set availability.
55. Set availability is Branch-aware.
56. Product existence does not imply Menu availability.
57. Product existence does not imply inventory availability.
58. Recipe readiness does not imply stock availability.
59. Inventory state remains Backend-authoritative.
60. Menu state remains Backend-authoritative.
61. Product state remains Backend-authoritative.
62. Recipe state remains Backend-authoritative.
63. Set state remains Backend-authoritative.
64. Frontend does not independently authorize final configuration changes.
65. Frontend does not independently determine historical truth.
66. Configuration mutations use operation UUID where retryable.
67. Duplicate configuration requests do not create duplicate versions.
68. Unknown mutation results are reconciled.
69. Stale configuration updates return conflicts.
70. Silent last-write-wins is prohibited for important configuration.
71. Conflict resolution is explicit.
72. Conflict resolution preserves historical values.
73. Important configuration changes are audited.
74. Audit records remain immutable.
75. Branch-specific context cannot cross Branch boundaries.
76. Business-specific context cannot cross Business boundaries.
77. Offline configuration uses only authorized local state.
78. Offline mode cannot grant new permission.
79. Offline mode cannot bypass subscription restrictions.
80. Offline mutations are supported only where explicitly allowed.
81. Unsupported offline mutation is clearly presented as requiring online access.
82. Cached configuration is not authoritative.
83. Cache is Business-isolated.
84. Branch-specific cache is Branch-isolated.
85. Cache invalidation follows authoritative changes.
86. Product forms protect unsaved changes.
87. Recipe forms protect unsaved changes.
88. Set forms protect unsaved changes.
89. Context changes cannot submit stale configuration.
90. Duplicate clicks cannot create duplicate configuration.
91. Client validation improves UX but does not replace Backend validation.
92. Errors expose recovery guidance.
93. Temporary failures can be retried when safe.
94. Permanent failures are not blindly retried.
95. Import results expose partial failures.
96. Export respects authorization.
97. Export does not block normal Product operations.
98. Large Product catalogs use pagination.
99. Large Recipe graphs use bounded/lazy loading.
100. Large history lists use pagination.
101. Product search target is p95 ≤150 ms.
102. Product list target is p95 ≤300 ms after API response.
103. Product detail target is p95 ≤300 ms.
104. Recipe component search target is p95 ≤150 ms.
105. Local editor interaction target is p95 ≤100 ms.
106. Product page first useful content target is p75 ≤1.5 s.
107. Product detail interactive target is p75 ≤2.0 s.
108. Recipe editor interactive target is p75 ≤2.0 s.
109. Set editor interactive target is p75 ≤2.0 s.
110. Fatal Product/Recipe/Set UI error rate target is <0.1% sessions.
111. Accessibility is mandatory.
112. Status is not communicated only through color.
113. Keyboard operation is supported.
114. Screen reader state is supported.
115. Product configuration remains attributable to the responsible actor.
116. Recipe approval remains attributable to the approver.
117. Set approval remains attributable to the approver.
118. Device context is retained for important configuration operations.
119. Historical configuration is reconstructable.
120. Current configuration cannot reinterpret historical transactions.
121. Product, Recipe and Set UI uses centralized API/data boundaries.
122. Feature components do not directly access persistence.
123. Product, Recipe and Set state remains compatible with offline-first architecture.
124. Product, Recipe and Set state remains compatible with synchronization architecture.
125. Product, Recipe and Set state remains compatible with Menu and Pricing architecture.
126. Product, Recipe and Set state remains compatible with Inventory architecture.
127. Product configuration prioritizes historical integrity over UI convenience.
128. Security prioritizes authorization over client-side convenience.
129. Backend remains the final authority for all operational configuration.
130. Product, Recipe and Set architecture supports future expansion without breaking historical identity.

---

# 151. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
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
* `docs/05_Database/20_Audit_and_History_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/11_Inventory_and_Warehouse.md`
* `docs/02_System_Analysis/12_Products_and_Recipes.md`
* `docs/02_System_Analysis/13_Menu_and_Pricing.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 152. Status

**Document:** `13_Products_Recipes_and_Sets_UI.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `12_Inventory_and_Warehouse_UI.md`

**Next Document:** `14_Menu_and_Pricing_UI.md`

