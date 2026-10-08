# Application and Use Case Layer

**Document ID:** BE-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the Application Layer and Use Case architecture of FastFood ERP.

The Application Layer coordinates business operations between:

* API;
* authentication and authorization;
* domain services;
* repositories;
* transaction management;
* audit;
* outbox;
* background processing;
* synchronization;
* reporting.

The Application Layer is responsible for turning a business request into a controlled application operation.

---

# 2. Application Layer Principle

The Application Layer answers:

> What must happen when the system receives a business operation?

It does not primarily define:

> What is the business rule itself?

Business rules belong to the Domain Layer.

For example:

```text
Application:
AcceptOrder
    ↓
load order
validate access
invoke domain rules
persist changes
create audit
create outbox event
commit
```

Domain:

```text
Order
    ↓
Can this order be accepted?
```

---

# 3. Application Layer Responsibilities

The Application Layer is responsible for:

1. Use-case orchestration.
2. Transaction ownership.
3. Authorization integration.
4. Business context validation.
5. Repository coordination.
6. Domain service invocation.
7. Audit coordination.
8. Outbox coordination.
9. Idempotency coordination.
10. Error translation.
11. Background-job invocation.
12. Synchronization orchestration.

It must not become a second Domain Layer.

---

# 4. Use Case Definition

A Use Case represents one meaningful application operation.

Examples:

```text
CreateOrder
AddOrderItem
ModifyOrder
AcceptOrder
CancelOrder

RecordPayment
CreateRefund
CreateDebt
RecordDebtRepayment

OpenCashSession
CloseCashSession
HandoverCash

ReceiveInventory
AdjustInventory
ApproveRecipe

ChangeProductPrice
ChangeBranchPrice
ConfigureBranchMenu

GenerateReport
SynchronizeOfflineBatch
```

A use case should represent user/business intent rather than generic database manipulation.

---

# 5. Use Case Naming

Use cases should use action-oriented names.

Preferred:

```text
AcceptOrder
CloseCashSession
RecordPayment
ApproveRecipe
ChangeProductPrice
HandoverCash
```

Avoid:

```text
OrderService
CashService
PaymentManager
GenericCrudService
```

unless the class genuinely represents a reusable domain service rather than a use case.

---

# 6. Use Case Structure

A use case may follow this structure:

```text
Use Case
    ↓
Input
    ↓
Context
    ↓
Authorization
    ↓
Idempotency
    ↓
Load Data
    ↓
Domain Validation
    ↓
Perform Operation
    ↓
Persist Changes
    ↓
Audit / Outbox
    ↓
Commit
    ↓
Output
```

Not every use case requires every step.

The implementation must include only the applicable steps.

---

# 7. Use Case Input

Use cases should receive explicit input objects.

Example:

```text
AcceptOrderInput
    order_id
    employee_id
    branch_id
    device_id
    operation_id
```

The input should contain the data required for the operation.

It should not receive:

* raw HTTP requests;
* Flask/FastAPI response objects;
* database session objects unless explicitly part of infrastructure abstraction.

---

# 8. Use Case Context

A server-side application context may contain:

```text
ApplicationContext
    request_id
    operation_id
    employee_id
    business_id
    branch_id
    device_id
    cash_register_id
    cash_session_id
    source
```

Not every field is required for every operation.

The context must be derived from authenticated state and validated server-side.

---

# 9. Context Is Not Authorization

Having:

```text
branch_id = Branch-A
```

does not mean the employee is authorized to operate Branch A.

The Application Layer must evaluate:

```text
Employee
+
Business Membership
+
Branch Scope
+
Permission
+
Employee Status
+
Subscription Entitlement
```

before executing a protected operation.

---

# 10. Authorization Boundary

Authorization should occur before business state is changed.

Example:

```text
AcceptOrder
    ↓
Employee active?
    ↓
Business accessible?
    ↓
Branch accessible?
    ↓
Permission valid?
    ↓
Subscription permits operation?
    ↓
Continue
```

A frontend-hidden button is never considered an authorization mechanism.

---

# 11. Subscription Entitlement

The Application Layer must enforce subscription restrictions.

Example:

```text
Business ACTIVE
    → normal operation

Business READ_ONLY
    → read/export/history
    → modification blocked

Business DELETING
    → operational requests blocked

Business DELETED
    → operational requests rejected
```

