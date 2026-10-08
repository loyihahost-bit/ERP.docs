# Domain Service and Business Logic

**Document ID:** BE-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines how business rules and domain behavior are implemented in FastFood ERP.

The Domain Layer represents the business meaning of the system.

It must protect important business invariants regardless of whether an operation originates from:

* Web UI;
* API;
* trusted offline device;
* synchronization;
* background job;
* administrative operation.

The Domain Layer must not depend on HTTP, frontend behavior, database implementation details, or external service providers.

---

## 2. Domain Layer Principle

The Domain Layer answers:

> What is allowed according to the business rules?

The Application Layer answers:

> In what workflow should these rules be executed?

Example:

```text
Application:
AcceptOrderUseCase
        ↓
Domain:
Order.accept()
Inventory.canDeduct()
Pricing.resolve()
        ↓
Application:
persist + audit + outbox
```

---

## 3. Domain Responsibilities

The Domain Layer is responsible for:

1. Business invariants.
2. Entity behavior.
3. Value objects.
4. Domain services.
5. State transitions.
6. Business calculations.
7. Domain validation.
8. Domain events where appropriate.
9. Cross-entity business rules that cannot naturally belong to one entity.

The Domain Layer is not responsible for:

* HTTP;
* authentication tokens;
* SQL queries;
* ORM session management;
* API response formatting;
* notification delivery;
* file generation;
* database transactions.

---

# 4. Domain Model Categories

The domain should distinguish between:

### Entities

Objects with stable identity.

Examples:

```text
Business
Branch
Employee
Product
Recipe
Order
Payment
CashSession
InventoryItem
Report
```

### Value Objects

Objects defined by their value rather than independent identity.

Examples:

```text
Money
Quantity
Percentage
PhoneNumber
Address
DateRange
Price
```

### Domain Services

Business operations that do not naturally belong to one entity.

Examples:

```text
PricingService
InventoryCostService
OrderPricingService
CashCalculationService
RecipeAvailabilityService
```

---

# 5. Entity Identity

Entities must have stable UUID-based identity.

An entity's identity must not change because of:

* rename;
* category change;
* price change;
* Branch configuration;
* recipe change;
* archive;
* status change.

Historical records must continue referencing the original entity identity.

---

# 6. Entity Behavior

Important entities should expose behavior rather than allowing unrestricted state mutation.

Preferred:

```text
order.accept()
order.cancel(reason)
order.add_item(...)
cash_session.close(...)
product.archive()
recipe.approve(...)
```

Avoid:

```text
order.status = "accepted"
cash_session.status = "closed"
product.deleted = True
```

when those changes bypass business rules.

---

# 7. Invariant Protection

An invariant is a condition that must always remain true.

Examples:

```text
Closed Cash Session cannot be reopened.

Inventory cannot become negative.

Historical Order Item price cannot change.

Inactive Product cannot be newly sold.

Payment cannot be silently duplicated.

Business-owned records cannot cross Business boundaries.
```

Important invariants must be enforced in backend business logic rather than relying on frontend behavior.

---

# 8. State Transitions

Entities with lifecycle states should define valid transitions.

Example:

