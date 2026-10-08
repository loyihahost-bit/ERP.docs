# Application Layer Architecture

**Document ID:** ARCH-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/01_System_Architecture.md`

---

## 1. Purpose

This document defines the Application Layer architecture of FastFood ERP.

The Application Layer is responsible for coordinating system use cases between the API/presentation layer, domain modules, and infrastructure.

It defines:

* application services;
* commands;
* queries;
* use-case boundaries;
* transaction orchestration;
* authorization context;
* domain interaction;
* event handling;
* idempotency;
* error propagation;
* background job initiation;
* read and write flows;
* application-level validation;
* cross-domain orchestration.

The Application Layer must coordinate business operations without becoming the owner of business rules that belong to the Domain Layer.

---

# 2. Position in the Architecture

The logical architecture is:

```text id="e5p1q4"
Presentation / API
        ↓
Application Layer
        ↓
Domain Layer
        ↓
Infrastructure
        ↓
Database / External Systems
```

The Application Layer is therefore the orchestration boundary.

It coordinates:

```text
Request
  ↓
Context
  ↓
Authorization
  ↓
Use Case
  ↓
Domain Operations
  ↓
Persistence
  ↓
Events / Background Work
  ↓
Response
```

---

# 3. Primary Responsibilities

The Application Layer is responsible for:

1. Executing use cases.
2. Coordinating domain modules.
3. Establishing application execution context.
4. Starting and controlling transactions.
5. Calling authorization services.
6. Calling repositories or data-access abstractions.
7. Handling idempotency.
8. Coordinating domain events.
9. Creating background jobs.
10. Coordinating cross-domain workflows.
11. Mapping domain results to application results.
12. Coordinating consistency boundaries.
13. Handling application-level validation.
14. Providing stable use-case contracts for API and other adapters.

---

# 4. Responsibilities It Does Not Own

The Application Layer must not become the owner of:

* HTTP-specific behavior;
* frontend state;
* database schema definitions;
* SQL-specific business logic;
* low-level infrastructure implementation;
* domain invariants;
* UI presentation rules;
* printer-specific protocol logic;
* raw authentication protocol implementation.

For example:

```text id="w8sp4n"
Application Layer
    ↓
"Can this order be accepted?"
```

may coordinate the operation.

But the actual invariant:

```text id="h5kw7v"
"An order cannot be accepted when required inventory is unavailable."
```

belongs to the Domain/transactional business logic.

---

# 5. Application Module Structure

The Application Layer should follow business capabilities.

Conceptually:

```text id="s0c3pp"
application/
├── business/
├── identity/
├── subscription/
├── branch/
├── employee/
├── device/
├── order/
├── cash/
├── inventory/
├── product/
├── recipe/
├── menu/
├── pricing/
├── kitchen/
├── payment/
├── debt/
├── refund/
├── payroll/
├── reporting/
├── notification/
├── audit/
├── synchronization/
├── configuration/
└── data_lifecycle/
```

Exact package naming may be adjusted during backend implementation, but responsibility boundaries must remain.

---

# 6. Use Case Architecture

A use case represents one meaningful application operation.

Examples:

```text id="zvcl4e"
CreateOrder
AcceptOrder
ModifyOrder
CancelOrder

CreatePayment
CreateRefund
RecordDebtRepayment

OpenCashSession
CloseCashSession
PerformCashHandover
CreateCashCorrection

CreateInventoryAdjustment
RecordPurchase
ProduceSemiFinishedProduct

CreateRecipe
ApproveRecipe
ChangePrice
ActivateProduct

GenerateReport
CreateReportVersion
ExportReport

SynchronizeOfflineEvents
ResolveSynchronizationConflict

RegisterDevice
RevokeDevice

ExpireSubscription
ReactivateSubscription