Offline synchronization must pass the same lifecycle checks.

---

# 12. Employee Status

An inactive employee must not perform new protected operations.

The Application Layer must validate employee status before executing relevant use cases.

Historical actions remain associated with the original employee.

---

# 13. Permission Evaluation

Permission evaluation follows:

```text
Role Permission
       +
Employee Override
       +
Branch Scope
       +
Employee Status
       +
Subscription Entitlement
       +
Operational State
```

The final decision must be made server-side.

The Application Layer should call a centralized authorization mechanism rather than duplicating permission logic in every use case.

---

# 14. Transaction Ownership

The Application Layer owns transaction boundaries.

Example:

```text
with transaction:
    order = order_repository.get(...)
    inventory = inventory_repository.get(...)
    order.accept(...)
    inventory.deduct(...)
    audit.create(...)
    outbox.add(...)

commit
```

Repositories should not unexpectedly commit independently.

---

# 15. Atomic Core Operations

Operations that modify tightly coupled business state must be atomic.

Examples:

### Order acceptance

```text
Order state
+
Inventory deduction
+
Required operational records
```

### Payment

```text
Payment record
+
Financial state
+
Required payment history
```

### Cash closing

```text
Session closing
+
Actual cash
+
Difference
+
Required history
```

### Shift handover

```text
Previous session closing
+
Handover
+
New session opening
```

If required core operations fail, the transaction must not leave partial business state.

---

# 16. Secondary Operations

Secondary effects must not unnecessarily block core transactions.

Examples:

* notification;
* report generation;
* email;
* export;
* analytics event.

Preferred:

```text
Core Transaction
      ↓
COMMIT
      ↓
Outbox
      ↓
Background Worker
```

Failure of a secondary operation must not automatically roll back the committed core transaction.

---

# 17. Idempotency

Retryable use cases must support idempotency.

A unique operation UUID should identify the logical operation.

Example:

```text
Operation UUID
      ↓
Already processed?
    /       \
  Yes        No
   ↓          ↓
Return      Execute
existing       ↓
result       Save result
```

This applies to:

* online retries;
* client retries;
* offline synchronization;
* background job retries.

---

# 18. Idempotency Scope

Idempotency records should identify at least the relevant:

* Business;
* operation UUID;
* operation type;
* source;
* processing result.

An operation UUID must not accidentally become globally reusable across unrelated operations.

---

# 19. Duplicate Request Handling

When a duplicate request is received:

```text
Same operation UUID
+
Same operation type
+
Same Business
```

the backend should return the previously recorded result where appropriate.

It must not create:

* duplicate payments;
* duplicate inventory deductions;
* duplicate cash operations;
* duplicate configuration versions;
* duplicate reports.

---

# 20. Mismatched Idempotency

If the same operation UUID is reused with materially different payload/context, the backend must reject it.

Example:

```text
Operation UUID = X
First request:
    Order = A

Second request:
    Order = B
```

This is an idempotency conflict, not a new operation.

---

# 21. Repository Coordination

A use case may coordinate several repositories.

Example:

```text
AcceptOrder
    ↓
OrderRepository
InventoryRepository
ProductRepository
RecipeRepository
AuditRepository
OutboxRepository
```

The use case is responsible for coordinating the workflow.

Repositories remain responsible for persistence operations.

---

# 22. Repository Scope

The Application Layer must provide validated scope to repositories.

For Business-owned records:

```text
business_id
```

must be available where required.

For Branch-owned operations:

```text
business_id
branch_id
```

must be validated.

The application must not rely on a client-provided identifier as proof of ownership.

---

# 23. Domain Invocation

The Application Layer should invoke domain behavior rather than reimplementing it.

Bad:

```text
if order.status == "draft":
    order.status = "accepted"
```

when the Order domain owns the lifecycle.

Preferred:

```text
order.accept(...)
```

The domain then validates the transition.

---

# 24. Application vs Domain Responsibility

### Application Layer

Responsible for:

* workflow;
* orchestration;
* transaction;
* repositories;
* authorization integration;
* audit/outbox coordination.

### Domain Layer

Responsible for:

* business invariants;
* state transitions;
* calculations;
* domain rules;
* domain validation.

