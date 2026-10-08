# Backend Architecture

**Document ID:** ARCH-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the backend architecture of FastFood ERP.

The backend is responsible for:

* enforcing business rules;
* protecting tenant and branch boundaries;
* executing application use cases;
* validating authorization;
* managing transactions;
* maintaining domain state;
* processing offline synchronization;
* generating reports;
* publishing domain/application events;
* maintaining audit and historical integrity;
* executing background jobs;
* exposing APIs to frontend and trusted devices.

The backend must remain modular, testable, secure, and suitable for gradual scaling.

The architecture must support the current SaaS deployment without requiring premature microservices.

---

# 2. Backend Architecture Principles

The backend follows these principles:

1. **Domain ownership**
2. **Explicit module boundaries**
3. **Application-layer orchestration**
4. **Server-side authorization**
5. **Tenant isolation**
6. **Branch isolation**
7. **Transactional integrity**
8. **Idempotent operations**
9. **Historical integrity**
10. **Offline continuity**
11. **Explicit synchronization**
12. **Asynchronous processing where appropriate**
13. **Read/write separation where useful**
14. **Minimal shared infrastructure**
15. **Testability**
16. **Operational observability**
17. **Performance without unnecessary complexity**

The backend must not allow convenience to bypass domain boundaries.

---

# 3. Backend Logical Structure

The backend is organized into the following logical layers:

```text
API / Transport
      ↓
Application
      ↓
Domain
      ↓
Infrastructure
      ↓
Database / External Services
```

A typical request flows as:

```text
HTTP Request
    ↓
API Endpoint
    ↓
Authentication
    ↓
Execution Context
    ↓
Authorization
    ↓
Application Use Case
    ↓
Domain Logic
    ↓
Repository / Infrastructure
    ↓
Transaction Commit
    ↓
Domain/Application Events
    ↓
Response
```

The API layer must not directly manipulate domain persistence.

---

# 4. API Layer

The API layer is responsible for transport concerns.

It handles:

* HTTP requests;
* request parsing;
* input schema validation;
* authentication extraction;
* response serialization;
* API error mapping;
* pagination;
* filtering;
* sorting;
* request metadata;
* correlation IDs;
* idempotency metadata.

The API layer must not contain core business rules.

## 4.1. API Responsibilities

The API layer may perform:

* required field validation;
* data type validation;
* format validation;
* request size validation;
* authentication token extraction;
* pagination validation;
* basic request normalization.

The API layer must delegate business decisions to the Application Layer.

## 4.2. API Must Not

The API layer must not:

* directly update database tables;
* calculate inventory deductions;
* determine payment authorization;
* decide subscription entitlement;
* modify cash sessions directly;
* resolve domain conflicts;
* bypass application use cases;
* implement duplicate business logic.

---

# 5. Application Layer

The Application Layer is the main backend orchestration layer.

It coordinates:

* use cases;
* commands;
* queries;
* authorization;
* subscription checks;
* branch scope;
* device trust;
* transaction boundaries;
* domain services;
* repositories;
* events;
* background processing;
* synchronization.

Examples:

```text
CreateOrder
AcceptOrder
ModifyOrder
CancelOrder

OpenCashSession
CloseCashSession
HandoverCashSession

CreatePayment
RecordDebtRepayment
CreateRefund

AdjustInventory
ReceivePurchase
ApproveRecipe

GenerateReport
ExportReport

SyncOfflineBatch
ResolveConflict
```

Each use case should represent a meaningful business operation.

---

# 6. Use Case Structure

A typical application use case should follow this structure:

```text
1. Receive command/query
2. Build execution context
3. Authenticate actor
4. Validate Business context
5. Validate Branch context
6. Validate Device context
7. Validate Subscription entitlement
8. Validate permission
9. Load required aggregates
10. Execute domain operation
11. Persist state
12. Record audit information where required
13. Publish required events
14. Commit transaction
15. Return result
```

Not every use case requires every step.

For example, a public read-only report may not require a Device Trust check.

---

# 7. Execution Context

Every important application operation should execute inside an explicit context.

A conceptual execution context contains:

```text
ExecutionContext
├── Business UUID
├── Branch UUID
├── Employee UUID
├── Device UUID
├── Cash Session UUID
├── Transaction UUID
├── Correlation ID
├── Authentication state
├── Permission state
├── Subscription entitlement state
├── Offline/Online mode
└── Request timestamp
```

Not every field is mandatory for every operation.

The context must prevent accidental operations outside the authorized scope.

---

# 8. Command Model

Commands represent state-changing operations.

Examples:

```text
CreateOrderCommand
AcceptOrderCommand
ModifyOrderCommand
CancelOrderCommand

OpenCashSessionCommand
CloseCashSessionCommand
HandoverCashSessionCommand

CreatePaymentCommand
CreateRefundCommand

AdjustInventoryCommand
ReceivePurchaseCommand

ApproveRecipeCommand
ActivateMenuConfigurationCommand

ResolveSyncConflictCommand
```

Commands should contain the information required to execute the operation.

They should not contain infrastructure dependencies.

