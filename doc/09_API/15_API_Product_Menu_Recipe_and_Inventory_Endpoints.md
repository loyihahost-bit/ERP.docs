# API Product, Menu, Recipe and Inventory Endpoints

**Document ID:** API-15
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the public API contract for Product, Category, Menu, Recipe, Set, Inventory and Warehouse operations in FastFood ERP.

The API must provide a clear separation between:

* Business-level product configuration;
* Branch-level menu availability;
* Product pricing;
* Recipe configuration;
* Recipe versions;
* Set configuration;
* Inventory state;
* Warehouse state;
* Inventory transactions;
* stock availability;
* purchasing information;
* low-stock and shopping-list information;
* equipment availability.

The API must expose business capabilities rather than database tables.

All authoritative state remains server-side.

---

# 2. Scope

This document covers:

* Product endpoints;
* Category endpoints;
* Product activation and archival;
* Business-level product configuration;
* Branch menu configuration;
* Product availability;
* Product pricing;
* Branch price overrides;
* Recipe endpoints;
* Recipe version endpoints;
* Recipe submission and approval;
* Recipe archival;
* Set endpoints;
* Set versioning;
* Set component configuration;
* Warehouse endpoints;
* Inventory balance endpoints;
* Inventory transaction endpoints;
* Stock receiving;
* Stock issue;
* Stock adjustment;
* Inventory counting;
* Low-stock information;
* Shopping-list information;
* Equipment availability;
* Product availability validation;
* FIFO-related inventory information;
* Last Purchase Cost;
* inventory cost information;
* offline configuration compatibility;
* synchronization;
* authorization;
* concurrency;
* idempotency;
* audit;
* historical integrity;
* performance;
* API errors.

Generic API principles, authentication, authorization, validation, errors, idempotency and pagination are defined in earlier API documents.

---

# 3. Architectural Position

The endpoint flow follows the standard API architecture:

```text
Client
   ↓
API
   ↓
Authentication
   ↓
Authorization
   ↓
Business / Branch Scope
   ↓
Request Validation
   ↓
Application Use Case
   ↓
Domain Rules
   ↓
Repository
   ↓
PostgreSQL
```

The API does not directly manipulate Product, Recipe or Inventory database records.

---

# 4. Resource Model

The main resources are:

```text
Business
 ├── Category
 ├── Product
 │    ├── Recipe
 │    │    └── Recipe Version
 │    └── Set
 │         └── Set Version
 │
 ├── Global Menu
 │
 └── Branch
      ├── Branch Menu
      ├── Branch Product Configuration
      ├── Warehouse
      └── Inventory
           └── Inventory Transactions
```

The same Product identity may be used across multiple Branches.

Branch-specific configuration must not create duplicate Product identities.

---

# 5. Resource Identity

Products, Categories, Recipes, Recipe Versions, Sets, Warehouses and Inventory Transactions use server-generated UUIDs.

Example:

```json
{
  "id": "018f7e7c-..."
}
```

A UUID identifies a resource.

It does not provide authorization.

The server must validate:

* Business ownership;
* Branch scope;
* resource state;
* employee permission;
* subscription state;
* operational rules.

---

# 6. Product Resource

A Product represents a sellable or operational inventory/menu item.

A Product may represent:

* raw material;
* semi-finished product;
* finished product.

The Product type must be explicit.

Example:

```json
{
  "id": "018f...",
  "name": "Chicken Burger",
  "product_type": "FINISHED",
  "category_id": "018f...",
  "active": true
}
```

---

# 7. Product Types

Initial Product types:

```text
RAW_MATERIAL
SEMI_FINISHED
FINISHED
```

The API must reject unsupported Product types.

Product type changes are controlled configuration operations and must preserve historical integrity.

---

# 8. Product Creation

Endpoint:

```http
POST /api/v1/products
```

Example request:

```json
{
  "name": "Chicken Burger",
  "product_type": "FINISHED",
  "category_id": "018f...",
  "unit": "PCS"
}
```

The server generates:

* Product UUID;
* creation timestamp;
* Business scope;
* initial configuration version where required.

The client must not determine authoritative Business ownership.

---

# 9. Product Read

Endpoint:

```http
GET /api/v1/products/{product_id}
```

The response may include:

```text
Product identity
Product type
Category
Unit
Active state
Recipe requirement
Set status
Creation metadata
Current configuration version
```

Sensitive administrative information must only be returned when authorized.

---

# 10. Product List

Endpoint:

```http
GET /api/v1/products
```

Supported filters may include:

```text
category_id
product_type
active
search
has_recipe
branch_id
```

The server must enforce Business and Branch scope.

Large results use the pagination rules defined in:

`11_API_Pagination_Search_Filtering_and_Sorting.md`

---

# 11. Product Update

Endpoint:

```http
PATCH /api/v1/products/{product_id}
```

Only permitted configuration fields may be changed.

The endpoint must not allow arbitrary modification of:

* historical prices;
* historical Recipe Versions;
* historical inventory transactions;
* historical Order snapshots.

Important state changes should use explicit commands.

---

# 12. Product Activation

Endpoint:

```http
POST /api/v1/products/{product_id}/activate
```

Activation requires appropriate permission.

The operation must validate:

* Business scope;
* employee status;
* subscription;
* product state;
* required configuration.

Activation does not automatically make the Product available at every Branch.

---

# 13. Product Deactivation

Endpoint:

```http
POST /api/v1/products/{product_id}/deactivate
```

A deactivated Product cannot be newly sold.

Historical data remains available.

The operation must not:

* delete inventory history;
* delete Orders;
* delete Recipe history;
* rewrite historical prices.

---

# 14. Product Archival

Endpoint:

```http
POST /api/v1/products/{product_id}/archive
```

Products with historical or Recipe dependencies should be archived rather than physically deleted.

Archive preserves:

* Product identity;
* historical Orders;
* inventory history;
* Recipe history;
* Set history;
* audit history.

---

# 15. Product Deletion

Physical Product deletion is generally prohibited when dependencies exist.

The API may return:

```text
PRODUCT_HAS_HISTORICAL_DEPENDENCIES
```