Example:

```text
Application:
AcceptOrderUseCase

Domain:
Order.accept()
Inventory.can_deduct()
Pricing.calculate()
```

---

# 25. Application Services

Application services may coordinate multiple domain operations.

Examples:

```text
OrderApplicationService
CashApplicationService
InventoryApplicationService
PaymentApplicationService
ConfigurationApplicationService
```

However, use cases should remain explicit where an operation is important.

A generic application service must not hide the entire business workflow.

---

# 26. Use Case Output

Use cases should return explicit result objects where useful.

Example:

```text
AcceptOrderResult
    order_id
    status
    accepted_at
    inventory_result
    operation_id
```

The API layer then converts the result into the appropriate response schema.

Domain entities should not be serialized directly into API responses without deliberate mapping.

---

# 27. Read Use Cases

Read operations may also use application services/use cases.

Examples:

```text
GetOrder
GetMenu
GetCashSession
GetInventory
GetEmployee
GetDashboard
GetReport
```

Read use cases may use optimized query repositories where appropriate.

They do not always need the same orchestration complexity as write operations.

---

# 28. Query vs Command

The application layer should distinguish conceptually between:

### Commands

Change state:

```text
AcceptOrder
RecordPayment
CloseCashSession
ChangePrice
AdjustInventory
```

### Queries

Read state:

```text
GetOrder
GetMenu
GetInventory
GetCashReport
```

Commands require transaction and invariant enforcement.

Queries should avoid unnecessary state mutation.

---

# 29. Query Optimization

Read use cases may use specialized query objects when normal repositories would produce inefficient queries.

Example:

```text
DashboardQuery
OrderListQuery
InventorySummaryQuery
CashReportQuery
```

These query components must still enforce:

* Business scope;
* Branch scope;
* permissions.

Performance optimization must never remove security boundaries.

---

# 30. Order Acceptance Use Case

Conceptual flow:

```text
AcceptOrder
    ↓
Authenticate context
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
Load Order
    ↓
Validate Order State
    ↓
Validate Products
    ↓
Validate Recipe / Set
    ↓
Validate Inventory
    ↓
Deduct Inventory
    ↓
Accept Order
    ↓
Create Audit
    ↓
Create Outbox Event
    ↓
Commit
```

This operation must be atomic for all required core state changes.

---

# 31. Create Order Use Case

Create Order should:

1. Validate Business.
2. Validate Branch.
3. Validate employee.
4. Validate permission.
5. Validate active Cash Session where required.
6. Determine applicable menu configuration.
7. Create Order.
8. Assign customer-facing order number according to session rules.
9. Preserve source/device context.
10. Persist the Order.

The Order should initially remain in the appropriate draft state.

---

# 32. Add Order Item Use Case

Adding an item should:

1. Load Order.
2. Validate employee access.
3. Validate Order state.
4. Resolve effective Product configuration.
5. Resolve applicable price.
6. Validate menu availability.
7. Capture price snapshot.
8. Add Order Item.
9. Recalculate applicable Order financial state.
10. Persist the change.

If inventory validation is required only at acceptance, the backend must not unnecessarily deduct inventory during item creation.

---

# 33. Modify Order Use Case

Modification should:

* validate Order state;
* validate permission;
* preserve existing item history where required;
* apply current valid configuration to newly added items;
* preserve existing price snapshots;
* record required comments/history.

A current Product price must not rewrite an existing Order Item price.

---

# 34. Payment Use Case

Record Payment should:

1. Validate employee.
2. Validate Branch.
3. Validate Order.
4. Validate Order financial state.
5. Validate payment method.
6. Validate amount.
7. Apply payment rules.
8. Persist Payment.
9. Update authoritative financial state.
10. Create required audit/history.
11. Commit.

Duplicate payment retries must be idempotent.

---

# 35. Refund Use Case

Refund should:

1. Validate employee.
2. Validate permission.
3. Validate Branch.
4. Validate original payment/order.
5. Require refund reason.
6. Validate refund amount.
7. Preserve original financial history.
8. Create refund transaction/revision.
9. Create audit event.
10. Commit.

Current Product price must never be used to recalculate historical refund amounts.

---

# 36. Cash Session Opening

Opening a Cash Session should:

1. Validate employee.
2. Validate Branch.
3. Validate Cash Register.
4. Validate that no conflicting active session exists.
5. Validate starting cash.
6. Create Cash Session.
7. Record opening context.
8. Create audit event.
9. Commit.

Concurrent opening attempts must be resolved deterministically.

---

# 37. Cash Session Closing

Closing should:

1. Validate active session.
2. Validate employee authority.
3. Calculate expected cash.
4. Record actual cash.
5. Calculate difference.
6. Require required comment.
7. Persist closing.
8. Create audit event.
9. Commit.

A closed session cannot be reopened through the ordinary close/open workflow.

---

# 38. Shift Handover

Handover should coordinate:

```text
Previous Cash Session
        ↓
Cash Count
        ↓
Handover Record
        ↓
Previous Cashier Confirmation
        ↓
New Cashier Authentication
        ↓
New Cash Session
```

The complete operation must preserve the required historical chain.

---

# 39. Inventory Receipt

Inventory receipt should:

1. Validate employee permission.
2. Validate Branch/Warehouse.
3. Validate Product.
4. Validate quantity.
5. Validate cost.
6. Record source.
7. Create inventory transaction.
8. Update stock.
9. Create relevant audit/history.
10. Commit.

The operation must preserve FIFO/cost information required by the inventory model.

---

# 40. Inventory Adjustment

Inventory adjustment should:

* require appropriate permission;
* record reason;
* record before quantity;
* record adjustment quantity;
* record after quantity;
* preserve actor;
* preserve Branch/Warehouse;
* create audit/history.

Direct arbitrary mutation of stock quantity is prohibited.

---

# 41. Price Change Use Case

A price change should:

1. Validate employee.
2. Validate permission.
3. Validate Business.
4. Validate Branch scope where applicable.
5. Validate current configuration version.
6. Create new configuration version.
7. Set effective boundary.
8. Preserve previous version.
9. Create audit event.
10. Commit.

Stale configuration versions must result in conflict.

---

# 42. Recipe Approval Use Case

Recipe approval should:

1. Validate employee permission.
2. Validate Recipe state.
3. Validate required components.
4. Validate recipe structure.
5. Create approved Recipe Version.
6. Preserve previous version.
7. Set effective boundary.
8. Create audit event.
9. Commit.

Historical inventory deductions continue referencing their original Recipe Version.

---

# 43. Report Generation Use Case

Report generation should:

1. Validate Business.
2. Validate Branch scope.
3. Validate report permission.
4. Validate requested period.
5. Determine report type.
6. Create report generation request.
7. Generate synchronously or asynchronously according to report size.
8. Create immutable Report Version.
9. Store result/reference.
10. Notify user when required.

Report generation must not block critical POS transactions unnecessarily.

---

# 44. Offline Synchronization Use Case

Synchronization should:

1. Authenticate trusted device.
2. Validate device authorization.
3. Validate Business.
4. Validate Business lifecycle.
5. Validate batch.
6. Validate operation UUIDs.
7. Validate dependency ordering.
8. Validate permissions applicable at operation time.
9. Validate domain rules.
10. Execute valid operations.
11. Detect conflicts.
12. Record synchronization result.
13. Return deterministic results.

Offline data must not bypass normal server-side business rules.

---

# 45. Partial Synchronization

A batch may contain multiple operations.

The system may process operations independently where dependency rules allow.

Example:

```text
Operation A → SYNCED
Operation B → CONFLICT
Operation C → SYNCED
Operation D → RETRY
```

The entire batch should not automatically fail merely because one independent operation fails.

Dependencies must be respected.

---

# 46. Application Error Categories

Use cases should produce controlled application errors.

Categories include:

```text
ValidationError
AuthorizationError
BusinessRuleViolation
ConflictError
IdempotencyError
NotFoundError
SubscriptionRestriction
ConcurrencyError
TemporaryInfrastructureError
PermanentInfrastructureError
```

These are mapped to transport-specific responses by the API layer.

---

# 47. Error Handling Rule

When an error occurs inside a core transaction:

```text
Error
 ↓
Rollback
 ↓
No partial core state
```

When a secondary background operation fails:

```text
Secondary Failure
 ↓
Retry / Dead Letter / Alert
 ↓
Core transaction remains committed
```

The exact behavior depends on the operation.