StartBusinessDeletion
ProcessBusinessDeletion
```

A use case should represent a business operation rather than a database CRUD operation.

---

# 7. Command Model

Commands represent operations that change system state.

Examples:

```text id="pwm8ji"
AcceptOrderCommand
CreatePaymentCommand
CloseCashSessionCommand
CreateRefundCommand
AdjustInventoryCommand
ApproveRecipeCommand
ChangePriceCommand
ResolveConflictCommand
```

A command should contain the minimum information required to execute the operation.

Example conceptual structure:

```text id="0hmbkp"
AcceptOrderCommand
├── BusinessId
├── BranchId
├── OrderId
├── EmployeeId
├── DeviceId
├── CashSessionId
└── IdempotencyKey / Transaction UUID
```

The exact transport representation is defined by the API layer.

---

# 8. Query Model

Queries retrieve information without intentionally changing business state.

Examples:

```text id="z2m8ry"
GetOrder
ListOrders
GetTableState
GetCashSession
GetInventory
GetProduct
GetMenu
GetEmployee
GetPayroll
GetReport
GetAuditHistory
GetNotifications
GetSynchronizationStatus
```

Queries should be optimized independently from command processing where necessary.

A query must still enforce:

* Business scope;
* Branch scope;
* permission;
* subscription/read-only rules where applicable.

---

# 9. Command and Query Separation

The architecture should distinguish command and query responsibilities.

```text id="p5vxxe"
                 Application Layer
                       │
              ┌────────┴────────┐
              │                 │
           Commands           Queries
              │                 │
              ▼                 ▼
        Domain / Write     Read Models
        Transaction Path   / Query Services
```

This is a logical separation.

It does not require a full CQRS infrastructure.

---

# 10. Application Execution Context

Each use case receives an execution context.

Conceptually:

```text id="y7d8i4"
ApplicationContext
├── Actor
├── Business
├── Branch
├── Device
├── Cash Session
├── Subscription
├── Permissions
├── Request / Transaction UUID
├── Execution Source
└── Time Context
```

Not every use case requires every field.

For example:

* Super Admin platform operation may not require Branch;
* report query may not require Cash Session;
* inventory adjustment may not require Cash Session;
* cash payment requires Cash Session.

The application layer determines which context is required.

---

# 11. Actor Context

Every state-changing operation must have an explicit actor where applicable.

Actor may be:

```text id="4f9p0n"
Employee
```

or:

```text id="q4u9md"
SYSTEM
```

System-generated operations must not be represented as an arbitrary employee.

Examples:

* monthly report generation → SYSTEM;
* subscription expiry job → SYSTEM;
* deletion job → SYSTEM;
* notification retry → SYSTEM.

---

# 12. Business Context Resolution

Before executing a Business-scoped use case, the Application Layer must establish Business context.

Example:

```text id="7b3w4f"
Authenticated Employee
        ↓
Business Membership
        ↓
Business Context
        ↓
Use Case
```

The Business ID must never be trusted solely from arbitrary client input.

The system must validate that the actor is authorized to operate within the specified Business.

---

# 13. Branch Context Resolution

For Branch-scoped operations:

```text id="g9y5qh"
Actor
  ↓
Business
  ↓
Requested Branch
  ↓
Employee Branch Scope
  ↓
Permission
  ↓
Use Case
```

If the actor does not have access to the Branch, the use case must fail before changing state.

---

# 14. Authorization Flow

The Application Layer coordinates authorization.

Conceptually:

```text id="t4o3s6"
Request
  ↓
Authentication
  ↓
Actor Resolution
  ↓
Business Scope
  ↓
Branch Scope
  ↓
Role Permission
  ↓
Employee Override
  ↓
Subscription Entitlement
  ↓
Device Trust
  ↓
Operation Allowed
```

The Application Layer may call dedicated authorization/domain services.

Authorization logic must not be duplicated independently inside every controller.

---

# 15. Permission Evaluation

Effective permission is conceptually:

```text id="z1f7br"
Effective Permission =
    Role Permission
    + Employee Override
    + Branch Scope
    + Subscription Entitlement
```

The exact precedence and resolution rules are defined by the Identity, Access, Subscription, and Configuration domains.

Application services consume the resulting authorization decision.

---

# 16. Subscription Validation

Every modifying use case that is subscription-controlled must verify entitlement.

Example:

```text id="9ksq0k"
Create Employee
       ↓