```text
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

Invalid transitions must be rejected.

Example:

```text
Served → Draft
```

must not be possible through an ordinary operation.

---

# 9. Order Domain

The Order domain owns order lifecycle rules.

The Order domain should control:

* order state;
* order item consistency;
* order modification rules;
* cancellation rules;
* financial snapshot integrity;
* order acceptance conditions;
* historical state.

The Application Layer coordinates repositories and transactions.

---

# 10. Order Acceptance

An Order can be accepted only when required conditions are satisfied.

Typical domain checks include:

```text
Order is editable
+
required items exist
+
Product configuration is valid
+
Recipe/Set requirements are satisfied
+
required operational availability exists
+
inventory requirements are satisfied
```

The exact inventory deduction workflow is coordinated by the Application Layer.

---

# 11. Order Item Price Snapshot

When a Product is added to an Order, the applicable price is captured.

The snapshot may contain:

```text
product_id
price
pricing_configuration_version
discount information where applicable
markup information where applicable
```

Later Product price changes must not modify the snapshot.

---

# 12. Order Historical Integrity

Historical Order data must remain reconstructable.

The Domain Layer must prevent ordinary operations from silently changing:

* original item price;
* applied discount;
* markup result;
* payment history;
* refund history;
* relevant Recipe Version;
* relevant Set Version.

Corrections must create explicit historical records.

---

# 13. Product Domain

The Product domain controls:

* Product identity;
* Product type;
* active/inactive state;
* category association;
* recipe dependency;
* archive behavior.

A Product with historical references must not be physically removed through ordinary business operations.

---

# 14. Product Types

The domain supports:

```text
Raw Material
Semi-Finished Product
Finished Product
Set
```

Exact implementation may separate Set into its own aggregate/domain model.

A Product's type determines which business rules apply.

---

# 15. Product Archive

When a Product cannot safely be deleted because historical records reference it:

```text
Active
   ↓
Inactive / Archived
```

Historical references remain valid.

Archiving must not remove:

* Order history;
* Inventory history;
* Recipe history;
* Set history;
* Audit history.

---

# 16. Recipe Domain

The Recipe domain controls:

* Recipe structure;
* component quantities;
* Recipe Version;
* approval state;
* effective version;
* historical version integrity.

A Recipe change must not modify historical Recipe Versions.

---

# 17. Recipe Versioning

A Recipe change creates a new version when it changes operational behavior.

Example:

```text
Recipe V1
   ↓
Recipe V2
   ↓
Recipe V3
```

Existing historical inventory deductions remain associated with the relevant version.

---

# 18. Recipe Approval

A Recipe Version may require approval before becoming effective.

Conceptual lifecycle:

```text
Draft
  ↓
Pending Approval
  ↓
Approved
  ↓
Effective
  ↓
Superseded
```

Only an approved/effective version may be used where the business rules require it.

---

# 19. Recipe Composition

Recipe components may include:

* Raw Material;
* Semi-Finished Product;
* required quantity;
* unit of measure;
* loss/yield information where applicable.

The domain must prevent invalid recursive or structurally invalid recipes.

---

# 20. Recipe Dependency

Example:

```text
Raw Material
     ↓
Semi-Finished Product
     ↓
Finished Product
```

The domain must preserve traceability.

When a Finished Product consumes a Semi-Finished Product, the inventory system must be able to determine the underlying dependency when required.

---

# 21. Set Domain

A Set represents a predefined collection of Products.

A Set may have:

* own identity;
* own configuration;
* own price;
* component Products;
* Set Version.

Set configuration is distinct from individual Product Recipe configuration.

---

# 22. Set Component Substitution

Normal Set sale does not permit arbitrary component substitution.

If a substitution feature is introduced later, it must be implemented as an explicit business capability with its own pricing and inventory rules.

The current domain must not silently substitute components.

---

# 23. Inventory Domain

Inventory business logic controls:

* stock quantity;
* stock movement;
* inventory transactions;
* FIFO layers;
* cost information;
* adjustment;
* availability.

Stock must never become negative through a valid committed business operation.

---

# 24. Inventory Deduction

Inventory deduction should be based on the applicable Product/Recipe configuration.

Example:

```text
Order
  ↓
Finished Product
  ↓
Recipe Version
  ↓
Required Components
  ↓