---

# 48. Audit Coordination

Important use cases must create audit information.

The Application Layer should provide the audit context:

```text
event_uuid
business_id
branch_id
employee_id
device_id
cash_session_id
operation_id
entity_id
source
```

The Domain Layer determines what business change occurred.

The Audit module persists the historical event.

---

# 49. Outbox Coordination

When a committed operation requires asynchronous processing:

```text
Use Case
    ↓
Core State
+
Outbox Event
    ↓
COMMIT
```

The Application Layer ensures that both are included in the same transaction when required.

---

# 50. Notification Coordination

The use case should not directly depend on a notification provider.

Preferred:

```text
Use Case
   ↓
Outbox Event
   ↓
Notification Handler
   ↓
Notification Service
```

This prevents notification latency from slowing core operations.

---

# 51. External Integration

External calls should normally occur outside core database transactions.

If an external service is required for the business operation, the use case must define:

* timeout;
* retry;
* idempotency;
* reconciliation;
* failure behavior.

External failure must never be silently ignored when the external operation is business-critical.

---

# 52. Transaction Retry

Some infrastructure failures may allow transaction retry.

Retries must only occur when:

* the operation is known to be safe;
* transaction state is discarded;
* idempotency is preserved;
* retry does not duplicate side effects.

Do not blindly retry all exceptions.

---

# 53. Concurrency

Use cases must account for concurrent operations.

Examples:

```text
Two employees accepting the same Order
Two payments for the same amount
Two cashiers opening a session
Two users changing a price
Two inventory deductions
```

The application and database layers must work together to guarantee the relevant invariant.

---

# 54. Locking

Use cases should request narrow locks only where required.

Examples:

* inventory quantity row;
* active Cash Session;
* configuration version;
* payment state.

Locks should be acquired in a predictable order where multiple resources are involved.

---

# 55. Long Operations

Long operations should not remain inside a normal request transaction.

Examples:

* large report generation;
* large XLSX export;
* data deletion;
* extensive synchronization;
* large historical analysis.

Preferred:

```text
Request
 ↓
Create Job
 ↓
Commit
 ↓
Worker
 ↓
Long Operation
```

---

# 56. Use Case Observability

Each important use case should be traceable through:

```text
request_id
operation_id
business_id
branch_id
employee_id
device_id
```

Where applicable.

This allows operational investigation without exposing sensitive business data in logs.

---

# 57. Performance

Use cases must avoid unnecessary database queries.

For POS-critical operations:

* use targeted queries;
* load only required data;
* avoid unnecessary relationships;
* avoid N+1 queries;
* keep transactions short;
* avoid network calls inside transactions;
* avoid synchronous notifications.

Correctness remains more important than micro-optimizations.

---

# 58. Caching in Use Cases

Caching may be used for read-heavy data.

However, a use case must never assume cached data is authoritative for critical mutable state such as:

* inventory;
* cash;
* payment;
* subscription entitlement;
* permissions;
* historical transactions.

Critical state must be validated against authoritative storage.

---

# 59. Application Layer Testing

Every important use case should have tests covering:

### Success

```text
Valid request
→ expected state
```

### Authorization

```text
Unauthorized request
→ rejected
```

### Business scope

```text
Wrong Business
→ rejected
```

### Branch scope

```text
Wrong Branch
→ rejected
```

### Concurrency

```text
Concurrent operation
→ invariant preserved
```

### Idempotency

```text
Retry
→ no duplicate state
```

### Failure

```text
Exception
→ rollback
```

### Historical integrity

```text
Current configuration change
→ historical transaction unchanged
```

---

# 60. Use Case Test Example

For `AcceptOrder`:

```text
Given:
    valid employee
    valid Branch
    valid permission
    active subscription
    valid Order
    sufficient stock

When:
    AcceptOrder is executed

Then:
    Order becomes Accepted
    Inventory is deducted
    Audit event exists
    Outbox event exists
    Transaction commits
```

Failure case:

```text
Given:
    insufficient stock

When:
    AcceptOrder is executed

Then:
    Order remains unaccepted
    Inventory remains unchanged
    Core transaction rolls back
```

---

# 61. Application Layer Guardrails

The following are prohibited:

1. API routes directly modifying database state.
2. Use cases directly manipulating ORM internals unnecessarily.
3. Repositories committing independent transactions inside larger workflows.
4. Domain entities depending on HTTP frameworks.
5. Client-provided Business ID being treated as authorization.
6. Client-provided Branch ID being treated as authorization.
7. Frontend permission checks being treated as security.
8. Notification delivery inside critical transactions.
9. Duplicate retryable operations.
10. Silent last-write-wins for important configuration.
11. Current configuration rewriting historical transactions.
12. Background jobs duplicating domain rules.
13. Long-running work inside POS-critical transactions.
14. External network calls inside transactions unless explicitly required.
15. Generic CRUD operations bypassing business workflows.
16. Uncontrolled direct stock mutation.
17. Uncontrolled direct Cash Session status mutation.
18. Uncontrolled direct Payment status mutation.
19. Bypassing subscription restrictions through offline synchronization.
20. Returning raw database exceptions to API clients.

---

# 62. Application Layer Invariants

1. Every protected use case validates authorization.
2. Business scope is validated server-side.
3. Branch scope is validated server-side.
4. Employee status is validated where required.
5. Subscription entitlement is validated for modifying operations.
6. Core state changes occur within explicit transactions.
7. Core operations preserve atomicity.
8. Retryable operations use idempotency.
9. Duplicate requests do not duplicate business state.
10. Stale configuration updates produce conflicts.
11. Historical snapshots remain immutable.
12. Audit events are created for important changes.
13. Required outbox events are committed atomically with core state.
14. Secondary failures do not normally roll back committed core state.
15. Domain rules remain in the Domain Layer.
16. Persistence remains behind repository/infrastructure boundaries.
17. API transport concerns remain outside business logic.
18. Offline synchronization uses the same authoritative business rules.
19. Concurrency-sensitive operations preserve their invariants.
20. Long-running work is moved to background processing where appropriate.
21. Read operations do not mutate business state unexpectedly.
22. Application errors are translated into controlled responses.
23. Historical transactions are never reinterpreted using current configuration.
24. Core POS workflows remain performant.
25. The Application Layer remains orchestration-focused.

---

# 63. Example Use Case Structure

A conceptual implementation may look like:

```text
class AcceptOrderUseCase:

    def execute(input, context):

        authorize(context, "order.accept")

        check_idempotency(input.operation_id)

        with transaction:

            order = order_repository.get_for_update(
                business_id=context.business_id,
                branch_id=context.branch_id,
                order_id=input.order_id
            )

            order_acceptance_service.validate(order)

            inventory_service.validate_and_deduct(
                order=order,
                branch_id=context.branch_id
            )

            order.accept(context.employee_id)

            audit_service.record(...)

            outbox_service.add(...)

            save_idempotency_result(...)

        return result
```

This is illustrative structure only.

The final implementation must follow the actual framework and coding standards defined in later Backend documents.

---

# 64. Recommended Application Directory

The resulting structure is:

```text
app/application/
├── business/
├── identity/
├── subscription/
├── devices/
├── products/
├── recipes/
├── inventory/
├── menu/
├── orders/
├── tables/
├── payments/
├── cash/
├── handover/
├── attendance/
├── payroll/
├── notifications/
├── audit/
├── reports/
├── synchronization/
├── configuration/
└── lifecycle/
```

Each module contains only the use cases and application-level coordination belonging to that domain.

---

# 65. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `16_Offline_and_Synchronization_Backend.md`
* `17_Background_Jobs_and_Scheduling.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/02_Database_Architecture.md`
* `../05_Database/13_Order_and_Order_Item_Data_Model.md`
* `../05_Database/15_Payment_and_Debt_Data_Model.md`
* `../05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `../05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `../05_Database/23_Configuration_Data_Model.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/16_Inventory_Transaction_System.md`
* `../02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`

---

# 66. Status

**Backend Architecture:** Accepted

**Project Structure:** Accepted

**Application Layer:** Accepted

**Transaction Ownership:** Application Layer

**Business Rules:** Domain Layer

**Persistence:** Repository / Infrastructure Layer

**Authorization:** Server-side

**Idempotency:** Required for retryable operations

**Audit:** Application-coordinated

**Outbox:** Application-coordinated

**Next Document:** `04_Domain_Service_and_Business_Logic.md`