Permission Check
       ↓
Subscription Employee Limit
       ↓
Allowed / Rejected
```

Subscription validation must occur server-side.

Frontend visibility is not sufficient.

Read-only operations may remain available after subscription expiry according to the defined lifecycle policy.

---

# 17. Device Validation

Device-sensitive operations must validate the Device context.

For offline operations:

```text id="c8m4ww"
Device
  ↓
Trusted?
  ↓
Business Scope Valid?
  ↓
Branch Scope Valid?
  ↓
Offline Authorization Valid?
  ↓
Employee Authorized?
  ↓
Use Case
```

A trusted device must not automatically grant employee permissions.

---

# 18. Transaction Boundary

The Application Layer determines the transaction boundary for a use case.

Example:

```text id="f4c6b8"
AcceptOrder
    │
    ├── Load Order
    ├── Validate Authorization
    ├── Validate Configuration
    ├── Validate Inventory
    ├── Apply Order State
    ├── Deduct Inventory
    ├── Persist Required History
    └── Commit
```

Secondary effects occur after the core transaction.

---

# 19. Unit of Work

A Unit of Work abstraction may be used to coordinate transactional persistence.

Conceptually:

```text id="wq9s2m"
Use Case
   ↓
Unit of Work
   ├── Order Repository
   ├── Inventory Repository
   ├── Audit Repository
   └── Other Required Repositories
   ↓
Commit / Rollback
```

The Unit of Work must not become a global object containing unrelated operations.

It should correspond to a controlled transactional boundary.

---

# 20. Rollback Behavior

If a critical operation fails before commit:

```text id="7z8l2c"
Operation Failure
      ↓
Rollback
      ↓
No Partial Core State
```

Example:

If Order Acceptance deducts inventory but another required part of the transaction fails, the complete transaction must roll back.

The system must not leave:

```text
Accepted Order
+
Missing Inventory Deduction
```

or:

```text
Inventory Deducted
+
Rejected Order
```

unless such state is explicitly defined as part of a recovery workflow.

---

# 21. Cross-Domain Orchestration

Some use cases require multiple domains.

Example:

```text id="p9d3x4"
Accept Order
   │
   ├── Order
   ├── Inventory
   ├── Configuration
   ├── Authorization
   └── Audit
```

The Application Layer coordinates these dependencies.

Domain modules should not create uncontrolled direct dependencies on every other domain.

---

# 22. Domain Ownership

The Application Layer may call multiple domains, but each domain remains responsible for its own state and rules.

For example:

```text id="7r4b8a"
Application Service
       │
       ├── Order Domain
       │      └── Owns Order State
       │
       └── Inventory Domain
              └── Owns Stock State
```

The Application Layer coordinates the operation.

It does not become the owner of either Order or Inventory state.

---

# 23. Order Acceptance Use Case

Conceptual flow:

```text id="4q4g1s"
AcceptOrder
    ↓
Validate Context
    ↓
Validate Permission
    ↓
Validate Subscription
    ↓
Load Order
    ↓
Validate Order State
    ↓
Load Effective Configuration
    ↓
Validate Inventory
    ↓
Deduct Inventory
    ↓
Change Order → Accepted
    ↓
Persist Transaction
    ↓
Commit
    ↓
Publish Secondary Events
```

Secondary events may include:

* kitchen notification;
* print job;
* audit processing;
* application notification.

---

# 24. Order Modification Use Case

For modification of an Accepted unpaid order:

```text id="8f0k1d"
Modify Order
    ↓
Validate Permission
    ↓
Validate Order State
    ↓
Calculate Modification
    ↓
Validate Inventory
    ↓
Apply Inventory Change
    ↓
Apply Order Change
    ↓
Record Inventory Decision
    ↓
Audit
    ↓
Commit
```

If the required inventory operation fails:

```text id="qf8w5n"
Modification
     ↓
Failure
     ↓