Inventory Deduction
```

The deduction must preserve the Recipe Version used by the transaction where historical traceability is required.

---

# 25. Inventory Availability

Inventory availability is separate from Menu availability.

A Product may be:

```text
Menu Active
+
Inventory Insufficient
```

In this case, normal sale may be blocked according to the business rule.

Disabling a Product in the menu must not modify its stock.

---

# 26. FIFO Domain Rules

Where FIFO is applicable, inventory cost calculations must use the correct inventory layers.

The domain must preserve:

* layer identity;
* quantity;
* acquisition cost;
* remaining quantity;
* source transaction.

Historical consumption must remain attributable to the appropriate layer.

---

# 27. Inventory Adjustment

An adjustment is an explicit business operation.

It must preserve:

```text
Before Quantity
Adjustment
After Quantity
Reason
Actor
Branch
Warehouse
Timestamp
```

Direct assignment of arbitrary stock values is prohibited.

---

# 28. Pricing Domain

Pricing business logic is responsible for:

* standard price;
* Branch override;
* effective configuration;
* transaction price;
* discount;
* markup;
* Set price.

Pricing must preserve the distinction between:

```text
Selling Price
Inventory Cost
Discount
Markup
Historical Transaction Price
```

---

# 29. Standard Price

The Business may define a standard Product price.

A Branch may override it where authorized.

The domain must ensure that a Branch override:

* affects only that Branch;
* does not modify the global standard price;
* does not affect another Branch.

---

# 30. Effective Price Resolution

The effective selling price is conceptually resolved as:

```text
Business Product Price
        ↓
Branch Override
        ↓
Effective Configuration
        ↓
Transaction Price
```

The resulting price is then captured in the Order Item snapshot.

---

# 31. Discount Domain

Discounts are transaction-level adjustments.

A discount must not mutate the Product's configured base price.

Example:

```text
Product Price = 30,000

Discount = 5,000

Final Amount = 25,000
```

The Product price remains 30,000.

---

# 32. Discount Validation

The domain should validate applicable discount rules such as:

* amount/range;
* Order state;
* permitted discount type;
* required authorization;
* financial consistency.

Authorization itself is coordinated through the Application/Security layer.

---

# 33. Custom Markup

Custom markup is a transaction-specific pricing operation.

Allowed range:

```text
0% ≤ Markup ≤ 100%
```

Calculation:

```text
Final Price = Last Purchase Cost × (1 + Markup / 100)
```

The domain must validate the mathematical result and applicable cost.

---

# 34. Money

Money must use an exact representation.

Floating-point arithmetic must not be used for financial values.

The domain should use a dedicated `Money` value object or equivalent exact numeric representation.

Money should contain:

```text
amount
currency
```

where currency is required by the financial model.

---

# 35. Quantity

Inventory and recipe quantities should use an explicit quantity representation.

Quantity must preserve the required precision for the relevant unit.

Examples:

```text
1 kg
250 g
0.5 l
2 pieces
```

The domain must reject invalid negative quantities where the operation does not permit them.

---

# 36. Percentage

Percentage values should use a dedicated value representation where useful.

Examples:

```text
Discount Percentage
Markup Percentage
Loss Percentage
```

The domain should enforce allowed ranges.

Example:

```text
Markup:
0%–100%
```

---

# 37. Cash Domain

Cash Session domain controls:

* opening;
* active state;
* closing;
* expected cash;
* actual cash;
* difference;
* session lifecycle.

A Cash Session must not be reopened after final closure.

---

# 38. Cash Session State

Conceptual lifecycle:

```text
Closed / Not Open
       ↓
Open
       ↓
Closing
       ↓