---

# 9. Query Model

Queries represent read operations.

Examples:

```text
GetOrderQuery
ListOrdersQuery
GetCashSessionQuery
GetInventoryQuery
GetEmployeeQuery
GetPayrollQuery
GetReportQuery
GetAuditHistoryQuery
GetNotificationsQuery
```

Queries should not modify domain state.

Read models may be optimized independently from transactional models.

---

# 10. Domain Layer

The Domain Layer contains business behavior and domain rules.

It owns:

* aggregates;
* entities;
* value objects;
* domain services;
* domain events;
* invariants;
* domain policies.

The Domain Layer must not depend on:

* HTTP;
* framework-specific controllers;
* database implementation;
* ORM session management;
* frontend;
* message broker implementation.

The domain must remain independently testable.

---

# 11. Infrastructure Layer

Infrastructure implements technical capabilities required by the application.

Examples include:

```text
Database
Repositories
Transaction Manager
Cache
Message/Event Infrastructure
Background Job Queue
File Storage
Excel Export
Clock
Cryptography
Device Trust Storage
External Integrations
Logging
Metrics
```

Infrastructure implements interfaces defined by higher layers.

---

# 12. Repository Architecture

Repositories provide domain/application access to persistent state.

A repository belongs to the module that owns the aggregate.

Examples:

```text
OrderRepository
CashSessionRepository
InventoryRepository
PaymentRepository
EmployeeRepository
RecipeRepository
ReportRepository
DeviceRepository
```

A module must not directly use another module's repository to modify its state.

For cross-module operations:

```text
Application Use Case
        ↓
Module A Application Service
        ↓
Module A Domain
        ↓
Module B Application Service / Domain Contract
```

The exact mechanism depends on consistency requirements.

---

# 13. Aggregate Persistence

Aggregates should be persisted as controlled transactional units.

An application use case should load an aggregate, execute its operation, and persist the resulting state.

Example:

```text
AcceptOrder
    ↓
Load Order Aggregate
    ↓
Validate Order
    ↓
Validate Inventory
    ↓
Deduct Inventory
    ↓
Change Order State
    ↓
Persist
    ↓
Commit
```

The transaction boundary must correspond to the actual business consistency requirement.

---

# 14. Transaction Management

Critical business operations must use database transactions.

Examples:

* accepting an order;
* deducting inventory;
* creating a payment;
* closing a cash session;
* recording a refund;
* applying an inventory correction;
* approving important configuration;
* resolving a synchronization conflict.

The backend must ensure atomicity where required.

For example:

```text
Accept Order
+
Inventory Deduction
```

must not result in:

```text
Order Accepted
Inventory Not Deducted
```

or:

```text
Inventory Deducted
Order Not Accepted
```

when both operations belong to the same atomic business transaction.

---

# 15. Strong Consistency

Strong consistency is required for operations where incorrect state could cause financial, inventory, or operational corruption.

Examples:

* inventory deduction;
* payment amount validation;
* cash session opening;
* cash session closing;
* correction limits;
* order acceptance;
* subscription entitlement enforcement;
* permission enforcement;
* employee activation/deactivation;
* configuration activation boundaries.

The backend must use appropriate database transactions and concurrency controls.

---

# 16. Eventual Consistency

Eventual consistency is appropriate for secondary processing.

Examples:

* notifications;
* audit processing where safely decoupled;
* report generation;
* Excel export;
* analytics;
* non-critical UI updates;
* background synchronization tasks.

Secondary processing must never silently change the result of the core transaction.

---

# 17. Domain Events

Domain events describe important state changes.

Examples:

```text
OrderAccepted
OrderCancelled
OrderModified

PaymentCompleted
RefundCreated
DebtRepaymentRecorded

CashSessionOpened
CashSessionClosed
CashSessionHandoverCompleted

InventoryAdjusted
InventoryReceived
InventoryShortageDetected

RecipeApproved
ConfigurationActivated

EmployeeDeactivated
PayrollFinalized

SubscriptionExpired
BusinessDeletionEligible

SyncConflictDetected
ConflictResolved
```

Domain events should represent business facts rather than technical implementation details.

---

# 18. Event Handling

Events may trigger:

* notifications;
* audit entries;
* report invalidation;
* background jobs;
* synchronization state updates;
* derived read models.

Example:

```text
OrderAccepted
    ├── Notify Kitchen
    ├── Create Audit Entry
    └── Update Relevant Read Models
```

These secondary handlers must not modify the original transaction result.

---

# 19. Transactional Event Reliability

Critical events must not be lost because the application crashes after database commit.

The backend should use a reliable event publication strategy.

A preferred approach is an outbox-style pattern:

```text
Database Transaction
├── Domain State
└── Outbox Event

        ↓

Outbox Processor

        ↓

Event Handler
```

This ensures that state and the intention to publish an event are committed together.

---

# 20. Idempotency

State-changing operations must support idempotency where duplicate requests are possible.

This is especially important for:

* offline synchronization;
* payment submission;
* order acceptance;
* inventory operations;
* cash operations;
* report generation;
* background jobs;
* event processing.