Rollback
```

The entire modification must be rejected.

---

# 25. New Product After Acceptance

Adding a new product after an order has already been Accepted creates a new operational order/ticket according to the approved system rules.

The Application Layer must:

1. Validate permission.
2. Validate table/order context.
3. Validate current configuration.
4. Validate inventory.
5. Create the new operational order identity.
6. Deduct required inventory.
7. Persist the relationship to the original context.
8. Commit.
9. Trigger kitchen processing.

The original order UUID must not be silently replaced.

---

# 26. Payment Use Case

Conceptual flow:

```text id="6g8xq5"
Create Payment
    ↓
Validate Actor
    ↓
Validate Branch
    ↓
Validate Permission
    ↓
Validate Order
    ↓
Validate Paymentable State
    ↓
Calculate Remaining Amount
    ↓
Validate Payment Amount
    ↓
Validate Cash Session if Required
    ↓
Create Payment
    ↓
Commit
```

Overpayment must follow the approved financial rules and must be explicitly represented.

---

# 27. Refund Use Case

Refund processing:

```text id="b7y4s3"
Create Refund
    ↓
Validate Permission
    ↓
Validate Order / Payment
    ↓
Validate Refund Type
    ↓
Validate Refund Amount
    ↓
Require Reason
    ↓
Create Refund
    ↓
Update Financial State
    ↓
Audit
    ↓
Commit
    ↓
Trigger Alert if Required
```

Refund must not automatically return inventory.

---

# 28. Cash Session Use Cases

Application services coordinate:

* opening;
* closing;
* correction;
* handover;
* forced closure.

Example:

```text id="w3q1e9"
Close Cash Session
    ↓
Validate Actor
    ↓
Validate Permission
    ↓
Load Session
    ↓
Validate Session State
    ↓
Capture Actual Cash
    ↓
Calculate Difference
    ↓
Persist Closing State
    ↓
Audit
    ↓
Commit
    ↓
Notification if Required
```

The Application Layer must not reopen a closed session.

---

# 29. Shift Handover

Handover crosses:

* Cash;
* Employee;
* Order;
* Payment;
* Device;
* Audit.

Conceptually:

```text id="q3t5w8"
Previous Cashier
       ↓
Close Previous Session
       ↓
Physical Cash Count
       ↓
Record Difference
       ↓
New Cashier Authentication
       ↓
New Cash Session
       ↓
Transfer Operational Context
       ↓
Audit
```

The physical Cash Register identity remains the same.

The Cash Session UUID changes.

---

# 30. Inventory Adjustment

Inventory adjustment requires explicit permission.

Flow:

```text id="9d8f3m"
Inventory Adjustment
       ↓
Permission
       ↓
Branch Context
       ↓
Product / Warehouse
       ↓
Reason
       ↓
Current Stock
       ↓
Adjustment
       ↓
History
       ↓
Audit
       ↓
Commit
```

The Application Layer must not expose unrestricted stock editing.

---

# 31. Recipe Approval

Recipe workflow:

```text id="6q2v7x"
Create / Modify Recipe
        ↓
Validate Permission
        ↓
Validate Recipe
        ↓
Save Draft / Pending Approval
        ↓
Owner Approval
        ↓
Create New Version
        ↓
Activate According to Effective Rule
        ↓
Audit
```

Historical recipe versions remain immutable.

---

# 32. Configuration Change

Configuration operations follow:

```text id="p6s1x8"
Configuration Change
        ↓
Permission
        ↓
Validate New Configuration
        ↓
Validate Version
        ↓
Create New Version
        ↓
Approval if Required
        ↓
Determine Effective Boundary
        ↓
Activate
        ↓
Audit
```

Operational transactions use the configuration version valid for that operation.

---

# 33. Report Generation

Report generation is application orchestration around reporting logic.

```text id="x9n2p6"
Generate Report
      ↓
Validate Scope
      ↓
Validate Permission
      ↓
Validate Date Range
      ↓
Create Consistent Snapshot
      ↓
Calculate Report
      ↓
Create Immutable Version
      ↓
Persist
      ↓
Return / Queue Export
```

Large reports may be processed asynchronously.

---

# 34. Synchronization Use Case

Synchronization is a dedicated application workflow.

```text id="r8m5y2"
Receive Sync Batch
      ↓