Instead, the client should use:

```text
POST /products/{id}/archive
```

Deletion behavior must follow the Data Lifecycle architecture.

---

# 16. Category Endpoints

Typical endpoints:

```text
GET    /api/v1/categories
POST   /api/v1/categories
GET    /api/v1/categories/{category_id}
PATCH  /api/v1/categories/{category_id}
POST   /api/v1/categories/{category_id}/archive
```

A Product belongs to exactly one menu category.

---

# 17. Category Assignment

Product category changes must not create a new Product identity.

Example:

```http
PATCH /api/v1/products/{product_id}
```

```json
{
  "category_id": "018f..."
}
```

The operation must preserve historical reporting context where required.

---

# 18. Category Archive

A category with active Products may require reassignment before archival.

The API must not silently orphan Products.

Possible error:

```text
CATEGORY_HAS_ACTIVE_PRODUCTS
```

---

# 19. Global Menu

The Business owns the Global Menu.

The Global Menu defines which Products are commercially configured by the Business.

Typical endpoint:

```http
GET /api/v1/menu
```

Administrative operations may include:

```http
POST /api/v1/menu/products/{product_id}/enable
POST /api/v1/menu/products/{product_id}/disable
```

Global Menu state is distinct from Branch availability.

---

# 20. Branch Menu

Branch-specific menu configuration is represented separately.

Typical endpoints:

```http
GET /api/v1/branches/{branch_id}/menu
GET /api/v1/branches/{branch_id}/menu/products/{product_id}
PATCH /api/v1/branches/{branch_id}/menu/products/{product_id}
```

The Branch configuration affects only that Branch.

---

# 21. Branch Product Availability

A Branch may enable or disable a Product.

Example:

```http
POST /api/v1/branches/{branch_id}/menu/products/{product_id}/enable
```

and:

```http
POST /api/v1/branches/{branch_id}/menu/products/{product_id}/disable
```

Disabling a Product in Branch A must not affect Branch B.

---

# 22. Menu Availability vs Stock

Menu availability and stock availability are separate.

A Product may be:

```text
Menu Enabled + In Stock
Menu Enabled + Out of Stock
Menu Disabled + In Stock
Menu Disabled + Equipment Unavailable
```

The API must not treat menu activation as proof of stock availability.

---

# 23. Effective Menu

The API may expose the effective Branch menu:

```http
GET /api/v1/branches/{branch_id}/menu/effective
```

The response should contain only information required by the client.

Example:

```json
{
  "configuration_version": 12,
  "products": [
    {
      "product_id": "018f...",
      "name": "Chicken Burger",
      "category_id": "018f...",
      "price": "30000.00",
      "available": true
    }
  ]
}
```

The effective menu is derived from authoritative configuration.

---

# 24. Configuration Version

Effective menu responses should expose a configuration version.

Example:

```json
{
  "configuration_version": 12
}
```

Clients may use this value to detect stale configuration.

Configuration versioning follows:

`18_Menu_Pricing_and_Configuration.md`

and:

`10_API_Idempotency_and_Concurrency.md`

---

# 25. Product Pricing

Product pricing endpoints:

```http
GET   /api/v1/products/{product_id}/price
PATCH /api/v1/products/{product_id}/price
```

The Business-level standard price is separate from inventory cost.

---

# 26. Branch Price Override

Endpoint:

```http
PATCH /api/v1/branches/{branch_id}/products/{product_id}/price
```

The Branch override:

* affects only that Branch;
* does not change the global price;
* does not affect other Branches;
* requires explicit permission.

---

# 27. Price Effective Boundary

Price configuration changes become operational according to the configured Cash Session boundary.

Therefore:

```text
Current Cash Session
    ↓
Current effective price

New configuration
    ↓
Next Cash Session
    ↓
New effective price
```

The API must not cause an active POS session to silently switch price configuration.

---

# 28. Price Snapshot

When a Product is added to an Order, the Order Item stores the applicable price snapshot.

Therefore:

```text
Current Product Price
        ≠
Existing Order Item Price
```

This API must never modify existing Order Item financial snapshots.

Financial API behavior is defined in:

`14_API_Payment_Cash_and_Financial_Endpoints.md`

---

# 29. Last Purchase Cost

The API may expose the current Last Purchase Cost where authorized.

Example:

```http
GET /api/v1/products/{product_id}/cost
```

The response may contain:

```json
{
  "product_id": "018f...",
  "last_purchase_cost": "18000.00",
  "currency": "UZS",
  "as_of": "2026-10-07T10:00:00Z"
}
```

Last Purchase Cost is an inventory cost concept.

It is not the Product selling price.

---

# 30. Cost Data Authorization

Cost information may be restricted because it can reveal sensitive Business information.

The API must validate appropriate permissions before exposing:

* purchase cost;
* FIFO cost;
* average cost;
* supplier-related cost information.

---

# 31. Custom Markup

Where the Product pricing API supports transaction-specific custom markup, the server calculates the result from applicable Last Purchase Cost.

Allowed markup:

```text
0% – 100%
```

The client may provide:

```json
{
  "markup_percent": "20.00"
}
```

The server calculates the authoritative result.

The client must not provide an authoritative final price.

---

# 32. Recipe Resource

A Recipe defines the components required to produce or sell a Product.

Example relationship:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

A Recipe may contain:

* component Product;
* quantity;
* unit;
* optional yield/loss information;
* effective version.

---

# 33. Recipe Endpoints

Typical endpoints:

```text
GET  /api/v1/products/{product_id}/recipe
POST /api/v1/products/{product_id}/recipes
GET  /api/v1/recipes/{recipe_id}
PATCH /api/v1/recipes/{recipe_id}
POST /api/v1/recipes/{recipe_id}/submit
POST /api/v1/recipes/{recipe_id}/approve
POST /api/v1/recipes/{recipe_id}/archive
GET  /api/v1/recipes/{recipe_id}/versions
```

Exact permissions are enforced by the authorization layer.

---

# 34. Recipe Creation

Creating a Recipe does not automatically make it active.

A Recipe may initially exist in:

```text
DRAFT
```