The system uses UUID-based operation identity.

Client Transaction ID is not part of the system identity model.

A repeated operation with the same valid transaction UUID must not create duplicate business effects.

---

# 21. Idempotency Handling

Conceptually:

```text
Incoming Transaction UUID
        ↓
Check Existing Operation
        ↓
 ┌───────────────┐
 │ Exists?       │
 └───────┬───────┘
         │
     Yes │ No
         │
 Return  Execute
 Existing Operation
 Result      ↓
        Persist Result
```

Idempotency records must be scoped appropriately to Business and operation type.

---

# 22. Concurrency Control

The backend must explicitly handle concurrent operations.

Examples:

```text
Two cashiers accepting the last item
Two users opening a session
Two users modifying the same order
Two users changing configuration
Two devices syncing the same transaction
Two users applying corrections
```

Appropriate techniques include:

* database transactions;
* row-level locking;
* optimistic concurrency;
* version numbers;
* unique constraints;
* state transition validation.

Concurrency strategy must be selected according to the operation.

---

# 23. Order and Inventory Transaction

Order acceptance is one of the most important backend transactions.

Conceptually:

```text
AcceptOrder
    ↓
Validate Order
    ↓
Validate Permission
    ↓
Validate Subscription
    ↓
Validate Current Configuration
    ↓
Validate Stock
    ↓
Lock Relevant Inventory
    ↓
Deduct Inventory
    ↓
Change Order → Accepted
    ↓
Create Kitchen Event
    ↓
Commit
```

If stock validation or deduction fails:

```text
No Inventory Deduction
No Accepted State
No Successful Acceptance
```

The kitchen notification is secondary to the core transaction.

---

# 24. Order Modification

Accepted order modification must preserve atomicity.

Example:

```text
Modify Order
    ↓
Validate Permission
    ↓
Load Current Order
    ↓
Validate Modification
    ↓
Validate Inventory
    ↓
Apply Inventory Change
    ↓
Apply Order Change
    ↓
Audit Modification
    ↓
Commit
```

If the inventory operation fails, the complete modification must roll back.

---

# 25. Payment Architecture

Payment operations must be isolated from order operational lifecycle.

The backend must distinguish:

```text
Order State
Payment State
Cash Session State
Refund State
```

Payment completion must not automatically mark an order as Served or Ready.

Payment operations must validate:

* Business;
* Branch;
* Employee;
* Device;
* Cash Session where applicable;
* permission;
* order paymentability;
* remaining amount;
* payment method.

---

# 26. Cash Architecture

Cash operations belong to the Cash module.

The backend must preserve:

```text
Cash Register
    ↓
Cash Session
    ↓
Cash Operations
```

A physical cash register is currently one per Branch.

The architecture must not prevent future support for multiple registers.

Cash Session identity is independent from physical register identity.

---

# 27. Cash Session Concurrency

Only one active Cash Session may exist for the same operational register context unless future configuration explicitly permits otherwise.

Opening must be protected by transactional concurrency control.

Example:

```text
Request A ──┐
            ├── Database Constraint / Transaction
Request B ──┘
                 ↓
          First Successful Request
                 ↓
             Session Open
```

The second conflicting request must be rejected.

---

# 28. Cash Session Handover

Handover is not implemented as reopening the previous session.

The backend flow is:

```text
Previous Cashier
      ↓
Close Previous Cash Session
      ↓
New Cashier Authentication
      ↓
Physical Cash Count
      ↓
Accept Opening Cash
      ↓
Open New Cash Session
```

The previous session remains permanently historical.

The physical register remains the same.

The new session receives a new UUID.

---

# 29. Inventory Architecture

Inventory owns stock state and stock transactions.

Core concepts include:

```text
Product
Stock
Warehouse
Inventory Transaction
Purchase
Adjustment
Recipe Consumption
Production
Discrepancy
```

Inventory must prevent negative stock.

Inventory operations must be atomic where required.

---

# 30. Inventory Concurrency

For online transactions:

```text
Read Stock
   ↓
Lock Relevant Stock
   ↓
Validate Quantity
   ↓
Deduct
   ↓
Commit
```

Only one transaction may successfully consume the final available quantity.

For offline operations:

```text
Local Validation
      ↓
Offline Transaction
      ↓
Synchronization
      ↓
Server Validation
      ↓
Accepted / Conflict
```

Offline local success does not bypass server validation.

---

# 31. Recipe Processing

Recipe calculation belongs to the Inventory/Product/Recipe domain boundary.

The backend must support:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

Recipe changes must be versioned.

Approved recipe changes become effective according to the configuration boundary rules.

Historical transactions must retain the relevant recipe/configuration snapshot.

---

# 32. Menu and Pricing Backend

Menu and Pricing operations are configuration-oriented.

The backend must support:

* global products;
* branch availability;
* global prices;
* branch overrides;
* categories;
* Sets;
* recipe references;
* product activation;
* price history;
* effective dates/session boundaries.

Price changes must not silently rewrite historical orders.

Open orders retain their valid price snapshots.

---