Authenticate Device
      ↓
Validate Device Trust
      ↓
Validate Business
      ↓
Validate Branch
      ↓
Validate Employee
      ↓
Validate Permission
      ↓
Validate Subscription
      ↓
Check UUID Idempotency
      ↓
Validate Dependencies
      ↓
Apply Valid Events
      ↓
Create Conflicts
      ↓
Return Sync Result
```

A synchronization failure must not delete the original local event.

---

# 35. Conflict Resolution

Conflict resolution is a separate use case.

```text id="w2c9k4"
Conflict
   ↓
Load Conflict
   ↓
Validate Resolver Permission
   ↓
Review Context
   ↓
Select Resolution
   ↓
Apply Resolution
   ↓
Record Reason
   ↓
Audit
   ↓
Mark Conflict Resolved
```

Conflict resolution must not silently rewrite historical data.

---

# 36. Idempotency

The Application Layer is responsible for enforcing idempotency at the use-case boundary where necessary.

Conceptually:

```text id="m7z1q5"
Transaction UUID
      ↓
Already Processed?
   ┌──┴──┐
  Yes    No
   │      │
Return   Execute
Result   Use Case
```

This is especially important for:

* offline synchronization;
* payment retries;
* background jobs;
* report generation;
* notification delivery;
* printing.

---

# 37. Application-Level Validation

Validation has multiple levels.

### Transport Validation

Examples:

* required fields;
* data types;
* string length;
* format.

Owned by API/presentation adapters.

### Application Validation

Examples:

* required execution context;
* permission;
* subscription;
* Branch scope;
* actor state.

Owned by Application Layer.

### Domain Validation

Examples:

* order state transition;
* stock invariant;
* cash session invariant;
* payment rules.

Owned by Domain Layer.

### Database Validation

Examples:

* unique constraints;
* foreign keys;
* atomic concurrency;
* persistence integrity.

Owned by Database/Infrastructure.

These layers must complement each other rather than duplicate the same responsibility unnecessarily.

---

# 38. Error Handling

Application services should convert low-level failures into meaningful application outcomes.

Conceptually:

```text id="9g5s4w"
Infrastructure Error
      ↓
Application Error Mapping
      ↓
Stable Error Code
      ↓
API Response
```

Examples:

```text
ORDER_NOT_FOUND
ORDER_ALREADY_ACCEPTED
INSUFFICIENT_STOCK
PERMISSION_DENIED
SUBSCRIPTION_EXPIRED
DEVICE_NOT_TRUSTED
CASH_SESSION_ALREADY_OPEN
DUPLICATE_TRANSACTION
SYNC_CONFLICT
INVALID_CONFIGURATION
```

Error codes should remain stable enough for frontend and API consumers.

---

# 39. Domain Exceptions

Domain rules may produce domain-specific failures.

The Application Layer may catch and translate them into application-level results.

Example:

```text id="2s8p7n"
Inventory Domain
    ↓
InsufficientStock
    ↓
Application Layer
    ↓
INSUFFICIENT_STOCK
```

The Application Layer must not reinterpret a business rule in a way that changes its meaning.

---

# 40. Retry Policy

Retries must be applied only to operations that are safe to retry.

Safe retry candidates may include:

* temporary network failures;
* notification delivery;
* printer jobs;
* background report generation;
* synchronization requests;
* external service timeouts.

A financial or inventory operation must never simply be retried without idempotency protection.

---

# 41. Background Job Creation

The Application Layer may create background jobs after a successful core transaction.

Example:

```text id="q7b4m8"
Payment Completed
      ↓
Commit
      ↓
Create Notification Job
      ↓
Worker
      ↓
Deliver Notification
```

The job must reference the originating transaction/entity UUID.

---

# 42. Outbox Pattern

Where reliable event delivery is required, the architecture may use an Outbox-style mechanism.

Conceptually:

```text id="e5w8q2"
Core Transaction
   ├── Business State
   └── Outbox Event
          ↓
       Commit
          ↓
    Background Processor
          ↓
     Secondary Effect