Closed
```

The exact persisted states may differ, but the domain must prevent invalid lifecycle transitions.

---

# 39. Cash Difference

At closing:

```text
Difference = Actual Cash - Expected Cash
```

The domain must preserve the calculated result.

A correction must create a new explicit correction record rather than silently changing the historical close.

---

# 40. Shift Handover Domain

Shift handover represents the transfer of operational responsibility between cashiers.

The domain should preserve:

```text
Previous Cashier
New Cashier
Previous Session
New Session
Transferred Cash
Actual Count
Difference
Confirmation
```

The handover must remain historically traceable.

---

# 41. Payment Domain

Payment logic controls:

* payment amount;
* payment method;
* payment state;
* payment association with Order;
* mixed payment composition;
* overpayment;
* historical financial state.

Supported methods include:

```text
Cash
Card
Debt
Mixed
```

---

# 42. Payment Idempotency

The Payment domain must prevent the same logical payment operation from being applied twice.

The Application Layer provides operation-level idempotency.

The Domain Layer ensures that an invalid duplicate financial state cannot be created.

---

# 43. Overpayment

If overpayment is permitted:

```text
Order Amount = 100,000
Paid = 120,000
Overpayment = 20,000
```

The additional amount must be represented according to the financial model.

It must not silently alter the original Order price.

---

# 44. Debt Domain

Debt represents an outstanding financial obligation.

The domain should preserve:

* debtor identity where applicable;
* original debt;
* repayments;
* remaining balance;
* history.

Partial repayment must not rewrite the original debt transaction.

---

# 45. Refund Domain

Refund is a separate financial operation.

Refund rules must use historical transaction information.

Current Product pricing must not reinterpret the original refund.

Refunds must preserve:

* original payment;
* refund amount;
* reason;
* actor;
* timestamp;
* correction/revision chain where applicable.

---

# 46. Attendance Domain

Attendance logic controls:

* employee attendance state;
* working period;
* applicable branch context;
* attendance corrections where permitted.

Attendance should not be directly rewritten without preserving correction history.

---

# 47. Payroll Domain

Payroll calculations must support the configured compensation model.

Supported models may include:

```text
Fixed
Percentage
Shift
Hybrid
Daily
Bonus
```

The exact calculation rules belong to the payroll domain configuration.

Payroll calculations must be deterministic and reproducible.

---

# 48. Configuration Domain

Configuration changes that affect operational behavior should be versioned.

Examples:

* menu;
* price;
* Set configuration;
* workflow configuration;
* order statuses;
* other business configuration.

The domain must preserve historical configuration identity.

---

# 49. Configuration Effective Boundary

For the current system, important menu/pricing configuration becomes operational from the next Cash Session.

The domain must therefore distinguish:

```text
Current Active Configuration
Pending Configuration
Historical Configuration
```

An active Cash Session must not silently switch to a newly created configuration.

---

# 50. Configuration Concurrency

When changing configuration:

```text
Current Version = V5

Employee A → creates V6
Employee B → tries to update V5
```

Employee B's stale update must be rejected.

The domain must not support silent last-write-wins for important configuration.

---

# 51. Business Domain

Business lifecycle controls:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The domain must prevent operations that are incompatible with the current lifecycle state.

For example:

```text
DELETED → active operational transaction
```

must never be allowed.

---

# 52. Branch Domain

Branch behavior includes:

* Branch identity;
* active/inactive state;
* Business ownership;
* operational configuration;
* employee scope.

A Branch cannot belong to multiple Businesses.

---

# 53. Employee Domain

Employee domain behavior may include:

* active/inactive state;
* Branch assignments;
* role assignment;
* permission override configuration.

Permission evaluation itself should remain centralized rather than duplicated across domain entities.

---

# 54. Device Domain

Trusted devices have their own lifecycle.

Example:

```text
Registered
   ↓
Trusted
   ↓
Active
   ↓
Revoked
```

A revoked device must not continue to be treated as trusted by synchronization logic.

---

# 55. Offline Authorization Domain Rules

Offline authorization may be represented by a signed, time-bounded authorization context.

The domain/application system must validate:

* device identity;
* Business;
* validity period;
* authorization state;
* required security context.

Offline authorization must not grant permissions that the employee did not have.

---

# 56. Audit Domain

Audit represents immutable historical facts.

The domain should expose meaningful events such as:

```text
OrderAccepted
PaymentRecorded
CashSessionClosed
PriceChanged
RecipeApproved
InventoryAdjusted
EmployeeDeactivated
```

The audit persistence mechanism belongs to Infrastructure.

---

# 57. Domain Events

Domain events may be used when a domain operation produces meaningful business facts.

Example:

```text
OrderAccepted
PaymentRecorded
RecipeApproved
CashSessionClosed
```

A domain event should describe what happened.

It should not directly send notifications or perform database queries.

---

# 58. Domain Event Handling

Preferred flow:

```text
Domain Operation
      ↓