The API must validate:

* Product scope;
* component Product scope;
* quantity;
* unit compatibility;
* dependency validity;
* circular dependency rules.

---

# 35. Recipe Components

Example:

```json
{
  "components": [
    {
      "product_id": "raw-meat-id",
      "quantity": "1.000",
      "unit": "KG"
    },
    {
      "product_id": "mayonnaise-id",
      "quantity": "0.200",
      "unit": "KG"
    }
  ]
}
```

The API must validate that each component belongs to the same Business.

Cross-Business Recipe references are prohibited.

---

# 36. Recipe Circular Dependency

The system must prevent invalid circular Recipes.

Example:

```text
A → B
B → C
C → A
```

Such configuration must be rejected.

Possible error:

```text
RECIPE_CIRCULAR_DEPENDENCY
```

---

# 37. Recipe Version

Every operational Recipe configuration must have a version.

Example:

```json
{
  "recipe_id": "018f...",
  "version": 3,
  "status": "APPROVED"
}
```

Historical versions remain immutable.

---

# 38. Recipe Version Endpoint

Endpoint:

```http
GET /api/v1/recipes/{recipe_id}/versions
```

The response may include:

* version;
* status;
* created_at;
* created_by;
* approved_at;
* approved_by;
* effective_at;
* components.

Historical Recipe Versions must not be silently modified.

---

# 39. Recipe Submission

Endpoint:

```http
POST /api/v1/recipes/{recipe_id}/submit
```

Submission moves a valid draft toward approval.

The API validates completeness before submission.

---

# 40. Recipe Approval

Endpoint:

```http
POST /api/v1/recipes/{recipe_id}/approve
```

Approval requires explicit permission.

The approved version becomes eligible for operational use according to configuration rules.

The approval event must be auditable.

---

# 41. Recipe Rejection

Where approval workflow supports rejection:

```http
POST /api/v1/recipes/{recipe_id}/reject
```

The request should include a reason.

Rejected configuration must not become operational.

---

# 42. Recipe Archive

Endpoint:

```http
POST /api/v1/recipes/{recipe_id}/archive
```

Archiving does not delete historical Recipe Versions.

An archived Recipe cannot become operational unless a new valid configuration is explicitly created and approved.

---

# 43. Recipe and Product Sale

If a Product requires a Recipe, normal sale requires a valid applicable approved Recipe Version.

The API must reject sale-related operations when Recipe requirements are not satisfied.

Possible error:

```text
RECIPE_NOT_APPROVED
```

---

# 44. Recipe and Historical Inventory

Inventory deductions must retain the Recipe Version used at the time.

Example:

```text
Order
 ↓
Recipe Version 4
 ↓
Inventory deduction
```

Later Recipe Version 5 must not reinterpret the historical deduction.

---

# 45. Recipe Quantity Validation

Recipe component quantities must:

* be positive where required;
* use supported units;
* respect precision rules;
* remain within configured limits.

Zero or negative component quantities must be rejected unless explicitly supported by a future business rule.

---

# 46. Recipe Yield and Loss

Where yield/loss is configured, the API must validate the values before approval.

Yield/loss configuration must be versioned with the Recipe Version.

Historical inventory operations must retain the applicable historical values.

---

# 47. Set Resource

A Set represents a group of Products sold as one configured commercial item.

A Set has:

* its own identity;
* its own configuration;
* its own selling price;
* component Products.

---

# 48. Set Endpoints

Typical endpoints:

```text
GET  /api/v1/sets
POST /api/v1/sets
GET  /api/v1/sets/{set_id}
PATCH /api/v1/sets/{set_id}
POST /api/v1/sets/{set_id}/archive
GET  /api/v1/sets/{set_id}/versions
POST /api/v1/sets/{set_id}/versions
POST /api/v1/sets/{set_id}/versions/{version}/approve
```

---

# 49. Set Version

Operational Set composition should be versioned when configuration changes affect behavior.

Example:

```json
{
  "set_id": "018f...",
  "version": 2,
  "components": [
    {
      "product_id": "018f...",
      "quantity": 1
    }
  ]
}
```

Historical Set Orders retain the applicable Set configuration.

---

# 50. Set Component Substitution

Component substitution is prohibited during normal sale.

The API must not provide a generic endpoint allowing a cashier to replace a Set component unless a future business rule explicitly introduces such functionality.

---

# 51. Set Availability

A Set is operationally available only when:

* Set is active;
* applicable Set Version is valid;
* Branch menu allows it;
* mandatory components are available;
* required inventory exists.

---

# 52. Warehouse Resource

A Warehouse represents an inventory storage location associated with a Branch or supported Business scope.

Typical endpoints:

```http
GET  /api/v1/warehouses
POST /api/v1/warehouses
GET  /api/v1/warehouses/{warehouse_id}
PATCH /api/v1/warehouses/{warehouse_id}
POST /api/v1/warehouses/{warehouse_id}/archive
```

Warehouse scope must be explicit.

---

# 53. Warehouse Isolation

A Branch Warehouse must belong to the correct Business and Branch.

The API must reject:

```text
Business A Product
+
Business B Warehouse
```

and:

```text
Branch A Inventory
+
Branch B Warehouse
```

---

# 54. Inventory Balance

Endpoint:

```http
GET /api/v1/inventory
```

Possible filters:

```text
warehouse_id
product_id
product_type
low_stock
out_of_stock
```

The response represents current inventory state.

---

# 55. Inventory Balance Read

Example:

```json
{
  "product_id": "018f...",
  "warehouse_id": "018f...",
  "quantity": "12.500",
  "unit": "KG",
  "available": true
}
```

Inventory balance is authoritative on the server.

Cached or client-side quantities are informational only.

---

# 56. Inventory Availability

Endpoint:

```http
GET /api/v1/inventory/availability
```

Example query:

```text
GET /api/v1/inventory/availability?product_id=...&quantity=2
```

The result may indicate:

```json
{
  "product_id": "018f...",
  "requested": "2.000",
  "available": "5.000",
  "sufficient": true
}
```

This endpoint is informational.

Final inventory validation occurs inside the authoritative transaction.