```

This prevents the following failure:

```text
Database committed
+
Event lost
```

The exact implementation is defined in the Event and Message Architecture document.

---

# 43. Application Events

Application events represent completed application-level actions.

Examples:

```text
OrderAccepted
PaymentCompleted
CashSessionClosed
RefundCreated
InventoryAdjusted
RecipeApproved
PriceChanged
SubscriptionExpired
BusinessDeletionStarted
```

Events must contain stable identifiers and enough context for downstream processing.

---

# 44. Domain Events vs Application Events

The architecture distinguishes:

### Domain Event

Represents a meaningful domain state change.

Example:

```text
OrderAccepted
```

### Application Event

Represents a completed application workflow or technical application action.

Example:

```text
LargeReportGenerated
```

The two may be implemented using a common infrastructure mechanism, but their semantic purpose must remain clear.

---

# 45. Query Architecture

Queries may use optimized read models.

Example:

```text id="8r6m3p"
Dashboard Query
      ↓
Query Service
      ↓
Optimized Read Model
      ↓
Response
```

A query model must still respect:

* Business scope;
* Branch scope;
* permissions;
* subscription read-only rules;
* data lifecycle.

---

# 46. Report Query Isolation

Large report queries must not unnecessarily compete with critical POS transactions.

Possible techniques include:

* optimized indexes;
* read replicas where justified;
* precomputed summaries;
* background report generation;
* dedicated read models.

The selected strategy must be based on actual workload requirements.

---

# 47. Caching Interaction

Application services may request cached data for read-heavy configuration.

Example:

```text id="j5q9r4"
Get Active Menu
      ↓
Cache
   ┌──┴──┐
 Hit    Miss
  │      │
Return  Database
         ↓
       Cache
```

Critical mutable state must still be validated against authoritative state when required.

---

# 48. Security Context Propagation

The execution context must remain attached throughout the use case.

For example:

```text id="y3q6m9"
Business ID
Branch ID
Employee ID
Device ID
Transaction UUID
```

must remain available to:

* domain operations where needed;
* audit;
* repositories;
* synchronization;
* background job metadata.

Context must not be lost when control moves between application components.

---

# 49. Audit Integration

The Application Layer coordinates audit recording for important operations.

Example:

```text id="q2w6n8"
Application Command
      ↓
Domain Operation
      ↓
State Change
      ↓
Audit Event
      ↓