Domain Event
      ↓
Application / Outbox
      ↓
Background Handler
      ↓
Notification / Report / Secondary Action
```

This keeps the Domain Layer independent of infrastructure.

---

# 59. Domain Service

A Domain Service should be used when a business operation:

* spans multiple entities;
* does not naturally belong to one entity;
* contains meaningful business logic.

Examples:

```text
OrderPricingService
RecipeAvailabilityService
InventoryCostService
CashCalculationService
ConfigurationResolutionService
```

---

# 60. Domain Service Example

Pricing resolution may conceptually be:

```text
resolve_price(
    business_product,
    branch_configuration,
    transaction_context
)
```

The service determines the applicable business price according to domain rules.

It does not:

* read HTTP requests;
* query SQL directly;
* save database records;
* send notifications.

---

# 61. Domain Service vs Application Service

### Domain Service

Contains business logic.

```text
Can this Product be sold?
How should this price be calculated?
How should FIFO cost be determined?
```

### Application Service

Coordinates the workflow.

```text
Load Product
→ call domain service
→ save result
→ create audit
→ commit
```

---

# 62. Domain Repository Dependency

The Domain Layer should not depend directly on SQLAlchemy repositories.

Where a domain service genuinely needs persisted information, the architecture should expose an appropriate abstraction without coupling the domain to the database implementation.

The preferred design is to keep persistence orchestration in the Application Layer whenever practical.

---

# 63. Domain Validation

Domain validation should reject invalid business state.

Examples:

```text
Negative inventory
Invalid Order transition
Invalid payment amount
Invalid markup
Closed session reopening
Invalid Recipe Version
Invalid Set composition
Invalid configuration transition
```

Validation errors should use domain-specific exceptions or result types.

---

# 64. Domain Exceptions

Examples:

```text
InvalidOrderState
InsufficientInventory
InvalidPayment
CashSessionClosed
InvalidRecipeVersion
InvalidMarkup
InvalidConfigurationTransition
ProductUnavailable
InvalidSetConfiguration
```

These errors should describe business meaning.

Transport-specific status codes do not belong in the Domain Layer.

---

# 65. Domain Calculations

Business calculations must be deterministic.

Examples:

```text
Order total
Discount
Markup
Cash difference
Debt balance
Payroll amount
Inventory consumption
FIFO cost
```

Calculations must use exact numeric representations where financial precision matters.

---

# 66. Historical Calculation Rule

Historical calculations must use the historical snapshot relevant to the transaction.

The domain must not use today's:

* Product price;
* Recipe;
* Set configuration;
* Branch price;
* discount configuration

to reinterpret a historical transaction.

---

# 67. Domain and Offline Operations

Offline-originated operations eventually enter the same domain rules.

Example:

```text
Offline Order
      ↓
Synchronization
      ↓
Application Use Case
      ↓
Domain Validation
      ↓
Persist
```

Offline status must not bypass domain invariants.

---

# 68. Domain and Background Jobs

Background jobs must invoke application use cases or appropriate domain services.

They must not directly modify business state through uncontrolled database writes.

Example:

```text
ReportJob
   ↓
GenerateReportUseCase

NotificationJob
   ↓
NotificationApplicationService
```

---

# 69. Domain Purity

The Domain Layer must remain independent from:

* Flask/FastAPI;
* SQLAlchemy;
* Redis;
* Celery/RQ or another worker;
* SMTP;
* filesystem;
* HTTP clients;
* PostgreSQL-specific APIs.

This keeps the business model testable and portable.

---

# 70. Domain Testing

Domain tests should not require:

* HTTP server;
* PostgreSQL;
* Redis;
* external services.

Pure domain tests should execute business rules directly.

Example:

```text
order.accept()
```

can be tested without creating an HTTP request.

---

# 71. Application + Domain Testing

Integration tests should verify that the Application Layer correctly coordinates Domain behavior.

Example:

```text
AcceptOrderUseCase
    ↓
