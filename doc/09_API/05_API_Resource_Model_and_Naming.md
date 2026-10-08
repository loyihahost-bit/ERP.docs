# API Resource Model and Naming

**Document ID:** API-05
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

# 1. Purpose

This document defines the API resource model and naming standards for FastFood ERP.

The objective is to provide a consistent representation of:

* Business resources;
* Branch resources;
* employee and identity resources;
* product and menu resources;
* inventory resources;
* order and financial resources;
* configuration resources;
* reports and files;
* synchronization resources;
* resource relationships;
* collection endpoints;
* individual resources;
* business commands;
* resource identifiers;
* naming conventions.

The API resource model must remain predictable for frontend clients, POS clients, offline clients and external integrations.

---

# 2. Scope

This document covers:

* resource definition;
* resource identity;
* resource ownership;
* Business scope;
* Branch scope;
* resource hierarchy;
* resource naming;
* URL naming;
* collection naming;
* singular resource naming;
* nested resources;
* relationship representation;
* resource references;
* UUID representation;
* command naming;
* action endpoints;
* state representation;
* timestamps;
* monetary representation;
* quantity representation;
* enum naming;
* query parameter naming;
* field naming;
* request and response naming;
* resource lifecycle representation;
* cross-Business and cross-Branch references;
* resource compatibility;
* API invariants.

This document does not define detailed validation, authorization rules, error codes, pagination behavior or individual business endpoint contracts.

---

# 3. Resource Model Principle

An API resource represents a stable business or system concept that has an identifiable lifecycle or authoritative state.

Examples:

```text id="resprinciple1"
Business
Branch
Employee
Device
Product
Recipe
Recipe Version
Set
Inventory
Order
Order Item
Payment
Refund
Cash Register
Cash Session
Shift Handover
Attendance
Payroll
Notification
Report
File
Configuration
Subscription
Synchronization Operation
```

A resource should exist because the system needs to identify, retrieve, reference, modify, audit or synchronize that concept.

---

# 4. Resource Identity

Every persistent resource that requires independent identification must have a stable UUID.

Example:

```json id="resourceid1"
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The UUID identifies the resource.

The UUID does not itself grant:

* authorization;
* Business access;
* Branch access;
* permission;
* subscription entitlement.

Authorization is evaluated separately.

---

# 5. UUID Stability

A resource UUID remains stable throughout the supported lifetime of the resource.

Changing:

* name;
* category;
* status;
* price;
* configuration;
* Branch availability

must not create a new UUID when the underlying resource identity remains the same.

Historical records may reference the same resource UUID together with the historical snapshot required by their own domain rules.

---

# 6. UUID Format

API resource UUIDs should use the canonical textual UUID representation.

Example:

```text id="uuidformat1"
550e8400-e29b-41d4-a716-446655440000
```

The API must not expose internal database numeric identifiers as public resource identity when a UUID is defined as the resource identifier.

---

# 7. Business Resource

`Business` is the primary tenant resource.

Example:

```text id="businessresource1"
GET /api/v1/businesses/{business_id}
```

A Business owns or scopes resources such as:

* Branches;
* Employees;
* Products;
* Menu configuration;
* Inventory;
* Orders;
* Reports;
* subscription state;
* configuration.

Business identity is the primary isolation boundary for tenant-owned resources.

---

# 8. Branch Resource

`Branch` represents an operational location belonging to a Business.

Example:

```text id="branchresource1"
GET /api/v1/branches/{branch_id}
```

A Branch must belong to exactly one Business.

A Branch UUID must never be interpreted outside its Business scope without server-side verification.

---

# 9. Business-to-Branch Relationship

The logical relationship is:

```text id="businessbranch1"
Business
   └── Branch