Commit
```

Audit records must contain sufficient context to reconstruct the operation later.

---

# 50. Application Logging

Application logs are operational diagnostics.

They are different from audit records.

### Application Logs

Used for:

* debugging;
* errors;
* performance;
* infrastructure diagnosis;
* job execution.

### Audit Records

Used for:

* business history;
* security accountability;
* correction history;
* state-change reconstruction.

Sensitive business data should not be unnecessarily written to operational logs.

---

# 51. Application Time

The Application Layer must avoid trusting client-provided timestamps for authoritative server state.

For online operations:

```text
Server Time
```

is authoritative.

For offline operations:

```text
Device Timestamp
+
Offline Authorization
+
Clock Integrity Checks
+
Synchronization Validation
```

must be used.

The original transaction timestamp remains part of historical context.

---

# 52. System-Generated Operations

System jobs execute with a dedicated SYSTEM actor identity.

Examples:

```text
SYSTEM
├── Subscription Expiration
├── Monthly Report Generation
├── Business Deletion
├── Notification Retry
├── Print Retry
└── Cleanup
```

System actions must remain auditable where required.

---

# 53. Application State Machines

State transitions should be executed through application/domain operations rather than arbitrary field updates.

Examples:

```text
Order:
Draft → Accepted → Preparing → Ready → Served
```

```text
Cash Session:
Open → Closed
```

```text
Business:
Active → Expired/Read-Only → Deletion Eligible → Deleting → Deleted
```

Invalid transitions must be rejected.

---

# 54. Cross-Domain Transaction Rules

The Application Layer must identify whether a workflow requires:

### Strong Consistency

Examples:

* order acceptance + inventory deduction;
* payment creation;
* cash session closure;
* critical inventory adjustment.

### Eventual Consistency

Examples:

* notification;
* printer job;
* heavy report;
* non-critical background processing.

The choice must be explicit for each workflow.

---

# 55. Application Boundary Rules

The following rules apply:

1. Controllers do not contain business workflows.
2. Application services do not contain database-specific SQL.
3. Domain modules own domain rules.
4. Repositories own persistence interaction.
5. Infrastructure owns external technical integrations.
6. Queries must enforce authorization.
7. Commands must validate execution context.
8. Critical operations must have explicit transaction boundaries.
9. Retryable operations must be idempotent.
10. Secondary effects should not block core transactions unnecessarily.

---

# 56. Anti-Patterns

The following patterns are prohibited or strongly discouraged.

### 56.1. Fat Controllers

Controllers must not contain multi-step business workflows.

### 56.2. Fat Application Services

Application services must not become a replacement for the Domain Layer.

### 56.3. Generic CRUD Services

Critical business operations must use explicit use cases.

### 56.4. Direct Cross-Module Database Updates

One module must not directly modify another module's internal tables without an explicit architectural contract.

### 56.5. Authorization Duplication

The same permission logic must not be independently reimplemented across many controllers.

### 56.6. Hidden Side Effects

A use case must clearly define important side effects.

### 56.7. Non-Idempotent Retry

Retried operations must not duplicate payments, stock changes, or financial records.

### 56.8. Client-Trusted Authorization

The client must never be the final authority for authorization.

---

# 57. Application Layer Testing

Application services should be testable independently from HTTP.

Tests should cover:

* authorization;
* Business scope;
* Branch scope;
* subscription;
* device trust;
* transaction behavior;
* state transitions;
* idempotency;
* concurrency-sensitive operations;
* error mapping;
* event creation;
* background job creation;
* conflict handling.

Integration tests must verify real persistence behavior for critical workflows.

---

# 58. Performance Requirements

Application services must keep critical POS paths short.

Avoid:

* unnecessary repository calls;
* repeated authorization queries;
* synchronous report generation;
* synchronous notification delivery;
* unnecessary network calls;
* unnecessary configuration reloads.

Where safe, read-heavy reference data may be cached.

Critical state must remain authoritative.

---

# 59. Application Layer and Offline Operations

Offline operations use the same conceptual use cases where possible.

Example:

```text id="7s2n4m"
Online:
Frontend → API → Application Service

Offline:
Frontend → Local Application Service
```

The local implementation must preserve the same business rules as the server-side application model within the limits of offline authorization and locally available state.

When synchronized, the server validates the operation again.

---

# 60. Application Layer and Synchronization

Synchronization must not bypass normal domain rules.

Incorrect:

```text id="1z4p8k"
Sync
 ↓
Direct Database Insert
```

Correct:

```text id="3x7v2q"
Sync
 ↓
Application Use Case
 ↓
Domain Validation
 ↓
Transaction
 ↓
Persist
```

Synchronization may use specialized application commands, but they must still respect domain invariants.

---

# 61. Application Layer and Data Lifecycle

Data lifecycle operations are application-level workflows.

Examples:

```text
ExpireSubscription
StartDeletion
ProcessDeletion
CompleteDeletion
ReactivateBusiness
```

Deletion must not be implemented as an unrestricted database cascade initiated directly from the UI.

The lifecycle must remain controlled and auditable.

---

# 62. Application Layer and Configuration

Application services must resolve effective configuration before executing operations affected by configuration.

Example:

```text id="1c8s5p"
Order Acceptance
      ↓
Effective Product Configuration
      ↓
Effective Recipe
      ↓
Effective Price
      ↓
Inventory Rules
      ↓
Execute
```

Configuration snapshots used by operational transactions must remain historically identifiable.

---

# 63. Application Layer and Reporting

Reports should consume stable query interfaces rather than directly modifying operational domain state.

Report generation must use a consistent data snapshot.

The Application Layer coordinates:

```text
Scope
+
Date Range
+
Permissions
+
Snapshot
+
Report Calculation
+
Version
```

---

# 64. Application Layer and Notifications

Notifications are normally triggered after successful core state changes.

Example:

```text id="n2f7k4"
Cash Session Closed
       ↓