---

# 57. Inventory Receiving

Endpoint:

```http
POST /api/v1/inventory/receipts
```

Example:

```json
{
  "warehouse_id": "018f...",
  "items": [
    {
      "product_id": "018f...",
      "quantity": "20.000",
      "unit_cost": "15000.00",
      "source": "PURCHASED",
      "date": "2026-10-07"
    }
  ]
}
```

The server validates:

* Product;
* Warehouse;
* Business;
* Branch;
* quantity;
* cost;
* permission;
* source.

---

# 58. Inventory Receipt Sources

Initial source values:

```text
PURCHASED
PREPARED_IN_BRANCH
```

The source is retained as part of the inventory transaction.

---

# 59. Inventory Issue

Endpoint:

```http
POST /api/v1/inventory/issues
```

Used for authorized inventory exits not directly generated by normal Product sale.

Example:

```json
{
  "warehouse_id": "018f...",
  "items": [
    {
      "product_id": "018f...",
      "quantity": "2.000",
      "reason": "INTERNAL_USE"
    }
  ]
}
```

The server must validate sufficient stock.

Negative inventory is prohibited.

---

# 60. Inventory Adjustment

Endpoint:

```http
POST /api/v1/inventory/adjustments
```

Adjustments are used to correct verified inventory discrepancies.

An adjustment must include:

* Product;
* Warehouse;
* quantity change;
* reason;
* actor;
* operation UUID.

The adjustment must not rewrite previous transactions.

---

# 61. Inventory Count

Endpoint:

```http
POST /api/v1/inventory/counts
```

The count records observed physical stock.

A count does not silently overwrite authoritative inventory history.

The resulting discrepancy may produce a separate adjustment transaction.

---

# 62. Inventory Transaction History

Endpoint:

```http
GET /api/v1/inventory/transactions
```

Supported filters may include:

```text
product_id
warehouse_id
transaction_type
from
to
source
employee_id
```

Results must be paginated.

Historical transactions are immutable.

---

# 63. Inventory Transaction Types

Typical transaction types:

```text
RECEIPT
SALE
ISSUE
ADJUSTMENT
RETURN
TRANSFER
PRODUCTION
WASTE
COUNT_CORRECTION
```

Only supported types may be created through the API.

Some types may only be generated by internal business workflows.

---

# 64. Sale-Generated Inventory Transactions

Normal Product sales should not allow clients to directly create arbitrary `SALE` inventory transactions.

The Order/Inventory application workflow creates the authoritative transaction.

This prevents clients from bypassing:

* Order state;
* Recipe;
* stock validation;
* financial state;
* audit.

---

# 65. Recipe-Generated Inventory Deduction

When a Product with a Recipe is sold:

```text
Order
  ↓
Approved Recipe Version
  ↓
Required components
  ↓
Inventory validation
  ↓
Inventory deduction
```

The API must not rely on a client-provided list of components.

The server derives components from the authoritative Recipe Version.

---

# 66. Semi-Finished Product Production

A semi-finished Product may be produced in a Branch.

The API may expose:

```http
POST /api/v1/inventory/production
```

The server derives required raw materials from the applicable Recipe Version.

Example:

```text
Raw Materials
    ↓
Recipe
    ↓
Semi-Finished Product
```

The operation must preserve the Recipe Version used.

---

# 67. FIFO Information

FIFO is an inventory accounting/valuation rule.

Where FIFO information is exposed:

```http
GET /api/v1/inventory/{product_id}/cost-layers
```

the API must treat cost layers as server-generated data.

Clients must not directly modify FIFO layers.

---

# 68. Cost Layers

A cost-layer response may include:

```json
{
  "product_id": "018f...",
  "layers": [
    {
      "quantity": "10.000",
      "unit_cost": "15000.00",
      "remaining": "4.000"
    }
  ]
}
```

The exact representation is subject to the database and accounting model.

---

# 69. Average Cost

If Average Cost is exposed:

```http
GET /api/v1/inventory/{product_id}/average-cost
```

it is a derived server-side value.

It must not be used by clients to overwrite authoritative inventory state.

---

# 70. Low Stock

Endpoint:

```http
GET /api/v1/inventory/low-stock
```

The result identifies Products at or below configured thresholds.

Example:

```json
{
  "product_id": "018f...",
  "quantity": "2.000",
  "threshold": "5.000"
}
```

Low-stock information is operational guidance.

---

# 71. Out of Stock

Endpoint:

```http
GET /api/v1/inventory/out-of-stock
```

A Product is out of stock when the authoritative available quantity does not satisfy required sale quantity.

This state must not be confused with menu deactivation.

---

# 72. Shopping List

The shopping list is advisory.

Typical endpoints:

```text
GET  /api/v1/inventory/shopping-list
POST /api/v1/inventory/shopping-list/items
PATCH /api/v1/inventory/shopping-list/items/{id}
POST /api/v1/inventory/shopping-list/items/{id}/complete
```

The shopping list does not itself increase inventory.

Actual receiving requires an inventory receipt operation.

---

# 73. Shopping List Generation

The system may generate shopping-list suggestions based on:

* low stock;
* out-of-stock state;
* expected demand;
* manually configured requirements.

Generated suggestions must remain distinguishable from confirmed purchases.

---

# 74. Equipment Availability

Products may become temporarily unavailable because required equipment is unavailable.

Endpoint:

```http
POST /api/v1/branches/{branch_id}/products/{product_id}/equipment-unavailable
```

and:

```http
POST /api/v1/branches/{branch_id}/products/{product_id}/equipment-available
```

The state must not change:

* Product identity;
* Recipe history;
* inventory history;
* historical Order prices.

---

# 75. Product Operational Availability

A Product's effective operational availability may depend on:

```text
Business Product State
+
Branch Menu State
+
Inventory State
+
Recipe State
+
Equipment State
+
Subscription State
```

The API may expose the derived state for POS use.

The derived state does not replace authoritative source records.

---

# 76. Effective Product State

Example:

```json
{
  "product_id": "018f...",
  "menu_enabled": true,
  "inventory_available": false,
  "recipe_valid": true,
  "equipment_available": true,
  "sellable": false
}
```