```

The API may expose Branches as:

```text id="branchcollection1"
GET /api/v1/businesses/{business_id}/branches
```

and as a direct scoped resource:

```text id="branchresource2"
GET /api/v1/branches/{branch_id}
```

The selected representation must remain consistent with authorization and Business scope enforcement.

---

# 10. Resource Ownership

Every resource must have a clearly defined ownership or scope.

Typical scopes include:

```text id="scopelevels1"
Platform
Business
Branch
Employee
Device
Transaction
```

The API contract must define the scope of each resource.

A resource must not be treated as globally accessible merely because it has a UUID.

---

# 11. Scope Metadata

Where useful, a response may include explicit scope references.

Example:

```json id="scopemeta1"
{
  "id": "uuid",
  "business_id": "uuid",
  "branch_id": "uuid"
}
```

Scope fields are references.

They do not replace server-side authorization.

---

# 12. Global Resources

Some resources are platform-level rather than Business-level.

Examples may include:

* subscription tariff definitions;
* platform feature definitions;
* system reference metadata.

Platform-level resources must not be confused with Business-owned resources.

---

# 13. Business-Scoped Resources

Typical Business-scoped resources include:

* Product;
* Category;
* Recipe;
* Recipe Version;
* Set;
* Business configuration;
* Employee;
* Report;
* Subscription;
* menu definitions.

A Business-scoped resource must contain or be resolvable to its Business context.

---

# 14. Branch-Scoped Resources

Typical Branch-scoped resources include:

* Branch menu configuration;
* inventory;
* warehouse;
* cash register;
* cash session;
* shift handover;
* attendance records;
* branch-specific price override;
* Branch operational configuration.

Branch-scoped resources must remain isolated between Branches.

---

# 15. Transaction Resources

Transaction resources represent operational or financial events.

Examples:

```text id="transactionresources1"
Order
Payment
Refund
Inventory Transaction
Cash Session
Cash Handover
Correction
```

Transaction resources must preserve their historical identity.

A transaction UUID must not be reused for another logical transaction.

---

# 16. Resource Naming Standard

Resource names in URLs use lowercase plural nouns.

Examples:

```text id="namingstandard1"
/businesses
/branches
/employees
/products
/orders
/payments
/refunds
/reports
/files
```

The API must not use inconsistent pluralization.

---

# 17. URL Case

URL paths use lowercase characters.

Words are separated using hyphens when multiple words are required.

Example:

```text id="urlcase1"
/cash-sessions
/shift-handovers
/recipe-versions
```

The API must not use mixed-case URL paths.

---

# 18. JSON Field Naming

JSON fields use `snake_case`.

Example:

```json id="jsonnaming1"
{
  "business_id": "uuid",
  "branch_id": "uuid",
  "created_at": "2026-10-06T10:00:00Z",
  "updated_at": "2026-10-06T10:05:00Z"
}
```

The API must not mix:

```text id="badjsonnaming1"
camelCase
snake_case
PascalCase
```

within the same contract.

---

# 19. Query Parameter Naming

Query parameters use `snake_case`.

Examples:

```text id="querynaming1"
?branch_id=uuid
?created_after=timestamp
?payment_status=PAID
?sort_by=created_at
```

The API must not introduce mixed naming conventions.

---

# 20. Collection Endpoints

A collection endpoint represents multiple resources.

Example:

```text id="collectionendpoint1"
GET /api/v1/orders
```

The response should use a consistent collection structure.

Example:

```json id="collectionresponse1"
{
  "items": [],
  "next_cursor": null
}
```

Pagination details are defined in the dedicated pagination document.

---

# 21. Individual Resource Endpoints

A single resource is addressed by its UUID.

Example:

```text id="singleresource1"
GET /api/v1/orders/{order_id}
```

The path identifies one logical resource.

A request for an invalid or inaccessible resource must not reveal information outside the caller's authorized scope.

---

# 22. Resource Collections and Ownership

Collection endpoints must apply their required scope.

For example:

```text id="scopedcollection1"
GET /api/v1/orders
```

must return only Orders accessible to the authenticated context.

The client must not be able to override Business or Branch scope simply by supplying another UUID.

---

# 23. Nested Resources

Nested resources may be used when the parent-child relationship is important to the API operation.

Example:

```text id="nestedresource1"
GET /api/v1/orders/{order_id}/items
```

This expresses:

```text id="nestedrelationship1"
Order
 └── Order Items
```

Nested resources should be used when the parent provides meaningful context.

---

# 24. Avoiding Excessive Nesting

The API must avoid deeply nested URLs.

Avoid patterns such as:

```text id="deepnest1"
/businesses/{business_id}/branches/{branch_id}/cash-registers/{register_id}/cash-sessions/{session_id}/...
```

When the resource can be addressed directly while preserving authorization, a shorter resource path is preferred.

Example:

```text id="shortresource1"
/cash-sessions/{cash_session_id}
```

The server still validates the complete Business and Branch relationship.

---

# 25. Parent-Child Relationship Validation

When a nested resource is requested, the server must verify that the child belongs to the specified parent.

For example:

```text id="parentvalidation1"
/orders/{order_id}/items/{item_id}
```

must not return an Order Item belonging to another Order.

A matching UUID alone is insufficient.

---

# 26. Resource Relationships

Relationships should normally be represented using UUID references.

Example:

```json id="relationship1"
{
  "id": "order-uuid",
  "branch_id": "branch-uuid",
  "cash_session_id": "cash-session-uuid"
}
```

The API should not duplicate complete related resources unnecessarily.

---

# 27. Relationship Expansion

Related resource details may be requested through explicit mechanisms when necessary.

The API must avoid silently returning large object graphs.

For example, an Order response should not automatically contain:

* complete employee history;
* complete Recipe history;
* complete inventory history;
* complete audit history.

Large related data should be retrieved through dedicated resources or explicit supported expansion mechanisms.

---

# 28. Resource Reference vs Embedded Object

A UUID reference should be preferred when the related resource has its own lifecycle.

Example:

```json id="refobject1"
{
  "product_id": "uuid"
}
```

An embedded object may be used when the information is:

* small;
* required for the representation;
* stable for that response;
* not intended to represent a separate mutable resource.

---

# 29. Historical Snapshots

Historical transactions may contain snapshots rather than only live resource references.

For example, an Order Item may retain:

```text id="ordersnapshot1"
Product UUID
Product Name Snapshot
Unit Price Snapshot
Discount Snapshot
Recipe Version Reference
```

The current Product resource must not be used to reinterpret the historical transaction.

---

# 30. Resource Identity vs Snapshot Identity

A live resource identity and a historical snapshot are different concepts.

Example:

```text id="identitysnapshot1"
Product
  UUID → stable identity