Commit
       ↓
Difference Detected
       ↓
Notification Job
```

Notification failure must not invalidate the closed Cash Session.

---

# 65. Application Layer and Printing

Printing is normally triggered after the relevant core transaction has committed.

Example:

```text id="h8q3m6"
Order Accepted
       ↓
Commit
       ↓
Create Print Job
       ↓
Printer Worker
```

The Application Layer must not wait indefinitely for physical printer response.

---

# 66. Application Layer and External Services

External service calls should be isolated behind adapters.

Example:

```text id="v6m2p8"
Application Service
      ↓
Payment Provider Interface
      ↓
Provider Adapter
      ↓
External Provider
```

The Application Layer should depend on stable internal interfaces rather than provider-specific APIs.

---

# 67. Application Layer Dependency Direction

Preferred dependency direction:

```text id="g6n2t8"
Presentation
    ↓
Application
    ↓
Domain
    ↓
Abstractions
    ↑
Infrastructure
```

Infrastructure implements abstractions required by the Application/Domain layers.

The Domain Layer should not depend on concrete infrastructure implementations.

---

# 68. Dependency Injection

Dependencies should be supplied through explicit interfaces.

Examples:

```text
OrderRepository
InventoryRepository
PaymentRepository
CashSessionRepository
ConfigurationRepository
AuditRepository
EventPublisher
JobQueue
Clock
TransactionManager
```

Concrete implementations belong to Infrastructure.

This improves:

* testing;
* replacement;
* isolation;
* maintainability.

---

# 69. Clock Abstraction

Time-sensitive operations should use an application-level clock abstraction.

Examples:

* subscription expiry;
* cash session timestamps;
* payment timestamps;
* offline authorization;
* report periods;
* data deletion eligibility;
* configuration effective dates.

This also makes deterministic testing possible.

---

# 70. Transaction UUID Propagation

Every important transactional workflow should carry a stable Transaction UUID where applicable.

Example:

```text id="r3m7w2"
Transaction UUID
      ↓
Application Command
      ↓
Domain Operation
      ↓
Audit
      ↓
Outbox / Event
      ↓
Synchronization
      ↓
Reports / History
```

This enables traceability and duplicate detection.

---

# 71. Correlation ID

A separate request-level Correlation ID may be used for technical tracing.

The distinction is:

```text
Correlation ID
→ Technical request trace

Transaction UUID
→ Business transaction identity
```

They must not be treated as interchangeable.

---

# 72. Application-Level Metrics

The Application Layer should expose metrics for important workflows.

Examples:

* order acceptance latency;
* payment latency;
* inventory transaction latency;
* synchronization latency;
* conflict count;
* failed jobs;
* report generation time;
* printer job failures;
* notification failures.

Metrics should not expose sensitive business information unnecessarily.

---

# 73. Application Architecture Completion Criteria

The Application Layer architecture is considered complete when:

* use-case boundaries are defined;
* command/query separation is defined;
* execution context is defined;
* authorization flow is defined;
* transaction boundaries are defined;
* cross-domain orchestration is defined;
* idempotency is defined;
* event handling is defined;
* background job initiation is defined;
* error handling is defined;
* dependency direction is defined;
* offline execution is defined;
* synchronization integration is defined;
* testing boundaries are defined;
* performance principles are defined.

---

# 74. Related Documents

### Previous Architecture

* `docs/04_Architecture/README.md`
* `docs/04_Architecture/01_System_Architecture.md`

### Next Architecture

* `docs/04_Architecture/03_Domain_Module_Architecture.md`

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 75. Final Status

**Status:** Accepted

This document defines the Application Layer architecture and establishes the boundaries between API, application use cases, domain logic, persistence, background processing, and external integrations.

The next architecture document is:

`docs/04_Architecture/03_Domain_Module_Architecture.md`