The final `sellable` decision remains server-side.

---

# 77. POS Product Availability

Endpoint:

```http
GET /api/v1/branches/{branch_id}/products/available-for-sale
```

This endpoint is optimized for POS read operations.

It should return compact data.

It must not require the client to reconstruct complex Recipe or Inventory rules itself.

---

# 78. Inventory and Order Boundary

The Product/Inventory API provides availability information.

The Order acceptance operation remains authoritative for final inventory validation.

Therefore:

```text
Availability Read
      ↓
Informational

Order Acceptance
      ↓
Authoritative Inventory Validation
```

---

# 79. Branch Transfers

If Branch-to-Branch inventory transfers are supported, they must be represented as explicit inventory operations.

Typical endpoints:

```http
POST /api/v1/inventory/transfers
GET  /api/v1/inventory/transfers/{transfer_id}
POST /api/v1/inventory/transfers/{transfer_id}/receive
POST /api/v1/inventory/transfers/{transfer_id}/cancel
```

The transfer must remain within the same Business unless future functionality explicitly permits otherwise.

---

# 80. Transfer State

Possible states:

```text
DRAFT
REQUESTED
IN_TRANSIT
RECEIVED
CANCELLED
```

State transitions must be server-controlled.

---

# 81. Inventory Return

Inventory returns may be created through:

```http
POST /api/v1/inventory/returns
```

The operation must identify:

* original transaction where applicable;
* Product;
* quantity;
* Warehouse;
* reason;
* actor.

A return must not rewrite the original inventory transaction.

---

# 82. Inventory and Subscription

When a Business enters `READ_ONLY`:

Allowed:

* inventory viewing;
* historical inventory viewing;
* reports;
* permitted exports.

Blocked:

* receiving;
* issuing;
* adjustment;
* production;
* transfer;
* other inventory mutations.

Offline devices cannot bypass the restriction.

---

# 83. Inventory and Employee Status

Inactive employees cannot create new inventory mutations.

Historical inventory transactions remain attributed to the original actor.

---

# 84. Inventory Authorization

Inventory permissions may include:

```text
inventory.view
inventory.receive
inventory.issue
inventory.adjust
inventory.count
inventory.transfer
inventory.production
inventory.cost.view
inventory.history.view
```

Exact permission names remain implementation-defined.

The API must use the centralized authorization model.

---

# 85. Recipe Authorization

Recipe permissions may include:

```text
recipe.view
recipe.create
recipe.edit
recipe.submit
recipe.approve
recipe.archive
recipe.history.view
```

Recipe visibility may be restricted.

A user authorized to sell a Product does not automatically gain Recipe management authority.

---

# 86. Product Authorization

Product permissions may include:

```text
product.view
product.create
product.edit
product.activate
product.archive
product.price.edit
product.category.edit
```

Branch-specific permissions must be evaluated according to the employee's Branch scope.

---

# 87. Menu Authorization

Menu permissions may include:

```text
menu.view
menu.edit
menu.branch.edit
menu.price.edit
menu.availability.edit
```

Global menu permissions and Branch menu permissions are distinct.

---

# 88. Cost Visibility

Cost information should normally be restricted to roles or employees with appropriate permissions.

A POS cashier should not automatically receive:

* supplier cost;
* FIFO layers;
* Average Cost;
* Last Purchase Cost

unless explicitly authorized.

The POS response should contain only the fields required for its workflow.

---

# 89. Offline Product Configuration

Trusted offline devices may store the latest valid authorized:

* Product configuration;
* Branch menu;
* effective price;
* Recipe-related operational data required for sale;
* availability configuration.

The local state remains non-authoritative.

---

# 90. Offline Inventory

Offline devices may maintain local inventory projections for operational continuity.

However, final inventory authority remains server-side after synchronization.

Offline transactions must include:

```text
operation_id
device_id
employee_id
branch_id
business_id
entity_id
operation_type
client_created_at
```

The server validates the operation during synchronization.

---

# 91. Offline Configuration Version

Offline configuration must identify the configuration version used.

Example:

```json
{
  "configuration_version": 12
}
```

This allows the server to determine whether the operation was created against an older configuration.

---

# 92. Offline Recipe Version

Offline Product operations requiring Recipe information must retain the Recipe Version used locally.

Example:

```json
{
  "recipe_version": 4
}
```

Historical inventory processing must preserve that version.

---

# 93. Offline Stale Configuration

A stale offline configuration does not automatically invalidate historical transactions already created under that configuration.

However, after synchronization:

* server state becomes authoritative;
* new local operations use the latest valid configuration;
* conflicts are explicitly resolved.

---

# 94. Synchronization Priority

Transaction synchronization has priority over configuration synchronization.

Example:

```text
Offline Sale
   ↓
Transaction Synchronization
   ↓
Inventory/Order Validation
   ↓
Configuration Synchronization
```

A new server price must not rewrite an offline-created Order Item price.

---

# 95. Inventory Synchronization

Inventory-related offline operations must use stable operation UUIDs.

Duplicate delivery of the same operation must not duplicate:

* inventory receipt;
* inventory issue;
* production;
* adjustment;
* transfer.

---

# 96. Inventory Concurrency

Inventory mutations require authoritative concurrency control.

For example:

```text
Stock = 5

Transaction A requires 4
Transaction B requires 3
```

The system must not allow both operations to consume 7 units.

The authoritative transaction must serialize or otherwise safely coordinate the inventory state.

---

# 97. Negative Inventory Prevention

The API must reject any authoritative inventory operation that would result in negative stock.

Possible error:

```text
INSUFFICIENT_STOCK
```

This validation must occur inside the authoritative transaction.

---

# 98. Inventory Adjustment Integrity

An adjustment must create a new transaction.

It must not:

* edit the original receipt;
* edit the original sale;
* overwrite historical quantity;
* delete transaction history.

---

# 99. Recipe Change Integrity

Changing a Recipe creates a new operational configuration/version where required.

It must not modify historical Recipe Versions.

Historical inventory deductions continue to reference their original Recipe Version.