# 33. Configuration Activation

Configuration changes must follow controlled versioning.

Conceptually:

```text
Draft
  ↓
Pending Approval
  ↓
Approved
  ↓
Active
```

Depending on configuration type, activation may occur:

* immediately;
* at the next Cash Session;
* at a configured effective time.

The activation rule belongs to the configuration type.

---

# 34. Authorization Pipeline

Important state-changing operations should pass through a consistent authorization pipeline.

Conceptually:

```text
Authentication
      ↓
Business Membership
      ↓
Branch Scope
      ↓
Employee Status
      ↓
Role Permission
      ↓
Employee Override
      ↓
Subscription Entitlement
      ↓
Device Trust
      ↓
Operation Authorization
```

Not every operation requires all checks.

The backend must not rely on frontend visibility as authorization.

---

# 35. Permission Evaluation

Effective permission is conceptually:

```text
Effective Permission
=
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

The backend remains authoritative.

A permission hidden from the frontend must still be denied server-side.

---

# 36. Subscription Enforcement

Subscription enforcement belongs to the backend.

The backend must evaluate:

* subscription state;
* expiry time;
* grace period;
* enabled features;
* branch limits;
* employee limits;
* Owner limits;
* other configured tariff limits.

After expiry:

```text
Read Operations
    ↓
Allowed according to policy

Modify Operations
    ↓
Blocked
```

Frontend restrictions are only usability controls.

They are not security controls.

---

# 37. Offline Backend Support

Offline operations are treated as delayed server operations.

The backend must:

1. receive synchronization requests;
2. authenticate the device;
3. validate Business and Branch;
4. validate Employee;
5. validate device trust;
6. validate offline authorization;
7. validate subscription bounds;
8. validate operation UUID;
9. validate dependencies;
10. validate current server state;
11. execute or reject;
12. create conflict when required;
13. return deterministic synchronization result.

---

# 38. Synchronization Endpoint

Synchronization should use explicit batch processing.

Conceptually:

```text
Device
  ↓
Sync Batch
  ↓
Authenticate Device
  ↓
Validate Batch
  ↓
Process Events
  ↓
Return Results
```

A batch may contain multiple operations.

One failed operation must not necessarily invalidate successfully processed independent operations.

---

# 39. Synchronization Ordering

Operations must respect dependencies.

Example:

```text
Create Order
    ↓
Accept Order
    ↓
Payment
```

The backend must not process Payment before the required Order state exists.

Dependency information must be explicit.

---

# 40. Conflict Handling

The backend must never silently overwrite conflicting business state.

A conflict should contain:

```text
Conflict UUID
Business UUID
Branch UUID
Transaction UUID
Entity UUID
Conflict Type
Local State
Server State
Detected At
Status
Resolution
Resolved By
Resolution Reason
Resolved At
```

Conflict resolution is an authorized business operation.

---

# 41. Conflict Resolution

Conceptually:

```text
Conflict Detected
      ↓
Conflict Record
      ↓
Authorized Review
      ↓
Resolution Decision
      ↓
Apply Resolution
      ↓
Audit
      ↓
Resolved
```

The original conflicting information must remain available for historical reconstruction.

---

# 42. Reporting Backend

Reporting must be separated from core transactional execution.

Reports may use:

* transactional data;
* optimized read models;
* report snapshots;
* report versions.

Heavy report generation must execute asynchronously.

POS operations must not wait for large report generation.

---

# 43. Report Versioning

A report version is immutable.

A new version is created when relevant underlying data changes.

Conceptually:

```text
Report Definition
      +
Period
      +
Scope
      ↓
Report Version
```

A correction that does not change relevant report metrics must not create an unnecessary new report version.

---

# 44. Excel Export

Excel export is a backend responsibility.

The export must represent an exact report snapshot/version.

For large exports:

```text
Export Request
    ↓
Background Job
    ↓
Generate XLSX
    ↓
Store File
    ↓
Notify User
```

Export access must follow the same Business, Branch, Permission, and Subscription boundaries.

---

# 45. Notification Backend

Notifications are secondary processing.

A core transaction must not fail because notification delivery fails.

Example:

```text
Cash Session Closed
      ↓
Transaction Commit
      ↓
Notification Event
      ↓
Notification Processor
      ↓
Owner Notification
```

Notification processing may retry independently.

---

# 46. Audit Backend

Audit information must preserve important business history.

Important operations include:

* payments;
* refunds;
* inventory adjustments;
* cash corrections;
* permission changes;
* employee status changes;
* configuration changes;
* subscription changes;
* synchronization conflicts;
* deletion lifecycle events.

Audit records must be immutable.

---

# 47. Historical Snapshots

The backend must preserve snapshots when historical meaning depends on mutable configuration.

Examples:

```text
Order Price Snapshot
Recipe Snapshot
Configuration Version
Employee Permission State
Payment Information
Report Version
```

Historical records must not depend only on current mutable configuration.

---

# 48. Background Processing

Background jobs should handle work that does not need to block the primary user operation.

Examples:

* report generation;
* Excel export;
* notification delivery;
* outbox processing;
* synchronization retry;
* cleanup;
* subscription lifecycle;
* deletion processing;
* scheduled monthly reports.

Background jobs must be:

* retryable;
* idempotent;
* observable;
* bounded;
* auditable where required.

---

# 49. Job Retry Policy

A failed job should not retry indefinitely.

Conceptually:

```text
Pending
  ↓