Order Item
  Product UUID → relationship
  Product Name Snapshot → historical state
  Unit Price Snapshot → historical financial state
```

Changing the current Product must not change historical snapshots.

---

# 31. Resource State

Resources with lifecycle state should expose an explicit state field.

Example:

```json id="resstate1"
{
  "id": "uuid",
  "status": "ACTIVE"
}
```

State values must be documented and stable within the API version.

---

# 32. Status Naming

Resource status values use uppercase `SCREAMING_SNAKE_CASE`.

Examples:

```text id="statusnaming1"
ACTIVE
INACTIVE
OPEN
CLOSED
PAID
CANCELLED
READ_ONLY
DELETED
```

The exact valid values are defined by the resource contract.

---

# 33. Status Semantics

A status value represents a defined business state.

The API must not use a status field as an unstructured text field.

Clients may safely depend on documented status semantics within the supported API version.

---

# 34. Resource Lifecycle

A resource lifecycle should be represented through explicit state transitions where the domain requires them.

Example:

```text id="lifecycle1"
OPEN
  ↓
ACCEPTED
  ↓
PAID
```

The API should expose domain commands for meaningful state transitions rather than allowing arbitrary status replacement.

---

# 35. State Changes vs Generic Updates

A client must not directly modify a business-controlled lifecycle state through a generic update when the state transition represents a business command.

For example:

```text id="statecommand1"
POST /api/v1/orders/{order_id}/accept
```

is preferred over:

```text id="badstatecommand1"
PATCH /api/v1/orders/{order_id}
{
  "status": "ACCEPTED"
}
```

The command endpoint allows the server to enforce the complete business transition.

---

# 36. Command Naming

Business commands use explicit action names.

The standard form is:

```text id="commandnaming1"
POST /resources/{resource_id}/{action}
```

Examples:

```text id="commandexamples1"
POST /orders/{order_id}/accept
POST /orders/{order_id}/cancel
POST /orders/{order_id}/refund
POST /cash-sessions/{cash_session_id}/close
POST /recipes/{recipe_id}/approve
```

Command naming must describe the business operation rather than an implementation detail.

---

# 37. Command vs CRUD

CRUD is appropriate for ordinary resource lifecycle operations.

Business commands are preferred when an operation:

* changes a business state;
* performs validation across multiple resources;
* creates financial effects;
* requires approval;
* creates audit events;
* requires idempotency;
* has domain-specific semantics.

---

# 38. Avoiding Generic Action Endpoints

The API should avoid generic endpoints such as:

```text id="genericaction1"
/orders/{id}/action
```

with a request like:

```json id="genericaction2"
{
  "action": "ACCEPT"
}
```

when the operation has a meaningful business command.

Explicit commands are easier to document, authorize, test and audit.

---

# 39. Resource Names vs Domain Terms

API names should use stable domain terminology.

Examples:

```text id="domainterms1"
Order
Cash Session
Shift Handover
Recipe Version
Branch Price Override
```

The API must not rename established domain concepts merely to match internal class names.

---

# 40. Internal Implementation Independence

Public resource names must not expose internal implementation details.

For example, the API should not expose:

```text id="internalbad1"
/sql-models
/repository-records
/orm-entities
/database-rows
```

The API represents business capabilities, not database structure.

---

# 41. Product Resource

`Product` represents a Business-level product identity.

Example:

```text id="productresource1"
/products/{product_id}
```

A Product may be:

* a raw material;
* a semi-finished product;
* a finished product;

according to the Product model.

Product type must be represented explicitly where required.

---

# 42. Category Resource

`Category` represents a menu category.

Example:

```text id="categoryresource1"
/categories/{category_id}
```

A Product belongs to exactly one menu category according to the established system model.

Changing category assignment does not create a new Product identity.

---

# 43. Recipe Resource

`Recipe` represents the logical recipe definition associated with a Product.

Example:

```text id="reciperesource1"
/recipes/{recipe_id}
```

Recipe Versions represent versioned recipe states.

---

# 44. Recipe Version Resource

`Recipe Version` represents a historical or operational version of a Recipe.

Example:

```text id="recipeversion1"
/recipe-versions/{recipe_version_id}
```

A Recipe Version must remain identifiable for historical inventory and transaction interpretation.

---

# 45. Set Resource

`Set` represents a configured combination of Products.

Example:

```text id="setresource1"
/sets/{set_id}
```

Set composition and Set pricing are version-sensitive where operational behavior changes.

---

# 46. Menu Resource

The API must distinguish between:

```text id="menuresource1"
Global Menu Configuration
Branch Menu Configuration
```

A Business-level menu definition must not be confused with Branch-specific availability.

The exact endpoint structure is defined in the dedicated menu/product endpoint document.

---

# 47. Inventory Resource

Inventory resources represent Branch-specific stock state and inventory operations.

Inventory APIs must distinguish between:

* current stock state;
* inventory transactions;
* warehouses;
* stock adjustments.

A cached or displayed quantity does not become authoritative merely because it is represented as an API resource.

---

# 48. Order Resource

`Order` represents a customer transaction.

Example:

```text id="orderresource1"
/orders/{order_id}
```

Order identity remains stable throughout its lifecycle.

Order financial history must use authoritative snapshots.

---

# 49. Order Item Resource

Order Items belong to an Order.

Example:

```text id="orderitemresource1"
/orders/{order_id}/items/{order_item_id}
```

An Order Item must not be exposed independently in a way that allows it to bypass its Order context.

Its relationship to the parent Order must always be validated.

---

# 50. Payment Resource

`Payment` represents a payment transaction associated with an Order.

Example:

```text id="paymentresource1"
/payments/{payment_id}
```

Payment identity must remain stable.

Payment operations must not be confused with generic Order updates.

---

# 51. Refund Resource

`Refund` represents a refund operation or resulting refund record.

Example:

```text id="refundresource1"
/refunds/{refund_id}
```

Refunds must preserve historical financial meaning.

Current Product pricing must not reinterpret a historical refund.

---

# 52. Cash Register Resource

`Cash Register` represents the physical/logical register assigned to a Branch.

Example:

```text id="cashregisterresource1"
/cash-registers/{cash_register_id}
```

The current system normally uses one register per Branch, while the API model must not prevent future multiple registers.

---

# 53. Cash Session Resource

`Cash Session` represents an operational cashier session.

Example:

```text id="cashsessionresource1"
/cash-sessions/{cash_session_id}
```

Cash Session state and financial operations are Branch-scoped and historically significant.

---

# 54. Shift Handover Resource

`Shift Handover` represents transfer of cash responsibility between cashier sessions.

Example:

```text id="handoverresource1"
/shift-handovers/{shift_handover_id}
```

The resource must retain references to the relevant sessions and employees.

---

# 55. Employee Resource

`Employee` represents a Business employee identity.

Example:

```text id="employeeresource1"
/employees/{employee_id}
```

Employee permissions, Branch scope and status are separate concerns from the employee's identity.

---

# 56. Device Resource

`Device` represents a trusted client device.

Example:

```text id="deviceresource1"
/devices/{device_id}
```

Device identity must remain separate from:

* employee identity;
* authentication session;
* offline authorization;
* API request identity.

---

# 57. Attendance Resource

`Attendance` represents employee attendance records.

Example:

```text id="attendanceresource1"
/attendance/{attendance_id}
```

Attendance records must retain their historical identity.

---

# 58. Payroll Resource

`Payroll` represents payroll-related records or calculations.

Example:

```text id="payrollresource1"
/payroll/{payroll_id}
```

Payroll API contracts must preserve financial precision and historical results.

---

# 59. Notification Resource

`Notification` represents an in-system notification.

Example:

```text id="notificationresource1"
/notifications/{notification_id}
```

Notification state may include:

```text id="notificationstate1"
UNREAD
READ
ARCHIVED
```

Notification delivery does not become part of a core business transaction merely because the notification references it.

---

# 60. Report Resource

`Report` represents a report definition or report resource.

Example:

```text id="reportresource1"
/reports/{report_id}
```

A Report Version is separately identifiable where immutable historical report results are required.

---

# 61. Report Version Resource

`Report Version` represents an immutable generated report state.

Example:

```text id="reportversionresource1"
/report-versions/{report_version_id}
```

A Report Version must not be modified in place.

A new result requires a new version.

---

# 62. File Resource

`File` represents a managed file or generated document.

Example:

```text id="fileresource1"
/files/{file_id}
```

The API resource identifies metadata and controlled access to the file.

Binary storage details remain an infrastructure concern.

---

# 63. Configuration Resource

Configuration represents versioned Business or Branch operational configuration.

Example:

```text id="configurationresource1"
/configurations/{configuration_id}
```

Configuration identity must remain separate from the current effective configuration.

Historical configuration must remain reconstructable.

---

# 64. Subscription Resource

`Subscription` represents Business subscription state.

Example:

```text id="subscriptionresource1"
/subscriptions/{subscription_id}
```

Subscription entitlement determines whether an operation is permitted.

Subscription identity must not be confused with tariff definition identity.

---

# 65. Synchronization Operation Resource

`Synchronization Operation` represents an offline operation submitted for server processing.

Example:

```text id="syncresource1"
/synchronization-operations/{operation_id}
```

The operation UUID also provides the idempotency identity for the synchronization operation where defined by the synchronization contract.

---

# 66. Resource Relationships

Important relationships should be explicit.

Example:

```text id="resourcegraph1"
Business
 ├── Branch
 ├── Employee
 ├── Product
 │    └── Recipe
 │         └── Recipe Version
 ├── Set
 └── Order
      ├── Order Item
      └── Payment