Order domain
    ↓
Inventory domain
    ↓
Repositories
    ↓
Transaction
```

This is separate from pure domain unit testing.

---

# 72. Domain Invariants

The following invariants must be protected:

1. Entity identity remains stable.
2. Invalid lifecycle transitions are rejected.
3. Historical transaction snapshots are immutable.
4. Inventory cannot become negative.
5. Closed Cash Sessions cannot reopen normally.
6. Product archive does not destroy historical references.
7. Recipe Versions remain immutable.
8. Set Versions remain historically identifiable.
9. Current pricing does not rewrite historical Orders.
10. Current Recipes do not rewrite historical inventory deductions.
11. Current configuration does not reinterpret historical transactions.
12. Discounts remain separate from base Product pricing.
13. Markup remains within the configured allowed range.
14. Payment state remains financially consistent.
15. Duplicate logical payments cannot create duplicate financial effects.
16. Debt balance remains mathematically consistent.
17. Cash difference remains derived from authoritative session values.
18. Branch-specific configuration remains Branch-scoped.
19. Business-specific entities cannot cross Business boundaries.
20. Offline operations cannot bypass domain rules.
21. Configuration conflicts are explicit.
22. Domain calculations are deterministic.
23. Historical corrections create explicit history rather than silent mutation.
24. Domain rules do not depend on frontend behavior.
25. Domain rules do not depend on transport mechanisms.

---

# 73. Domain Guardrails

The following are prohibited:

1. SQL queries inside domain entities.
2. ORM model manipulation inside domain entities.
3. HTTP requests inside domain services.
4. API response objects inside domain logic.
5. Notification sending from domain entities.
6. Direct Redis usage in domain logic.
7. Direct filesystem operations in domain logic.
8. Direct database commits in domain logic.
9. Permission checks based only on frontend state.
10. Historical record mutation for convenience.
11. Silent configuration overwrites.
12. Floating-point financial calculations.
13. Arbitrary direct state assignment bypassing invariants.
14. Business rules duplicated across unrelated layers.
15. Domain services becoming generic utility classes without business meaning.

---

# 74. Recommended Domain Structure

The Domain Layer should follow the project structure defined in BE-02:

```text
app/domain/
├── business/
├── branch/
├── identity/
├── subscription/
├── device/
├── product/
├── recipe/
├── set/
├── inventory/
├── menu/
├── pricing/
├── order/
├── table/
├── payment/
├── debt/
├── cash/
├── handover/
├── attendance/
├── payroll/
├── notification/
├── audit/
├── report/
├── synchronization/
├── configuration/
└── lifecycle/
```

Each domain module should contain only the business concepts relevant to that area.

---

# 75. Domain Module Example

Example:

```text
app/domain/order/
├── entities.py
├── value_objects.py
├── services.py
├── events.py
├── exceptions.py
└── rules.py
```

Not every module must contain every file.

Empty abstraction should be avoided.

---

# 76. Shared Domain Concepts

Only genuinely cross-domain concepts should be placed in shared domain modules.

Examples:

```text
Money
Quantity
Percentage
DomainEvent
EntityId
```

The shared domain area must remain small.

It must not become a dumping ground for unrelated business logic.

---

# 77. Domain Dependency Rules

Preferred dependency direction:

```text
Application
    ↓