Running
  ↓
Success

or

Running
  ↓
Retrying
  ↓
Retry Limit
  ↓
Failed
```

Permanent failures must be visible to operators.

Retry behavior must distinguish transient and permanent errors.

---

# 50. Error Classification

Backend errors should be classified.

Examples:

```text
Validation Error
Authorization Error
Authentication Error
Not Found
Conflict
Concurrency Error
Business Rule Violation
Subscription Restriction
Device Trust Error
Synchronization Conflict
Infrastructure Failure
```

The API layer maps these to stable API responses.

Internal implementation details must not be leaked to clients.

---

# 51. Error Handling Principle

Errors must be deterministic and actionable.

Example:

```text
Stock Insufficient
```

should provide enough information for the frontend to explain that the operation cannot be completed.

But internal database information such as:

```text
PostgreSQL constraint violation on table xyz
```

must not be exposed directly.

---

# 52. Database Access

All database access must be performed through controlled infrastructure.

Application/domain code must not construct raw database connections.

The database layer is responsible for:

* connection management;
* transaction management;
* query execution;
* locking;
* persistence;
* migrations;
* constraints;
* indexes.

Database-specific optimizations must not leak unnecessarily into the domain layer.

---

# 53. Database Constraints

Important business invariants should be protected at the database level where practical.

Examples:

* unique UUIDs;
* unique active cash session constraints;
* tenant ownership;
* valid foreign-key relationships;
* non-negative stock where enforceable;
* unique configuration versions;
* idempotency records.

Application validation remains necessary.

Database constraints provide a second protection layer.

---

# 54. Tenant Isolation

Every tenant-scoped operation must include Business context.

The backend must prevent:

```text
Business A
    ↓
Access Business B Data
```

This applies to:

* API requests;
* reports;
* exports;
* background jobs;
* synchronization;
* notifications;
* audit;
* cache;
* files.

Business UUID must be part of the relevant authorization and data-access context.

---

# 55. Branch Isolation

Branch-scoped operations must validate Branch membership and permission.

Example:

```text
Employee
   ↓
Business
   ↓
Authorized Branches
   ↓
Requested Branch
```

A user authorized for Branch A must not automatically access Branch B.

Multi-branch employees may have different permissions per branch.

---

# 56. Cache Architecture

Caching may be used for read-heavy and relatively stable data.

Suitable candidates include:

* menu configuration;
* product information;
* branch configuration;
* permission metadata;
* subscription entitlement snapshots.

Transactional state such as:

* stock;
* cash;
* payment;
* order state

must not rely on stale cache for authoritative decisions.

The database remains authoritative.

---

# 57. Cache Invalidation

Configuration changes must invalidate relevant cached data.

Example:

```text
Price Configuration Changed
      ↓
Commit
      ↓
Invalidate Relevant Cache
      ↓
New Reads Use New Version
```

Cache invalidation must not modify historical snapshots.

---

# 58. File Storage

Files such as generated Excel exports should be stored outside the transactional database where appropriate.

File metadata should include:

```text
File UUID
Business UUID
Report UUID
Report Version UUID
Created By
Created At
Expiration
Access Scope
```

Access must be authorized server-side.

---

# 59. Security Architecture

Backend security includes:

* secure authentication;
* authorization;
* tenant isolation;
* branch isolation;
* device trust;
* encrypted offline data;
* signed offline authorization;
* replay protection;
* clock rollback detection;
* secure secrets;
* rate limiting;
* input validation;
* audit logging;
* secure file access.

Security mechanisms must be centralized where possible.

---

# 60. Authentication

Authentication identifies the employee.

Authorization determines whether the employee may perform the operation.

These concepts must remain separate.

Example:

```text
Authenticated Employee
        ≠
Authorized Employee
```

A valid login does not automatically grant access to business operations.

---

# 61. Device Trust

Device trust is an independent security layer.

A trusted device:

* may participate in offline operations;
* has a Business/Branch scope;
* may be associated with employees;
* can be revoked;
* has its own Device UUID.

Device trust must never replace permission evaluation.

---

# 62. Secrets and Credentials

Sensitive credentials must not be stored in application source code.

Secrets should be supplied through secure configuration mechanisms.

Examples:

```text
Database Credentials
Signing Keys
Encryption Keys
API Secrets
Session Secrets
```

Secret rotation must be possible without changing business logic.

---

# 63. Logging

Backend logs should support troubleshooting without exposing sensitive information.

Logs should include where appropriate:

```text
Timestamp
Level
Correlation ID
Business UUID
Branch UUID
Employee UUID
Device UUID
Operation
Result
Duration
Error Category
```

Sensitive credentials and protected personal data must not be logged unnecessarily.

---

# 64. Correlation IDs

Every API request should have a correlation ID.

The correlation ID connects:

```text
API Request
    ↓