```

The API must preserve these domain relationships without exposing unnecessary database structure.

---

# 67. Cross-Business References

A resource belonging to Business A must not be accepted as a related resource for Business B.

Example:

```text id="crossbusiness1"
Business A
 └── Product A

Business B
 └── Order B
```

Order B must not reference Product A.

The server must validate Business ownership for every cross-resource relationship.

---

# 68. Cross-Branch References

Branch-scoped resources must not be associated across unrelated Branches.

For example:

```text id="crossbranch1"
Branch A
 └── Cash Session A

Branch B
 └── Order B
```

Order B must not use Cash Session A unless an explicitly defined business relationship permits it.

---

# 69. Scope Resolution

Resource scope must be resolved from authoritative server-side relationships.

The server must not trust:

```text id="untrustedscope1"
business_id
branch_id
employee_id
cash_session_id
```

supplied by the client merely because the values are syntactically valid.

The relationship must be verified against authenticated context and authoritative state.

---

# 70. Resource Creation

When a resource is created, the server determines its authoritative:

* UUID;
* Business;
* Branch where applicable;
* timestamps;
* actor;
* ownership;
* initial state.

Clients may provide business data required by the contract but must not control protected ownership relationships.

---

# 71. Resource Update

Generic resource updates should modify only fields explicitly permitted by the resource contract.

A client must not use generic update endpoints to modify:

* Business ownership;
* protected Branch ownership;
* historical timestamps;
* audit metadata;
* transaction identity;
* immutable financial snapshots;
* server-controlled lifecycle fields.

---

# 72. Resource Deletion

Deletion semantics depend on the resource.

Resources with historical or transactional significance should normally use:

* archive;
* deactivate;
* cancel;
* supersede;
* lifecycle state;

rather than physical deletion.

The API must reflect the domain's deletion policy rather than exposing unrestricted `DELETE` operations.

---

# 73. Physical Deletion

Physical deletion is permitted only where the underlying data lifecycle explicitly allows it.

Examples may include:

* temporary files;
* expired temporary artifacts;
* Business data after the defined lifecycle process.

Physical deletion must not silently remove required historical records.

---

# 74. Archive vs Delete

The API should use explicit lifecycle operations where archive behavior is required.

For example:

```text id="archivecommand1"
POST /products/{product_id}/archive
```

is preferred over:

```text id="baddelete1"
DELETE /products/{product_id}
```

when the Product must remain available for historical references.

---

# 75. Timestamps

Resources requiring temporal tracking should use explicit fields such as:

```text id="timestamps1"
created_at
updated_at
```

Additional domain-specific timestamps may include:

```text id="domaintimestamps1"
approved_at
effective_at
closed_at
paid_at
cancelled_at
```

Only semantically relevant timestamps should be exposed.

---

# 76. Timestamp Semantics

Timestamp fields must have documented semantics.

The API should use timezone-aware timestamps for instants.

Calendar dates must remain distinct from timestamps where time-of-day is not meaningful.

---

# 77. Actor References

Important resources and operations may expose actor references where required.

Example:

```json id="actorref1"
{
  "created_by_employee_id": "uuid"
}
```

The API must not expose sensitive authentication internals merely to identify the actor.

---

# 78. Device References

Operations requiring device attribution may expose:

```text id="deviceref1"
device_id
```

Device references must not be treated as authentication by themselves.

---

# 79. Monetary Values

Money fields must use a deterministic representation.

The API must not mix numeric and string representations for the same monetary field within a contract.

Example:

```json id="money1"
{
  "unit_price": 30000,
  "discount_amount": 5000,
  "total_amount": 25000,
  "currency": "UZS"
}
```

The exact precision and currency rules are defined by the financial API contracts.

---

# 80. Quantity Values

Inventory and order quantities must have explicit unit semantics.

A quantity must not be interpreted without its applicable unit.

Example:

```json id="quantity1"
{
  "quantity": 1.5,
  "unit": "KG"
}
```

The exact supported units are defined by the inventory and product data model.

---

# 81. Boolean Fields

Boolean fields use clear positive semantics.

Examples:

```text id="boolean1"
is_active
is_archived
is_read
is_available
```

The API should avoid ambiguous fields such as:

```text id="badboolean1"
status_flag
mode
value
```

when a direct semantic name is possible.

---

# 82. Collection Naming

Collection resources use plural nouns.

Correct:

```text id="collectionnaming1"
/products
/orders
/payments
/cash-sessions
```

Avoid:

```text id="badcollectionnaming1"
/product
/order
/payment
/cashSession
```

---

# 83. Singular Naming

A single resource is represented by the plural collection followed by its identifier.

Example:

```text id="singularnaming1"
/products/{product_id}
/orders/{order_id}
/cash-sessions/{cash_session_id}
```

The URL does not switch to a singular noun for an individual resource.

---

# 84. Acronyms

URL and JSON names should prefer readable domain names rather than unexplained abbreviations.

For example:

```text id="acronyms1"
/cash-sessions
```

is preferred over:

```text id="badacronym1"
/cs
```

Internal abbreviations must not become public API terminology unless they are established domain terms.

---

# 85. Action Names

Action names use lowercase hyphen-separated words where multiple words are required.

Examples:

```text id="actionnames1"
archive
approve
close
cancel
mark-paid
request-correction
```

Actions should represent business intent.

---

# 86. Relationship Names

Relationship fields use explicit `_id` suffixes for UUID references.

Examples:

```text id="relationshipnames1"
business_id
branch_id
product_id
order_id
cash_session_id
employee_id
device_id
```

A field containing a UUID reference must not use an ambiguous name such as:

```text id="badrelationshipnames1"
business
branch
product
```

unless the field contains an actual embedded resource object.

---

# 87. Embedded Resource Naming

When an embedded object is returned, the field name should identify the resource clearly.

Example:

```json id="embedded1"
{
  "product": {
    "id": "uuid",
    "name": "Burger"
  }
}
```

The API must not ambiguously mix UUID references and embedded objects under the same field semantics.

---

# 88. Resource Lists

List fields should use plural names.

Example:

```json id="listfield1"
{
  "items": [],
  "payments": [],
  "order_items": []
}
```

A collection field must not alternate unpredictably between singular and plural naming.

---

# 89. API Resource Naming and Compatibility

Once a public resource name is released within a supported API major version, it should remain stable.

Renaming:

```text id="renamebad1"
/cash-sessions
```

to:

```text id="renamed1"
/cashier-sessions
```

is a contract change.

The old resource name must remain supported during the migration period when backward compatibility is required.

---

# 90. Resource Aliases

Aliases may be introduced only when necessary.

The API should avoid maintaining multiple permanent names for the same resource because aliases increase:

* documentation complexity;
* testing requirements;
* maintenance cost;
* ambiguity.

A canonical resource name must always exist.

---

# 91. CRUD Endpoint Convention

Standard CRUD operations use:

```text id="crudconvention1"
GET    /resources
POST   /resources