Domain
```

Domain must not depend on Application.

Domain must not depend on:

```text
API
Database
Infrastructure
Background Workers
Frontend
External Providers
```

---

# 78. Domain Logic Duplication

The same business rule must not be implemented independently in:

* frontend;
* API route;
* application service;
* synchronization handler;
* background worker.

The authoritative rule belongs in the Domain Layer when it is a domain invariant.

Other layers may perform preliminary validation for usability, but they must not replace domain validation.

---

# 79. Frontend Validation

Frontend validation is allowed for user experience.

Example:

```text
Markup must be between 0 and 100
```

The frontend may immediately display an error.

However, the backend domain must validate the same invariant again.

Frontend validation is never authoritative.

---

# 80. Domain Versioning

Domain behavior changes must be reflected through the appropriate documentation and migration process.

A change to an important business rule should be reviewed against:

* Business Analysis;
* System Analysis;
* Database model;
* API behavior;
* tests;
* audit/history requirements.

Architecture-changing decisions should be recorded through ADRs where appropriate.

---

# 81. Example End-to-End Flow

Example: Product price change.

```text
API
 ↓
ChangeProductPriceUseCase
 ↓
Authorization
 ↓
Load Product Configuration
 ↓
Domain:
    validate price
    validate state
    create new configuration version
 ↓
Repository
 ↓
Audit
 ↓
Outbox
 ↓
Commit
```

The Domain Layer determines whether the new configuration is valid.

The Application Layer controls the workflow and transaction.

---

# 82. Example End-to-End Order Flow

```text
CreateOrderUseCase
        ↓
Order Domain
        ↓
Draft Order
        ↓
AddOrderItemUseCase
        ↓
Pricing Domain
        ↓
Price Snapshot
        ↓
AcceptOrderUseCase
        ↓
Inventory Domain
        ↓
Recipe Domain
        ↓
Order.accept()
        ↓
Audit + Outbox
        ↓
Commit
```

Each layer has a clear responsibility.

---

# 83. Performance Principles

Domain logic must remain efficient enough for POS operations.

Avoid:

* unnecessary object creation;
* repeated calculations;
* uncontrolled recursive loading;
* network operations;
* database calls from entities.

The Domain Layer should perform deterministic business calculations using already-loaded data whenever practical.

---

# 84. Security Principles

Security-sensitive business rules must remain enforced server-side.

Examples:

```text
Cannot sell inactive Product.
Cannot reopen closed Cash Session.
Cannot modify historical Payment.
Cannot bypass subscription restriction.
Cannot use another Business's Product.
Cannot use another Branch's configuration.
```

The Domain Layer protects business invariants; the Application/Security layers protect identity and access.

---

# 85. Recovery Principles

Domain recovery should prefer explicit state transitions.

Avoid:

```text
DELETE bad record
INSERT replacement record
```

when historical integrity requires a correction chain.

Prefer:

```text
Original State
      ↓
Correction
      ↓
New Authoritative State
```

The original historical event remains preserved.

---

# 86. Documentation Requirements

Any important domain rule introduced during implementation should be traceable to one or more of:

* Business Analysis requirement;
* System Analysis rule;
* Database invariant;
* API contract;
* ADR.

This prevents undocumented business behavior from appearing in code.

---

# 87. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `03_Application_and_Use_Case_Layer.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/02_Database_Architecture.md`
* `../05_Database/08_Product_and_Category_Data_Model.md`
* `../05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `../05_Database/10_Set_and_Set_Version_Data_Model.md`
* `../05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `../05_Database/12_Menu_and_Pricing_Data_Model.md`
* `../05_Database/13_Order_and_Order_Item_Data_Model.md`
* `../05_Database/15_Payment_and_Debt_Data_Model.md`
* `../05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `../05_Database/23_Configuration_Data_Model.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/16_Inventory_Transaction_System.md`
* `../02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `../02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `../02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 88. Status

**Backend Architecture:** Accepted

**Application Layer:** Accepted

**Domain Layer:** Accepted

**Business Logic:** Domain-owned

**Application Workflow:** Application-owned

**Persistence:** Infrastructure-owned

**Transaction Boundary:** Application-owned

**Historical Integrity:** Domain invariant

**Next Document:** `05_Repository_and_Data_Access.md`