Application Use Case
    ↓
Database Operation
    ↓
Background Job
    ↓
Event
    ↓
Notification / Audit
```

Correlation ID is operational metadata.

It is not the business transaction UUID.

---

# 65. Transaction UUID vs Correlation ID

These identifiers serve different purposes.

### Transaction UUID

Identifies a business operation.

Examples:

```text
Order Transaction
Payment Transaction
Sync Transaction
Inventory Transaction
```

### Correlation ID

Identifies a technical request or execution chain.

Therefore:

```text
Transaction UUID ≠ Correlation ID
```

Both may exist in the same operation.

---

# 66. Metrics

The backend should expose metrics for:

* request latency;
* request rate;
* error rate;
* database latency;
* transaction duration;
* background job duration;
* synchronization throughput;
* synchronization conflicts;
* report generation time;
* notification failures;
* cache performance;
* queue depth.

Metrics must support operational diagnosis without affecting business correctness.

---

# 67. Health Checks

The backend should expose appropriate health information.

Conceptually:

```text
Liveness
Readiness
Dependency Health
```

Health checks should distinguish:

```text
Application Process Healthy
```

from:

```text
Application Ready to Serve Traffic
```

A temporary optional dependency failure should not necessarily make the entire application unavailable.

---

# 68. API Versioning

API contracts must be versionable.

Breaking API changes must not silently invalidate supported clients.

Possible structure:

```text
/api/v1/...
```

Future versions may coexist where required.

Internal domain changes should not automatically require API changes.

---

# 69. Request Validation

Every external request must be validated before entering business logic.

Validation includes:

* type;
* required fields;
* length;
* ranges;
* enum values;
* UUID format;
* date format;
* numeric constraints;
* payload size.

Business validation remains in the Application/Domain layers.

---

# 70. Pagination

Large collections must not be returned without limits.

Pagination is required for:

* orders;
* payments;
* inventory movements;
* audit events;
* notifications;
* employees;
* reports;
* synchronization records.

Pagination should use stable ordering.

---

# 71. Query Performance

The backend should optimize read-heavy operations without compromising domain integrity.

Common techniques include:

* proper indexes;
* projection queries;
* read models;
* pagination;
* selective joins;
* caching;
* background generation;
* query profiling.

Premature optimization must be avoided.

---

# 72. N+1 Prevention

Application queries should avoid uncontrolled repeated database access.

For large lists:

```text
One inefficient query per item
```

must be avoided.

Use:

* joins;
* batch queries;
* projections;
* preloading where appropriate.

---

# 73. Module Dependency Rules

Backend modules must follow the ownership defined by:

`docs/04_Architecture/03_Domain_Module_Architecture.md`

Rules:

1. One module owns each authoritative state.
2. Other modules cannot directly mutate that state.
3. Cross-module behavior uses explicit contracts.
4. Shared database access must not become hidden coupling.
5. Shared utilities must not contain business rules.

---

# 74. Cross-Module Example

Payment and Cash are separate modules.

The Payment module determines:

```text
Payment Completed
```

The Cash module determines:

```text
Cash Session Impact
```

The integration should use an explicit application/domain contract.

Neither module should directly modify the other's internal tables.

---

# 75. Order and Kitchen Integration

Order owns operational order state.

Kitchen owns kitchen execution state.

The relationship is:

```text
Order Accepted
      ↓
Kitchen Event
      ↓
Kitchen Ticket
      ↓
Preparation Status
```

Kitchen processing must not directly modify Order persistence.

Order state changes must go through the Order application boundary.

---

# 76. Reporting Integration

Reporting should consume authoritative data.

It should not become a second source of truth.

```text
Transactional Modules
        ↓
Reporting Read Model / Snapshot
        ↓
Reports
```

Report calculations must be reproducible from the defined source state.

---

# 77. Notification Integration

Notifications consume business events.

They should not be embedded deeply into transactional business logic.

Bad:

```text
CloseCashSession()
    ↓
SendNotification()
    ↓
External Failure
    ↓
Rollback Cash Session
```

Preferred:

```text
CloseCashSession
    ↓
Commit
    ↓
CashSessionClosed
    ↓
Notification Handler
```

---

# 78. Audit Integration

Important state changes must produce audit information.

Audit persistence must be reliable.

For critical operations, audit creation should participate in the transaction or use a reliable outbox-style mechanism.

The backend must never allow a successful privileged correction to disappear from history.

---

# 79. Data Lifecycle Integration

Data lifecycle operations must be isolated from normal operational requests.

Deletion is a controlled background process.

Conceptually:

```text
Business Eligible for Deletion
        ↓
Lifecycle Lock
        ↓
Validate No Reactivation
        ↓
Delete Dependencies
        ↓
Delete Business Data
        ↓
Invalidate Devices
        ↓
Mark Deleted
```

Normal operational endpoints must reject deleted businesses.

---

# 80. Graceful Failure

The backend should degrade gracefully where possible.

Examples:

```text
Notification Service Down
    → Core Transaction Continues