GET    /resources/{id}
PATCH  /resources/{id}
DELETE /resources/{id}
```

Not every resource must support every CRUD operation.

The supported operations depend on the domain lifecycle.

---

# 92. PUT vs PATCH

`PATCH` should be used for partial updates where partial mutation is supported.

`PUT` should be used only when complete replacement semantics are explicitly defined.

The API must not use `PUT` merely because an update operation exists.

---

# 93. POST for Business Commands

`POST` is used for commands that create a business effect without representing a generic resource replacement.

Examples:

```text id="postcommands1"
POST /orders/{order_id}/accept
POST /orders/{order_id}/cancel
POST /cash-sessions/{cash_session_id}/close
```

The command may create secondary resources such as audit records, payments, inventory transactions or notifications.

---

# 94. DELETE Semantics

`DELETE` must be used only when deletion semantics are explicitly supported.

For historically significant resources, lifecycle commands should normally be preferred.

---

# 95. Resource Naming and Idempotency

Resource creation and business commands that may be retried must support the defined idempotency mechanism.

The resource model must not depend on the client repeating a request safely without explicit idempotency support.

---

# 96. Resource Naming and Offline Operations

Offline clients must use the same canonical resource identifiers as the server after synchronization.

Client-generated UUIDs may be used for offline-created resources where the resource contract permits it.

The server must preserve UUID uniqueness and Business scope.

---

# 97. Client-Generated UUIDs

Client-generated UUIDs must not automatically become trusted ownership identifiers.

The server must validate:

* UUID format;
* uniqueness;
* operation authorization;
* Business scope;
* resource relationship;
* idempotency.

---

# 98. Temporary Client Identity

Temporary local identifiers may exist inside an offline client.

They must not be confused with the authoritative resource UUID unless the API contract explicitly defines them as the resource identity.

Synchronization must provide deterministic mapping where required.

---

# 99. Resource References in Synchronization

Offline synchronization payloads should use canonical resource UUIDs wherever the resource already exists.

For newly created offline resources, the client-generated UUID may become the authoritative resource UUID when permitted by the synchronization architecture.

Duplicate UUID submission must be handled deterministically.

---

# 100. Resource Naming and Audit

Audit records should reference canonical resource UUIDs.

Example:

```json id="auditresource1"
{
  "resource_type": "PRODUCT",
  "resource_id": "uuid"
}
```

The audit system may use a controlled resource type identifier.

Resource type names must remain stable enough for historical interpretation.

---

# 101. Resource Type Naming

Where a resource type must be represented as a value, use uppercase `SCREAMING_SNAKE_CASE`.

Examples:

```text id="resourcetypes1"
BUSINESS
BRANCH
PRODUCT
ORDER
PAYMENT
CASH_SESSION
RECIPE_VERSION
```

The exact list is controlled by the system.

---

# 102. Resource Versioning

Resource configuration versions should be represented explicitly when the domain requires historical identity.

Examples:

```text id="resourceversion1"
configuration_version
recipe_version
set_version
report_version
```

A version must not be represented only as an arbitrary integer when the version itself has an independently identifiable lifecycle and UUID is required by the underlying data model.

---

# 103. Effective Configuration

When a resource depends on effective configuration, the API may expose the configuration version used for the operation.

Example:

```json id="effectiveconfig1"
{
  "configuration_version_id": "uuid"
}
```

This supports historical traceability without embedding the entire configuration.

---

# 104. Resource Ordering

Resource collection ordering must be explicitly defined by the endpoint contract.

The API must not rely on database default ordering.

Stable ordering is especially important for:

* pagination;
* synchronization;
* audit history;
* reports;
* transaction lists.

---

# 105. Resource Naming and Search

Search should operate on documented resource fields.

Search parameter naming must remain consistent.

Examples:

```text id="searchnaming1"
?search=burger
?category_id=uuid
?status=ACTIVE
```

Detailed search and filtering behavior is defined by:

`11_API_Pagination_Search_Filtering_and_Sorting.md`.

---

# 106. Resource Naming and Authorization

Resource naming does not determine authorization.

For example:

```text id="authnotname1"
/products/{product_id}
```

does not imply that any authenticated employee may read the Product.

Authorization is determined from:

* actor;
* Business;
* Branch;
* permission;
* resource scope;
* subscription;
* operational rules.

---

# 107. Resource Naming and Security

Public resource names must not expose:

* database table names;
* internal service names;
* infrastructure topology;
* secret identifiers;
* authentication internals.

The API should expose stable domain concepts only.

---

# 108. Resource Naming and Performance

Resource representations should remain focused.

A resource response must not automatically include large historical or related datasets.

This prevents:

* excessive payloads;
* unnecessary database queries;
* high serialization cost;
* frontend performance degradation.

---

# 109. Resource Naming and Caching

Cache keys may use resource identifiers, but cache identity must also include the required scope and configuration context.

For example:

```text id="resourcecache1"
product:{business_id}:{product_id}
```

is valid only when the cached representation is Business-scoped.

Branch-specific representations must include Branch identity.

---

# 110. Resource Naming and Historical Integrity

Resource names must not imply that current state is historical truth.

For example:

```text id="historicalresource1"
Product
```

represents current Product state.

Historical Order Item data must use its own snapshot fields.

Current Product data must never replace historical snapshot data.

---

# 111. Resource Naming and Subscription

Subscription resources and entitlement state must remain distinct from ordinary Business configuration.

A client must not infer entitlement solely from the existence of a resource endpoint.

Authorization determines whether the operation is permitted.

---

# 112. Resource Naming and Errors

Resource names used in errors must use canonical public resource terminology.

Example:

```json id="resourceerror1"
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product was not found.",
    "request_id": "uuid"
  }
}
```

Error code naming rules are defined by the dedicated error architecture document.

---

# 113. Resource Naming and External Integrations

External integrations must use the same canonical public resource model where applicable.

Internal resource names must not be exposed as undocumented integration contracts.

Integration-specific transformations must occur at the integration boundary.

---

# 114. Resource Naming and Webhooks

Webhook payloads should identify resources using stable UUIDs and canonical resource type names.

Example:

```json id="webhookresource1"
{
  "event": "ORDER_PAID",
  "resource_type": "ORDER",
  "resource_id": "uuid"
}
```

The exact webhook contract is defined separately.

---

# 115. Resource Model and API Versioning

Resource names and identity semantics are part of the API contract.

Within a supported major version:

* resource names remain stable;
* identifier semantics remain stable;
* relationship semantics remain stable;
* status meanings remain stable;
* command names remain stable.

Incompatible changes require controlled versioning.

---

# 116. Canonical Naming Examples

The following represent the preferred naming style:

```text id="canonicalexamples1"
GET    /api/v1/businesses
GET    /api/v1/branches
GET    /api/v1/employees
GET    /api/v1/products
GET    /api/v1/recipes
GET    /api/v1/recipe-versions
GET    /api/v1/sets
GET    /api/v1/orders
GET    /api/v1/payments
GET    /api/v1/refunds
GET    /api/v1/cash-registers
GET    /api/v1/cash-sessions
GET    /api/v1/shift-handovers
GET    /api/v1/attendance
GET    /api/v1/payroll
GET    /api/v1/notifications
GET    /api/v1/reports
GET    /api/v1/files
GET    /api/v1/configurations
GET    /api/v1/subscriptions
```

These are naming examples, not a complete endpoint specification.

---

# 117. Prohibited Naming Patterns

The API must avoid:

```text id="prohibitednaming1"
/getOrders
/get_orders
/order
/orderResource
/orm-orders
/db-orders
/orders/action
/orders/{id}/doSomething
```

The preferred model uses stable plural domain nouns and explicit business commands.

---

# 118. Naming Review

Before introducing a new API resource, verify:

```text id="namingreview1"
[ ] Represents a real domain/system concept
[ ] Has clear ownership/scope
[ ] Has stable identity
[ ] Uses canonical domain terminology
[ ] Uses lowercase plural URL naming
[ ] Uses snake_case JSON fields
[ ] Uses snake_case query parameters
[ ] Uses UUID identity where required
[ ] Relationship fields use _id
[ ] Lifecycle state is explicit where required
[ ] Historical identity is preserved
[ ] Business scope is enforced
[ ] Branch scope is enforced where applicable
[ ] Does not expose internal implementation
[ ] Does not duplicate an existing resource
[ ] Does not create unnecessary nesting
[ ] Does not create unnecessary aliases
```

---

# 119. System Invariants

The following invariants apply to the API Resource Model and Naming:

1. Every persistent resource requiring independent identity has a stable UUID.
2. UUID identity does not grant authorization.
3. Resource UUIDs remain stable throughout their supported lifetime.
4. Public resource identity must not expose internal database identifiers when UUID identity is defined.
5. Every resource has a clearly defined ownership or scope.
6. Business is the primary tenant isolation boundary.
7. Branch belongs to exactly one Business.
8. Business-scoped resources cannot cross Business boundaries.
9. Branch-scoped resources cannot cross unrelated Branch boundaries.
10. Cross-resource relationships require server-side scope validation.
11. Client-provided Business IDs are not trusted for authorization.
12. Client-provided Branch IDs are not trusted for authorization.
13. Resource naming uses lowercase plural nouns in URLs.
14. Multi-word URL resources use hyphen-separated names.
15. JSON field names use snake_case.
16. Query parameter names use snake_case.
17. UUID reference fields use the `_id` suffix.
18. Embedded resource objects must be distinguishable from UUID references.
19. Collection resources use plural names.
20. Individual resources use the collection path plus UUID.
21. Resource URLs remain stable within a supported API major version.
22. Resource names remain stable within a supported API major version.
23. Resource state values use documented semantics.
24. Resource status values use `SCREAMING_SNAKE_CASE`.
25. Business lifecycle transitions use explicit commands where domain behavior requires them.
26. Generic PATCH must not bypass business command rules.
27. Business commands use explicit action names.
28. Generic `/action` endpoints are prohibited where explicit commands are appropriate.
29. API resource names must use domain terminology rather than internal implementation names.
30. Public resource names must not expose database structure.
31. Deeply nested resource URLs must be avoided.
32. Nested resources must validate the parent-child relationship.
33. Resource relationships use stable UUID references where appropriate.
34. Related resources must not be embedded unnecessarily.
35. Large historical datasets must not be automatically embedded in normal resource responses.
36. Historical transactions retain required snapshots independently of current resource state.
37. Current Product state cannot reinterpret historical Order Item data.
38. Current Recipe state cannot reinterpret historical inventory transactions.
39. Current Set state cannot reinterpret historical Set Orders.
40. Resource state changes must preserve historical identity where required.
41. Product category changes do not create a new Product identity.
42. Product archival does not erase historical Product references.
43. Transaction resource UUIDs must never be reused for another transaction.
44. Financial resource identity must remain stable.
45. Cash Session identity must remain stable.
46. Shift Handover identity must remain stable.
47. Report Versions are independently identifiable when required by the report model.
48. Immutable resources must not support unrestricted generic mutation.
49. Physical deletion must follow the defined data lifecycle.
50. Archive/deactivate/cancel/supersede must be used where domain rules prohibit physical deletion.
51. Resource creation cannot arbitrarily assign protected ownership relationships.
52. Server controls authoritative timestamps where required.
53. Timestamp semantics must be explicit.
54. Timezone-aware timestamps represent instants.
55. Calendar dates remain distinct from timestamps.
56. Monetary values use a deterministic representation.
57. Monetary field representation must remain stable within a supported API version.
58. Quantity values must have explicit unit semantics.
59. Boolean fields must use clear semantic names.
60. Resource type identifiers use stable canonical names where required.
61. Resource version identity must remain distinguishable from ordinary resource identity.
62. Effective configuration references must identify the configuration used when historical traceability is required.
63. Collection ordering must be deterministic.
64. Resource naming must not determine authorization.
65. Resource existence must not imply permission to access it.
66. Resource responses must not automatically expose unrelated sensitive data.
67. Cache keys using resource IDs must preserve required Business and Branch scope.
68. Offline clients must use canonical resource identity after synchronization.
69. Client-generated UUIDs remain subject to server validation.
70. Duplicate UUID submissions must be handled deterministically.
71. Temporary client identifiers must not be confused with authoritative resource UUIDs.
72. Audit records should reference canonical resource identities.
73. Webhook resource references must use canonical resource identities.
74. External integrations must use documented public resource terminology.
75. API resource identity must remain compatible with the API versioning strategy.
76. Renaming a public resource is a contract change.
77. Permanent aliases should be avoided unless justified.
78. CRUD operations are supported only where compatible with domain lifecycle rules.
79. PATCH is used for partial updates where partial update semantics are defined.
80. PUT is used only where replacement semantics are explicitly defined.
81. POST is used for business commands that create domain effects.
82. DELETE is used only where deletion semantics are explicitly supported.
83. Resource commands must preserve idempotency semantics where required.
84. Resource naming must remain consistent across API, documentation and OpenAPI.
85. New resources must not duplicate an existing domain concept.
86. Resource model must remain independent from ORM and database implementation.
87. Resource relationships must preserve Business isolation.
88. Resource relationships must preserve Branch isolation.
89. Historical snapshots must remain independent from current cached resource representations.
90. Resource naming must remain predictable for frontend, POS, offline and external clients.

---

# 120. Related Documents

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/04_Architecture/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend

* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

### Security

* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`

---

# 121. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `05_API_Resource_Model_and_Naming.md`

**Previous Document:** `04_API_Versioning_and_Backward_Compatibility.md`

**Next Document:** `06_API_Authentication_and_Request_Context.md`