---

# 100. Menu Change Integrity

Disabling a Product at a Branch does not invalidate existing historical Orders.

Existing open Orders retain their snapshots.

New Order Items must use the current effective Branch menu.

---

# 101. Product Price Integrity

Current Product price must never reinterpret:

* historical Orders;
* historical refunds;
* historical inventory transactions;
* historical reports.

---

# 102. Configuration Concurrency

Important Product, Menu, Pricing and Recipe updates should use optimistic concurrency.

Example:

```http
If-Match: "12"
```

If current version is `13`:

```text
409 Conflict
STALE_VERSION
```

The server must not silently overwrite the newer configuration.

---

# 103. Idempotency

Retryable mutations should accept:

```http
Idempotency-Key: <operation_uuid>
```

Examples:

* Product activation;
* Recipe approval;
* inventory receipt;
* inventory adjustment;
* inventory transfer;
* production;
* menu configuration change.

Duplicate requests must not create duplicate authoritative effects.

---

# 104. Inventory Batch Operations

Bulk inventory operations may be supported.

Example:

```http
POST /api/v1/inventory/receipts/batch
```

Batch size must remain bounded.

Each item must be independently validated.

Large batches must not create unbounded transactions or memory usage.

---

# 105. Partial Batch Results

Where operations can succeed independently, the API may return per-item results.

Example:

```json
{
  "results": [
    {
      "operation_id": "018f...",
      "status": "ACCEPTED"
    },
    {
      "operation_id": "018f...",
      "status": "INSUFFICIENT_STOCK"
    }
  ]
}
```

Retry behavior follows the generic API batch rules.

---

# 106. Inventory Error Codes

Relevant error codes include:

```text
PRODUCT_NOT_FOUND
PRODUCT_INACTIVE
PRODUCT_ARCHIVED
CATEGORY_NOT_FOUND
CATEGORY_HAS_ACTIVE_PRODUCTS
MENU_PRODUCT_DISABLED
BRANCH_MENU_NOT_CONFIGURED
RECIPE_NOT_FOUND
RECIPE_NOT_APPROVED
RECIPE_CIRCULAR_DEPENDENCY
RECIPE_VERSION_CONFLICT
SET_NOT_FOUND
SET_VERSION_NOT_APPROVED
SET_COMPONENT_UNAVAILABLE
WAREHOUSE_NOT_FOUND
WAREHOUSE_SCOPE_DENIED
INSUFFICIENT_STOCK
NEGATIVE_STOCK_NOT_ALLOWED
INVALID_INVENTORY_QUANTITY
INVALID_UNIT
INVALID_COST
INVENTORY_VERSION_CONFLICT
INVENTORY_OPERATION_DUPLICATE
EQUIPMENT_UNAVAILABLE
STALE_CONFIGURATION
PRODUCT_NOT_SELLABLE
```

The canonical error architecture remains defined in:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 107. Response Security

Product and Inventory responses must expose only authorized information.

For example:

```text
POS
→ name, price, availability

Manager
→ operational inventory

Owner
→ cost, inventory history, configuration

Restricted employee
→ only explicitly permitted data
```

The exact field-level authorization depends on the centralized security model.

---

# 108. API Caching

Safe read-oriented resources may be cached:

* Product catalog;
* Category list;
* effective menu;
* effective price;
* approved Recipe metadata;
* reference data.

Authoritative inventory mutation must never depend on cache.

---

# 109. Cache Versioning

Cached configuration should include:

```text
Business ID
Branch ID where applicable
Product ID
Configuration Version
```

Example:

```text
menu:v2:{business_id}:{branch_id}:{configuration_version}
```

The cache architecture is defined in:

`14_Backend_Caching_and_Performance_Architecture.md`

---

# 110. Inventory Cache Restriction

Cached stock may be used for:

* display;
* preliminary availability;
* POS optimization.

It must not be used as the final authority for stock deduction.

Final validation occurs against PostgreSQL inside the business transaction.

---

# 111. Historical Inventory Reads

Historical inventory endpoints must return immutable transaction information.

Example:

```http
GET /api/v1/inventory/transactions/{transaction_id}
```

The response should preserve:

* Product;
* quantity;
* unit;
* cost;
* Recipe Version where applicable;
* source;
* Warehouse;
* actor;
* timestamp;
* operation UUID.

---

# 112. Audit

Important Product/Menu/Recipe/Inventory mutations must create audit events.

Examples:

* Product activation;
* Product archive;
* price change;
* Branch menu change;
* Recipe approval;
* Recipe archive;
* Set configuration;
* inventory adjustment;
* inventory count correction;
* warehouse change;
* equipment availability change.

Audit is handled through the Application layer.

---

# 113. Historical Integrity

The API must preserve:

```text
Historical Product identity
Historical Price
Historical Recipe Version
Historical Set Version
Historical Inventory Transaction
Historical Cost Information where required
Historical Configuration Version
```

Current configuration must never overwrite historical state.

---

# 114. Transaction Boundaries

Core mutations should use one authoritative transaction where atomicity is required.

Example:

```text
Inventory Receipt
    ↓
Validate
    ↓
Create Inventory Transaction
    ↓
Update authoritative stock
    ↓
Create Audit / Outbox
    ↓
Commit
```

Notifications and other secondary effects occur after commit.

---

# 115. Inventory and External Services

Inventory transactions must not depend on external services for authoritative completion.

For example:

```text
Inventory Receipt
      ↓
PostgreSQL Commit
      ↓
Notification
```

not:

```text
Inventory Receipt
      ↓
External Notification
      ↓
Database Commit
```

---

# 116. API Performance Targets

Initial targets:

| Operation                            |   Target |
| ------------------------------------ | -------: |
| Product read p95                     | ≤ 200 ms |
| Product list p95                     | ≤ 300 ms |
| Effective Branch menu p95            | ≤ 300 ms |
| Product price read p95               | ≤ 150 ms |
| Recipe read p95                      | ≤ 250 ms |
| Recipe version history p95           | ≤ 300 ms |
| Recipe approval p95                  | ≤ 400 ms |
| Set read p95                         | ≤ 250 ms |
| Inventory balance read p95           | ≤ 250 ms |
| Inventory availability read p95      | ≤ 200 ms |
| Inventory receipt p95                | ≤ 500 ms |
| Inventory issue p95                  | ≤ 500 ms |
| Inventory adjustment p95             | ≤ 500 ms |
| Inventory count submission p95       | ≤ 500 ms |
| Inventory transaction read p95       | ≤ 300 ms |
| Product operational availability p95 | ≤ 300 ms |

These targets exclude intentionally asynchronous background processing and unavailable external infrastructure.

---

# 117. Availability Target

The Product/Menu/Recipe/Inventory API layer follows the platform API availability target:

**≥ 99.9% monthly**

Critical correctness boundaries must fail safely when authoritative state cannot be established.

---

# 118. Observability

Metrics should include:

```text
product_read_latency
menu_read_latency
recipe_read_latency
inventory_read_latency
inventory_mutation_latency
inventory_conflict_count
insufficient_stock_count
recipe_approval_count
configuration_conflict_count
cache_hit_count
cache_miss_count
```

Metrics must avoid uncontrolled Business/Product UUID labels.

---

# 119. Inventory Alerts

The API may expose operational alert state for:

* low stock;
* out of stock;
* large inventory variance;
* unusual inventory adjustment.

Alert generation itself belongs to the notification/background architecture.

The Product/Inventory API should expose the resulting state rather than perform long-running alert generation synchronously.

---

# 120. Testing Requirements

The API must be tested for:

### Product

* creation;
* update;
* activation;
* deactivation;
* archival;
* category changes.

### Menu

* Business isolation;
* Branch isolation;
* availability;
* price overrides;
* effective configuration;
* session boundary.

### Recipe

* creation;
* validation;
* circular dependency;
* versioning;
* submission;
* approval;
* rejection;
* archival.

### Set

* versioning;
* component availability;
* no substitution;
* historical configuration.

### Inventory

* receiving;
* issue;
* adjustment;
* count;
* production;
* transfers;
* returns;
* FIFO;
* insufficient stock;
* negative stock prevention.

### Offline

* stale configuration;
* operation UUID;
* duplicate sync;
* Recipe Version preservation;
* inventory conflict;
* configuration synchronization.

---

# 121. Security Testing

Security tests must verify:

* Business isolation;
* Branch isolation;
* Product access;
* Recipe restrictions;
* cost visibility;
* inventory permissions;
* Manager authority;
* subscription restrictions;
* archived Product behavior;
* unauthorized Branch configuration;
* cross-Business Recipe references;
* cross-Business Warehouse references.

---

# 122. Concurrency Testing

Concurrency tests must cover:

```text
Two simultaneous stock deductions
Two simultaneous inventory adjustments
Two simultaneous Recipe approvals
Two simultaneous price changes
Two simultaneous Branch menu changes
Two simultaneous Product activation requests
Duplicate inventory receipt
```

The authoritative state must remain correct.

---

# 123. Failure Recovery

If an inventory mutation fails before commit:

```text
Rollback
```

If the transaction commits but a secondary operation fails:

```text
Committed Inventory State
+
Retryable Secondary Operation
```

The inventory transaction must not be duplicated during recovery.

---

# 124. API Endpoint Summary

### Products

```text
GET    /products
POST   /products
GET    /products/{id}
PATCH  /products/{id}
POST   /products/{id}/activate
POST   /products/{id}/deactivate
POST   /products/{id}/archive
GET    /products/{id}/price
PATCH  /products/{id}/price
GET    /products/{id}/cost
```

### Categories

```text
GET    /categories
POST   /categories
GET    /categories/{id}
PATCH  /categories/{id}
POST   /categories/{id}/archive
```

### Menu

```text
GET    /menu
GET    /branches/{branch_id}/menu
GET    /branches/{branch_id}/menu/effective
PATCH  /branches/{branch_id}/menu/products/{product_id}
POST   /menu/products/{product_id}/enable
POST   /menu/products/{product_id}/disable
```

### Recipes

```text
GET    /products/{product_id}/recipe
POST   /products/{product_id}/recipes
GET    /recipes/{id}
PATCH  /recipes/{id}
POST   /recipes/{id}/submit
POST   /recipes/{id}/approve
POST   /recipes/{id}/reject
POST   /recipes/{id}/archive
GET    /recipes/{id}/versions
```

### Sets

```text
GET    /sets
POST   /sets
GET    /sets/{id}
PATCH  /sets/{id}
POST   /sets/{id}/archive
GET    /sets/{id}/versions
POST   /sets/{id}/versions
POST   /sets/{id}/versions/{version}/approve
```

### Warehouses

```text
GET    /warehouses
POST   /warehouses
GET    /warehouses/{id}
PATCH  /warehouses/{id}
POST   /warehouses/{id}/archive
```

### Inventory

```text
GET    /inventory
GET    /inventory/availability
GET    /inventory/low-stock
GET    /inventory/out-of-stock
GET    /inventory/transactions
GET    /inventory/transactions/{id}

POST   /inventory/receipts
POST   /inventory/issues
POST   /inventory/adjustments
POST   /inventory/counts
POST   /inventory/production
POST   /inventory/transfers
POST   /inventory/returns
```

### Equipment

```text
POST /branches/{branch_id}/products/{product_id}/equipment-unavailable
POST /branches/{branch_id}/products/{product_id}/equipment-available
```

---

# 125. API Invariants

The following invariants apply to Product, Menu, Recipe and Inventory APIs:

1. Product identity is Business-scoped.
2. Product UUID does not provide authorization.
3. Cross-Business Product access is prohibited.
4. Product type is explicitly defined.
5. A Product belongs to exactly one menu category.
6. Category changes do not create a new Product identity.
7. Historical Product identity remains reconstructable.
8. Archived Products remain historically accessible.
9. Product archival does not delete historical Orders.
10. Product archival does not delete inventory history.
11. Product archival does not delete Recipe history.
12. Product activation does not automatically enable every Branch.
13. Product deactivation blocks new sales.
14. Branch menu state is Branch-scoped.
15. Branch menu changes do not affect other Branches.
16. Global menu state does not replace Branch availability.
17. Menu availability is separate from inventory availability.
18. Equipment availability is separate from menu configuration.
19. Out-of-stock state does not delete a Product.
20. Standard Product price is separate from inventory cost.
21. Branch price override affects only its Branch.
22. Branch price override does not change global price.
23. Price changes do not rewrite existing Order Item prices.
24. Historical prices remain immutable.
25. Last Purchase Cost is separate from selling price.
26. Client-provided final prices are never authoritative.
27. Custom markup is limited to 0–100%.
28. Custom markup uses server-authoritative cost data.
29. Recipe belongs to the correct Business.
30. Cross-Business Recipe components are prohibited.
31. Recipe components must reference valid Products.
32. Circular Recipe dependencies are prohibited.
33. Required Recipe Versions must be approved before normal operational use.
34. Recipe Versions are immutable after becoming historical.
35. Recipe changes create new operational versions where required.
36. Historical inventory deductions preserve Recipe Version.
37. Recipe changes do not rewrite historical inventory.
38. Recipe changes do not automatically rewrite historical Product prices.
39. Recipe approval is permission-controlled.
40. Recipe rejection does not become operational.
41. Archived Recipes remain historically available.
42. Set identity is preserved independently from components.
43. Set composition is versioned where operational behavior changes.
44. Historical Set Orders preserve their Set Version.
45. Set component substitution is prohibited unless explicitly supported by future rules.
46. Mandatory unavailable Set components block sale.
47. Warehouse is Business-scoped.
48. Branch Warehouse is Branch-scoped.
49. Cross-Business Warehouse access is prohibited.
50. Inventory balance is authoritative on the server.
51. Client inventory quantity is never authoritative.
52. Cached inventory is not authoritative for final deduction.
53. Negative inventory is prohibited.
54. Inventory receipts create authoritative transactions.
55. Inventory issues create authoritative transactions.
56. Inventory adjustments create new transactions.
57. Inventory counts do not silently overwrite history.
58. Historical inventory transactions are immutable.
59. Sale-generated inventory transactions cannot be fabricated through arbitrary client requests.
60. Recipe-derived deductions are server-generated.
61. Semi-finished production uses the applicable Recipe Version.
62. FIFO layers are server-controlled.
63. Cost layers cannot be directly modified by clients.
64. Average Cost is derived server-side.
65. Low-stock state is derived from authoritative inventory.
66. Shopping lists do not increase inventory.
67. Confirmed purchases require inventory receiving.
68. Equipment unavailability does not alter Product identity.
69. Equipment unavailability does not alter Recipe history.
70. Equipment unavailability does not alter historical prices.
71. Inventory mutations require appropriate permissions.
72. Cost visibility requires explicit authorization where restricted.
73. Inactive employees cannot perform new inventory mutations.
74. READ_ONLY subscription blocks inventory mutations.
75. Deleted Businesses cannot accept normal inventory mutations.
76. Offline inventory operations require valid trusted-device authorization.
77. Offline operations use stable operation UUIDs.
78. Duplicate offline operations do not duplicate inventory effects.
79. Offline configuration versions remain identifiable.
80. Offline Recipe Versions remain identifiable.
81. Server state remains authoritative after synchronization.
82. Transaction synchronization has priority over configuration synchronization.
83. Stale configuration cannot rewrite historical transactions.
84. Inventory mutations use authoritative concurrency control.
85. Concurrent stock deductions cannot produce negative inventory.
86. Configuration updates use optimistic concurrency where required.
87. Stale configuration updates are rejected.
88. Important mutations support idempotency.
89. Duplicate idempotent operations do not duplicate effects.
90. Inventory batch sizes are bounded.
91. Large inventory operations cannot create unbounded transactions.
92. Product responses expose only authorized fields.
93. Recipe responses expose only authorized information.
94. Cost information is not automatically exposed to POS users.
95. API cache cannot replace authoritative Product state.
96. API cache cannot replace authoritative Recipe state.
97. API cache cannot replace authoritative Inventory state.
98. Important configuration changes are audited.
99. Inventory adjustments are audited.
100. Recipe approvals are audited.
101. Historical state cannot be rewritten for performance.
102. Inventory transaction history remains reconstructable.
103. Secondary notification failures do not rollback committed inventory transactions.
104. External services are not authoritative for inventory completion.
105. Product/Menu/Recipe/Inventory APIs preserve Business isolation.
106. Product/Menu/Recipe/Inventory APIs preserve Branch isolation.
107. API authorization remains server-side.
108. Client-provided Business IDs are never trusted without validation.
109. Client-provided Branch IDs are never trusted without validation.
110. API availability follows the platform SLO.
111. Performance optimization must not weaken inventory correctness.
112. Performance optimization must not weaken security.
113. Historical Recipe Versions cannot be replaced by current Recipe configuration.
114. Current Menu configuration cannot reinterpret historical Orders.
115. Current Product price cannot reinterpret historical financial transactions.
116. Current inventory balance cannot rewrite historical transactions.
117. Current cost cannot reinterpret historical financial transactions.
118. Configuration version must remain identifiable.
119. Inventory operations must remain attributable to actor and operation context.
120. Product, Menu, Recipe and Inventory APIs must preserve the modular monolith boundary.

---

# 126. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/11_Inventory_and_Warehouse.md`
* `docs/02_System_Analysis/12_Products_and_Recipes.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

### Database

* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/13_API_POS_and_Order_Endpoints.md`
* `docs/04_Architecture/09_API/14_API_Payment_Cash_and_Financial_Endpoints.md`

---

# 127. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`

**Previous Document:** `14_API_Payment_Cash_and_Financial_Endpoints.md`

**Next Document:** `16_API_Employee_Attendance_and_Payroll_Endpoints.md`

---

## Final Principle

> Product, Menu, Recipe and Inventory APIs must expose operational capabilities while preserving Business and Branch isolation, authoritative inventory state, immutable historical configuration, Recipe Version integrity, pricing integrity, concurrency safety and offline compatibility.