Report Worker Down
    → Report Request Queued

Sync Network Failure
    → Local Queue Retained

Cache Failure
    → Read From Authoritative Store

Printer Failure
    → ERP Transaction Remains Valid
```

Critical transactional dependencies cannot be bypassed when correctness requires them.

---

# 81. Database Failure

If the transactional database is unavailable:

* state-changing operations must fail safely;
* partial business transactions must not be accepted;
* API should return a controlled infrastructure error;
* retry should be handled carefully;
* clients must not assume success unless confirmed.

Offline-capable devices may continue eligible offline operations.

---

# 82. Application Restart

The backend must be stateless where possible.

A process restart must not lose:

* committed business transactions;
* pending outbox events;
* synchronization queue state;
* background job state;
* report versions;
* audit records.

Durable state belongs in persistent storage.

---

# 83. Worker Restart

Background workers may restart at any point.

Jobs must therefore be:

* idempotent;
* retryable;
* resumable where necessary.

A worker crash must not create duplicate:

* notifications;
* report versions;
* synchronization effects;
* deletion effects.

---

# 84. API Request Retry

Clients may retry requests because of network failures.

The backend must distinguish:

```text
Request Failed Before Processing
```

from:

```text
Request Processed But Response Lost
```

Idempotency prevents duplicate business effects.

This is especially important for:

* payments;
* orders;
* inventory;
* cash operations;
* offline synchronization.

---

# 85. Deployment Model

The initial backend may be deployed as a modular monolith.

Conceptually:

```text
                 Reverse Proxy
                       ↓
                 Backend Application
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    Database         Cache        Background Worker
```

The exact infrastructure may evolve.

The application must not assume that every module is deployed independently.

---

# 86. Modular Monolith Principle

A modular monolith is the preferred initial backend deployment model.

This provides:

* simple deployment;
* strong transactional consistency;
* lower operational complexity;
* easier debugging;
* lower infrastructure requirements;
* clear module boundaries;
* future extraction capability.

Module boundaries must be enforced in code even though modules share a deployment.

---

# 87. Future Service Extraction

A module may later become an independent service if scale or organizational requirements justify it.

Potential extraction candidates include:

* Reporting;
* Notification;
* Synchronization;
* Data Lifecycle;
* heavy background processing.

Extraction must not be required for the initial architecture.

The current design must preserve explicit contracts so future extraction remains possible.

---

# 88. Dependency Injection

Infrastructure dependencies should be injected rather than constructed inside business logic.

Examples:

```text
Clock
Repository
Transaction Manager
Event Publisher
Cache
File Storage
Encryption Service
Authorization Service
```

This improves:

* testing;
* replacement;
* configuration;
* maintainability.

---

# 89. Clock Abstraction

Business logic involving time should use an abstract clock.

Examples:

* subscription expiry;
* offline authorization;
* cash sessions;
* payroll periods;
* report periods;
* configuration effective times;
* data deletion countdown.

This makes time-dependent logic testable.

Server time remains authoritative for online operations.

---

# 90. Testing Architecture

The backend must support multiple testing levels.

### Unit Tests

Test:

* domain rules;
* value objects;
* permission logic;
* calculations;
* state transitions.

### Application Tests

Test:

* use cases;
* authorization;
* transaction behavior;
* idempotency;
* event creation.

### Integration Tests

Test:

* database;
* repositories;
* transactions;
* locking;
* synchronization.

### API Tests

Test:

* authentication;
* authorization;
* request validation;
* response contracts.

### End-to-End Tests

Test critical user workflows.

---

# 91. Critical Backend Test Scenarios

The following scenarios require strong automated coverage:

```text
Order Acceptance + Inventory Deduction
Payment + Remaining Amount
Cash Session Open Concurrency
Cash Session Close
Cash Handover
Inventory Last-Unit Concurrency
Refund
Debt Repayment
Recipe Approval
Price Activation
Permission Change
Subscription Expiry
Offline Synchronization
Duplicate Sync Request
Sync Conflict
Report Version Creation
Data Deletion
```

---

# 92. Migration Architecture

Database schema changes must be managed through versioned migrations.

Migrations should be:

* ordered;
* repeatable in controlled environments;
* reviewable;
* tested;
* reversible where practical.

Destructive migrations require special review because historical data is important.

---

# 93. Seed Data

System-required reference data should be managed separately from tenant-owned data.

Examples:

```text
System Permission Definitions
System Role Templates
System Configuration Defaults
```

Tenant configuration must not accidentally be overwritten by application startup.

---

# 94. Configuration Management

Runtime configuration should distinguish:

```text
Application Configuration
Environment Configuration
Business Configuration
Branch Configuration
User Permission Configuration
Subscription Configuration
```

Business behavior must not depend on hard-coded tenant-specific values.

---

# 95. Feature Flags

Feature flags may be used for controlled technical rollout.

They must not replace:

* subscription entitlement;
* authorization;
* business configuration.

For example:

```text
Feature Flag
    = Technical Availability

Subscription Entitlement
    = Business Authorization
```

These concepts remain separate.

---

# 96. Performance Principles

Backend performance priorities are:

1. POS responsiveness;
2. transaction reliability;
3. database efficiency;
4. synchronization throughput;
5. report isolation;
6. background processing.

The backend must avoid unnecessary processing in the critical POS path.

---

# 97. Critical Path

The critical POS path should remain short.

Example:

```text
Authenticate
→ Authorize
→ Validate
→ Transaction
→ Commit
→ Respond
```

Secondary operations should move outside the critical path when safe.

Examples:

* notifications;
* heavy reports;
* Excel generation;
* analytics;
* non-critical synchronization processing.

---

# 98. Performance vs Security

Security must not be disabled for performance.

Instead:

* cache safe authorization metadata;
* use efficient indexes;
* minimize unnecessary database calls;
* use short transactional scopes;
* avoid repeated expensive calculations;
* use local trusted-device validation where appropriate;
* keep heavy processing asynchronous.

Security and performance must be designed together.

---

# 99. Backend Anti-Patterns

The following patterns are prohibited:

### Direct Database Writes from API

```text
Controller → Database
```

### Cross-Module Table Mutation

```text
Order Module → Direct Payment Table Update
```

### Business Logic in Controllers

```text
Controller contains inventory/cash/payment rules
```

### Frontend Authorization

```text
Hidden Button = Security
```

### Silent Conflict Resolution

```text
Server State Overwrites Offline State
```

### Unbounded Background Retry

```text
Retry Forever
```

### Mutable Historical Records

```text
Update Original Payment
```

### Notification-Coupled Transactions

```text
Notification Failure → Business Transaction Rollback
```

### Report-Coupled POS

```text
POS Waits for Heavy Report
```

### Global Shared Cache as Source of Truth

```text
Cache = Authoritative State
```

---

# 100. Backend Request Lifecycle

A standard authenticated state-changing request follows:

```text
Client
  ↓
Reverse Proxy
  ↓
API Endpoint
  ↓
Authentication
  ↓
Execution Context
  ↓
Authorization
  ↓
Subscription Check
  ↓
Device Trust Check
  ↓
Application Use Case
  ↓
Domain Operation
  ↓
Repository / Transaction
  ↓
Database Commit
  ↓
Outbox / Events
  ↓
Response
```

Not every endpoint requires every security step.

The Application Layer determines the exact policy.

---

# 101. Backend Read Lifecycle

A standard read request follows:

```text
Client
  ↓
API Endpoint
  ↓
Authentication
  ↓
Scope Validation
  ↓
Permission Check
  ↓
Query Handler
  ↓
Read Model / Repository
  ↓
Database / Cache
  ↓
Response
```

Read operations must still enforce Business and Branch isolation.

---

# 102. Backend State Ownership

The following ownership must remain explicit:

| State          | Owner                       |
| -------------- | --------------------------- |
| Business       | Business Module             |
| Employee       | Identity / Employee Module  |
| Permission     | Identity and Access Module  |
| Subscription   | Subscription Module         |
| Branch         | Branch Module               |
| Order          | Order Module                |
| Cash Session   | Cash Module                 |
| Stock          | Inventory Module            |
| Payment        | Payment Module              |
| Menu           | Menu and Pricing Module     |
| Recipe         | Inventory / Recipe Module   |
| Kitchen Ticket | Kitchen Module              |
| Payroll        | Employee and Payroll Module |
| Report Version | Reporting Module            |
| Notification   | Notification Module         |
| Audit Event    | Audit Module                |
| Sync State     | Synchronization Module      |
| Lifecycle      | Data Lifecycle Module       |
| Configuration  | Configuration Module        |
| Device Trust   | Device and Trust Module     |

---

# 103. Backend Boundary Rule

When another module needs information, it should prefer:

```text
Explicit Contract
```

rather than:

```text
Direct Internal Table Access
```

This preserves module independence.

---

# 104. Backend Architecture Completion Criteria

This architecture is considered complete when:

* API does not contain domain logic;
* application use cases own orchestration;
* domain owns business rules;
* infrastructure owns technical implementation;
* each module has clear state ownership;
* tenant isolation is enforced;
* branch isolation is enforced;
* authorization is server-side;
* subscription enforcement is server-side;
* offline synchronization is explicit;
* idempotency is implemented;
* critical transactions are atomic;
* historical data is preserved;
* reports are isolated from POS critical paths;
* background jobs are retryable;
* events are reliably persisted;
* errors are classified;
* observability exists;
* automated tests cover critical flows;
* deployment can operate as a modular monolith.

---

# 105. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`

---

# 106. Next Architecture Document

The next architecture document is:

`docs/04_Architecture/05_Frontend_Architecture.md`

It will define:

* frontend application structure;
* page/module boundaries;
* role-aware navigation;
* permission-aware UI;
* branch switching;
* POS frontend architecture;
* offline UI behavior;
* local state;
* synchronization UI;
* API client structure;
* frontend security boundaries;
* caching;
* performance;
* error handling;
* frontend/backend contract boundaries.

