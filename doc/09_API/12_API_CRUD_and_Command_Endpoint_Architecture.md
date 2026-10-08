# API CRUD and Command Endpoint Architecture

**Document ID:** API-12
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines when FastFood ERP API operations should use standard CRUD-style resource endpoints and when they must use explicit business command endpoints.

The primary objective is to prevent the API from becoming a generic database CRUD layer.

The API must expose business capabilities through predictable contracts while preserving:

* domain invariants;
* authorization;
* Business and Branch isolation;
* transaction correctness;
* idempotency;
* concurrency control;
* auditability;
* historical integrity;
* offline compatibility;
* predictable API behavior.

CRUD is appropriate for simple resource lifecycle operations.

Explicit command endpoints are required when an operation represents a meaningful business action rather than a simple resource field change.

---

# 2. Scope

This document covers:

* CRUD principles;
* resource-oriented endpoints;
* create operations;
* read operations;
* update operations;
* delete/archive behavior;
* explicit business commands;
* command naming;
* command request contracts;
* command response contracts;
* command authorization;
* command idempotency;
* command concurrency;
* command transaction boundaries;
* command state transitions;
* financial commands;
* inventory commands;
* configuration commands;
* approval commands;
* lifecycle commands;
* bulk commands;
* asynchronous commands;
* offline commands;
* command errors;
* audit;
* historical integrity;
* endpoint design guardrails;
* API invariants.

This document does not define detailed business rules for individual modules.

Those are defined in the endpoint-specific API documents.

---

# 3. Core Principle

The API must distinguish between:

```text
Resource State
```

and:

```text
Business Action
```

For example:

```text
PATCH /products/{id}
```

may update a simple Product attribute.

But:

```text
POST /recipes/{id}/approve
```

represents a business decision.

Similarly:

```text
POST /orders/{id}/pay
```

is not merely an update to:

```text
payment_status = PAID
```

The payment command may involve:

* authorization;
* idempotency;
* financial validation;
* payment creation;
* Order state transition;
* audit;
* inventory/cash effects where applicable.

Therefore it must be represented explicitly.

---

# 4. CRUD Definition

CRUD represents:

```text
Create
Read
Update
Delete
```

Typical resource operations are:

```text
POST   /products
GET    /products/{id}
PATCH  /products/{id}
DELETE /products/{id}
```

CRUD is appropriate when the operation does not require a complex business workflow beyond ordinary resource validation.

---

# 5. CRUD Does Not Mean Database CRUD

The API must never expose database tables directly.

The following architecture is prohibited:

```text
HTTP Request
   ↓
ORM Model
   ↓
Database INSERT/UPDATE/DELETE
```

The correct architecture is:

```text
HTTP Request
   ↓
API Contract
   ↓
Application Use Case
   ↓
Domain Rules
   ↓
Repository
   ↓
PostgreSQL
```

Even a simple CRUD endpoint must pass through the Application layer.

---

# 6. Resource-Oriented API

Resources should have stable public identities.

Examples:

```text
/businesses
/branches
/employees
/products
/categories
/recipes
/sets
/inventory
/orders
/payments
/cash-sessions
/attendance
/payroll
/reports
/notifications
/files
/configuration
```

The public resource model must not expose internal database table names merely because those tables exist.

---

# 7. Create Operations

Standard resource creation may use:

```text
POST /resources
```

Example:

```text
POST /products
```

The Application layer is responsible for:

* generating or validating identity;
* validating scope;
* applying business rules;
* persisting the resource;
* creating required audit/outbox records;
* committing the transaction.

---

# 8. Create vs Command

Creation should remain a normal resource operation when the primary effect is:

> Create a new resource.

Example:

```text
POST /products
```

A command should be used when creation represents a specific business action.

Example:

```text
POST /inventory/receipts
```

may represent an inventory receiving operation rather than generic creation of an internal database record.

The public contract should express the business meaning.

---

# 9. Read Operations

Read operations use:

```text
GET
```

Examples:

```text
GET /products
GET /products/{id}
GET /orders/{id}
GET /cash-sessions/{id}
```

Read operations must enforce:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* subscription visibility;
* resource visibility.

Read operations must never assume that possession of a UUID grants access.

---

# 10. Read Models

Read endpoints may use dedicated read models.

Example:

```text
GET /orders
```

may return an Order Summary rather than a complete Domain Order aggregate.

This improves:

* performance;
* response size;
* query efficiency;
* security filtering.

Read models remain derived representations.

They are not authoritative business state.

---

# 11. Update Operations

Simple resource updates may use:

```text
PATCH /resources/{id}
```

Example:

```text
PATCH /products/{id}
```

The update must contain only fields that the endpoint explicitly allows.

The API must not expose unrestricted JSON patching of arbitrary resource properties.

---

# 12. Partial Update

PATCH semantics should represent partial resource changes.

Example:

```json
{
  "name": "Chicken Burger",
  "active": true
}
```

The Application layer determines whether the change is valid.

The client cannot use PATCH to bypass a business workflow.

---

# 13. When PATCH Is Appropriate

PATCH is appropriate when:

* the resource remains the same;
* the identity remains unchanged;
* the change is a direct configuration update;
* no separate approval workflow is required;
* no complex state transition is being represented;
* no special financial transaction is created.

Examples may include:

```text
Update Product display name
Update Branch description
Update Employee display name
Update Business settings
```

subject to permissions and business rules.

---

# 14. When PATCH Is Not Appropriate

PATCH must not be used to represent important business commands such as:

```text
Pay Order
Refund Order
Accept Order
Close Cash Session
Approve Recipe
Adjust Inventory
Transfer Cash
Approve Configuration
Deactivate Employee
```

These operations have business semantics and should use explicit command endpoints.

---

# 15. Delete Operations

Generic DELETE must be used carefully.

FastFood ERP prefers historical integrity.

Therefore many business resources must not be physically deleted after becoming part of operational history.

Instead:

```text
Archive
Deactivate
Close
Cancel
Retire
```

may be represented as explicit business commands.

---

# 16. Physical Deletion

Physical deletion is appropriate only when:

* the resource has no historical dependency;
* deletion is explicitly allowed;
* no audit/history requirement is violated;
* no foreign-key dependency remains;
* lifecycle rules permit deletion.

The Application layer must determine whether physical deletion is allowed.

---

# 17. Archive Instead of Delete

Examples:

```text
Product
Recipe
Set
Configuration
Employee
```

may require archival rather than deletion.

Example:

```text
POST /products/{id}/archive
```

is preferable to:

```text
DELETE /products/{id}
```

when the Product has historical dependencies.

---

# 18. Command Endpoint Definition

A command endpoint represents an explicit business action.

Typical form:

```text
POST /resource/{id}/{command}
```

Examples:

```text
POST /orders/{id}/accept
POST /orders/{id}/cancel
POST /orders/{id}/pay
POST /orders/{id}/refund
POST /recipes/{id}/approve
POST /cash-sessions/{id}/close
POST /employees/{id}/deactivate
```

Commands should use POST because they represent state-changing actions and may create business effects.

---

# 19. Command Naming

Command names should use clear business verbs.

Preferred:

```text
/accept
/pay
/refund
/approve
/close
/cancel
/archive
/activate
/deactivate
/adjust
/transfer
/handover
```

Avoid generic names such as:

```text
/process
/update-status
/execute
/action
/change
/do
```

unless the domain meaning genuinely requires them.

---

# 20. Command Must Represent Intent

A command should answer:

> What business action is the actor requesting?

Example:

```text
POST /orders/{id}/pay
```

is clearer than:

```text
PATCH /orders/{id}
{
  "status": "PAID"
}
```

The command expresses intent.

The server determines whether the requested transition is valid.

---

# 21. State Transitions

Commands commonly cause state transitions.

Example:

```text
Order
OPEN
 ↓
ACCEPT
 ↓
ACCEPTED
 ↓
PAY
 ↓
PAID
```

The client requests the transition.

The Domain determines whether it is allowed.

The client must not directly assign arbitrary states.

---

# 22. State Assignment Prohibition

The API must not expose unrestricted state mutation such as:

```json
{
  "status": "PAID"
}
```

for state machines where transitions have business meaning.

Instead:

```text
POST /orders/{id}/pay
```

must execute the payment workflow.

---

# 23. Command Request Contract

A command may require input.

Example:

```text
POST /orders/{id}/refund
```

Request:

```json
{
  "amount": "25000.00",
  "reason": "Incorrect order"
}
```

The request contains business input.

The server calculates and validates authoritative effects.

---

# 24. Client-Provided Totals

Client-provided totals are never authoritative for financial operations.

For example:

```json
{
  "amount": "25000.00"
}
```

may be accepted as requested payment input.

But the server must validate it against:

* Order state;
* authoritative Order amount;
* previous payments;
* refund state;
* permissions;
* business rules.

The client cannot define the final financial result.

---

# 25. Command Response

A successful command should return enough information for the client to continue safely.

Possible response:

```json
{
  "data": {
    "order_id": "018f...",
    "status": "PAID",
    "operation_id": "01J..."
  }
}
```

The exact response depends on the command.

---

# 26. Command Idempotency

Retryable commands must support idempotency.

Example:

```http
POST /orders/{id}/pay
Idempotency-Key: 01J...
```

A repeated request with the same valid operation identity must not duplicate the business effect.

This is especially important for:

* payments;
* refunds;
* inventory adjustments;
* cash operations;
* synchronization;
* configuration changes.

Detailed idempotency rules are defined in:

`10_API_Idempotency_and_Concurrency.md`

---

# 27. Command Concurrency

Commands must protect against concurrent state changes.

Examples:

```text
Two cashiers pay the same Order
Two employees close the same Cash Session
Two users approve the same Recipe
Two users modify the same configuration
```

The Application/Domain/Database layers must enforce concurrency rules.

The command endpoint must not assume that the resource state observed by the client is still current.

---

# 28. Optimistic Concurrency

Configuration and editable resources may use version-based concurrency.

Example:

```http
If-Match: "12"
```

If the current version is 13:

```text
409 Conflict
STALE_VERSION
```

The server must not silently overwrite version 13.

---

# 29. Pessimistic Concurrency

Targeted database locks may be used for operations where simultaneous execution would be unsafe.

Examples:

* inventory deduction;
* Cash Session closing;
* payment state transition;
* financial correction.

Locks must remain narrow and short-lived.

---

# 30. Command Transaction Boundary

A business command should normally execute within a clearly defined Application transaction.

Example:

```text
Accept Order
    ↓
Validate
    ↓
Load authoritative state
    ↓
Apply Domain rules
    ↓
Update Order
    ↓
Inventory deduction
    ↓
Audit / Outbox
    ↓
Commit
```

Secondary effects should not unnecessarily extend the core transaction.

---

# 31. Secondary Effects

After successful commit, the system may perform:

* printing;
* notifications;
* cache invalidation;
* report updates;
* external integration;
* asynchronous processing.

Failure of these secondary operations must not incorrectly rollback already committed core business state.

---

# 32. Audit and Commands

Important commands must generate appropriate audit events.

Examples:

```text
Pay Order
Refund Order
Adjust Inventory
Approve Recipe
Close Cash Session
Change Price
Change Permissions
Deactivate Employee
```

Audit records should preserve:

* actor;
* Business;
* Branch;
* device;
* operation UUID;
* resource;
* old state where required;
* new state;
* timestamp;
* reason where required.

---

# 33. Command and Historical Integrity

Commands must never rewrite historical facts.

For example:

```text
Refund
```

must create a financial correction/refund effect.

It must not change the original Order Item price.

Similarly:

```text
Recipe Change
```

must create a new Recipe Version rather than rewriting historical Recipe usage.

---

# 34. Command Authorization

Every command must validate:

1. authenticated actor;
2. employee status;
3. Business scope;
4. Branch scope;
5. permission;
6. subscription entitlement;
7. device restrictions where applicable;
8. resource state;
9. business rules.

Authorization must be evaluated on the server.

---

# 35. Manager Authority

A Manager may execute only commands permitted by their effective permissions.

For permission-management commands, a Manager must not grant permissions beyond their own authority.

Example:

```text
Manager
   ↓
Permission Change Request
   ↓
Authority Check
   ↓
Allowed Scope
```

---

# 36. Subscription Restrictions

Commands are subject to subscription state.

For example:

```text
ACTIVE
→ modifying commands allowed according to permissions

READ_ONLY
→ modifying commands blocked

DELETION_ELIGIBLE
→ normal business mutation blocked

DELETED
→ normal API access blocked
```

Read operations may remain available according to lifecycle rules.

---

# 37. Command and Business Scope

Every command must operate within an authoritative Business context.

The client cannot change:

```text
business_id
```

to execute the same command against another Business.

The server validates resource ownership and scope.

---

# 38. Command and Branch Scope

Branch-scoped commands must validate Branch access.

Example:

```text
POST /branches/{branch_id}/products/{product_id}/activate
```

must verify:

* Business ownership;
* employee Branch scope;
* permission;
* Product state.

A Branch UUID is not an authorization credential.

---

# 39. Resource-Level Commands

Commands should normally be attached to the resource they operate on.

Example:

```text
POST /orders/{order_id}/accept
```

rather than:

```text
POST /commands
{
  "type": "ACCEPT_ORDER",
  "resource_id": "..."
}
```

Resource-specific URLs are easier to understand and document.

---

# 40. Generic Command Endpoint

A generic command endpoint may be used only where the domain genuinely requires a generic operation model.

For example:

```text
POST /synchronization/operations
```

may represent heterogeneous synchronization operations.

However, normal business API commands should remain explicit.

---

# 41. Command Discovery

The API should expose supported commands through documentation and OpenAPI.

The frontend should not infer available commands merely from resource fields.

Command availability depends on:

* resource state;
* permissions;
* Business;
* Branch;
* subscription;
* device;
* operational conditions.

---

# 42. Command Availability

A UI may hide unavailable commands for usability.

However:

> Hiding a command in the frontend is not authorization.

The server must validate every command independently.

---

# 43. Command Error Behavior

Commands use the common API error contract.

Examples:

```text
ORDER_ALREADY_PAID
ORDER_NOT_ACCEPTED
INSUFFICIENT_STOCK
CASH_SESSION_CLOSED
RECIPE_NOT_APPROVED
ACCESS_DENIED
BRANCH_SCOPE_DENIED
STALE_VERSION
DUPLICATE_OPERATION
SUBSCRIPTION_READ_ONLY
```

Detailed error architecture is defined in:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 44. Create vs Approve

Some resources have a lifecycle where creation and approval are different operations.

Example:

```text
POST /recipes
```

creates a Recipe draft.

Then:

```text
POST /recipes/{id}/approve
```

represents approval.

Approval must not be represented as:

```text
PATCH /recipes/{id}
{
  "status": "APPROVED"
}
```

when approval is a controlled business decision.

---

# 45. Draft and Effective Configuration

Configuration may follow:

```text
Draft
 ↓
Approved
 ↓
Scheduled
 ↓
Effective
 ↓
Superseded
```

Each transition should use explicit commands where the transition has business significance.

Examples:

```text
POST /configurations/{id}/approve
POST /configurations/{id}/activate
POST /configurations/{id}/archive
```

---

# 46. Activation and Deactivation

Activation/deactivation should be explicit commands when they affect business availability.

Examples:

```text
POST /products/{id}/activate
POST /products/{id}/deactivate

POST /employees/{id}/activate
POST /employees/{id}/deactivate
```

This makes audit and authorization requirements explicit.

---

# 47. Cancel vs Delete

Cancellation is not deletion.

For example:

```text
POST /orders/{id}/cancel
```

means:

> The Order remains historically known but is transitioned into a cancelled state.

It should not be implemented as:

```text
DELETE /orders/{id}
```

when historical integrity requires retaining the Order.

---

# 48. Archive vs Delete

Archiving preserves resource identity and history.

Example:

```text
POST /products/{id}/archive
```

The Product may no longer be available for new operations while remaining available for:

* historical Orders;
* reports;
* inventory history;
* audit;
* Recipe history.

---

# 49. Close vs Delete

Cash Sessions must be closed rather than deleted.

Example:

```text
POST /cash-sessions/{id}/close
```

After closure:

```text
Closed Session
```

remains authoritative historical state.

A closed Cash Session must not be recreated through deletion/recreation.

---

# 50. Adjustment Commands

Inventory adjustments should use explicit commands.

Example:

```text
POST /inventory/adjustments
```

The request should include business context such as:

```json
{
  "product_id": "018f...",
  "quantity": "-2",
  "reason": "Inventory count discrepancy"
}
```

The server validates the actual inventory state and creates the authoritative Inventory Transaction.

---

# 51. Transfer Commands

Transfers should be represented explicitly.

Example:

```text
POST /inventory/transfers
```

or:

```text
POST /cash-handover/{id}/accept
```

A transfer represents movement between states or scopes and should not be reduced to unrelated PATCH operations.

---

# 52. Financial Commands

Financial operations must use explicit commands.

Examples:

```text
POST /orders/{id}/pay
POST /orders/{id}/refund
POST /cash-sessions/{id}/close
POST /cash-handover/{id}/accept
```

Financial commands require:

* authoritative state;
* idempotency;
* concurrency protection;
* permission validation;
* audit;
* historical integrity.

---

# 53. Payment Command

Payment must not be implemented as:

```text
PATCH /orders/{id}
{
  "paid": true
}
```

Correct model:

```text
POST /orders/{id}/payments
```

or equivalent explicit payment command.

The backend determines the resulting financial state.

---

# 54. Refund Command

Refund is a separate financial event.

Example:

```text
POST /orders/{id}/refunds
```

It must not modify the original payment record as though the payment never existed.

Historical payment and refund relationships remain preserved.

---

# 55. Cash Session Commands

Cash Session operations may include:

```text
POST /cash-sessions
POST /cash-sessions/{id}/close
POST /cash-sessions/{id}/corrections
```

Each operation has its own authorization and concurrency requirements.

---

# 56. Handover Commands

Shift handover is a business workflow.

Possible commands:

```text
POST /handovers
POST /handovers/{id}/accept
POST /handovers/{id}/confirm
POST /handovers/{id}/reject
```

The exact lifecycle is defined by the Cash Handover domain/API documents.

---

# 57. Inventory Commands

Inventory operations should represent business meaning:

```text
POST /inventory/receipts
POST /inventory/issues
POST /inventory/adjustments
POST /inventory/transfers
```

The API should not expose direct:

```text
PATCH /inventory/{id}
```

for authoritative stock quantity manipulation.

---

# 58. Recipe Commands

Recipe lifecycle may use:

```text
POST /recipes/{id}/submit
POST /recipes/{id}/approve
POST /recipes/{id}/archive
```

Historical Recipe Versions remain immutable.

---

# 59. Set Commands

Set configuration changes may use:

```text
POST /sets/{id}/versions
POST /sets/{id}/approve
POST /sets/{id}/archive
```

A Set configuration change must not silently rewrite historical Set Orders.

---

# 60. Employee Commands

Employee lifecycle may use:

```text
POST /employees/{id}/activate
POST /employees/{id}/deactivate
POST /employees/{id}/restore
```

where permitted.

Deactivation blocks new valid operations but does not erase historical attribution.

---

# 61. Permission Commands

Permission changes should use explicit operations.

Examples:

```text
PUT /employees/{id}/permissions
POST /employees/{id}/permissions/overrides
DELETE /employees/{id}/permissions/overrides/{permission}
```

Where the operation has approval or authority semantics, an explicit command may be preferred.

The server validates Manager authority.

---

# 62. Configuration Commands

Configuration operations may include:

```text
POST /configurations/{id}/approve
POST /configurations/{id}/activate
POST /configurations/{id}/archive
```

The configuration system controls:

* version;
* effective boundary;
* actor;
* approval;
* audit.

---

# 63. Command and Cash Session Boundary

Some commands depend on Cash Session context.

For example:

```text
Add Order Item
Accept Order
Payment
Cash Operation
```

The Application layer must validate the appropriate Cash Session state.

The client must not assume that an old Cash Session remains valid merely because it has a cached UUID.

---

# 64. Command and Menu Configuration

Order-related commands must use the effective menu/pricing configuration defined for the current operational context.

Existing Order Item snapshots remain authoritative for already-created items.

A current menu change must not rewrite existing Order Items.

---

# 65. Command and Inventory

Order acceptance may trigger inventory deduction.

The command must validate authoritative stock inside the transaction.

Example:

```text
POST /orders/{id}/accept
```

may execute:

```text
Order validation
      ↓
Recipe validation
      ↓
Inventory validation
      ↓
Inventory deduction
      ↓
Order state transition
      ↓
Commit
```

The API must not treat a cached stock value as final authority.

---

# 66. Command and Printing

A command such as:

```text
POST /orders/{id}/accept
```

may trigger kitchen printing.

The core command transaction must not remain open waiting for printer hardware.

Correct sequence:

```text
Order Accept
    ↓
DB Commit
    ↓
Outbox / Print Job
    ↓
Printer
```

Printer failure must not incorrectly undo the committed Order acceptance.

---

# 67. Command and Notifications

Notifications should normally be secondary effects.

Example:

```text
Refund
   ↓
DB Commit
   ↓
Notification Job
```

Notification failure must not rollback a committed refund.

---

# 68. Command and External Integrations

External API calls should not normally be part of the core business transaction.

Where integration is required:

```text
Business Command
    ↓
Authoritative Commit
    ↓
Outbox
    ↓
Integration Worker
```

The integration worker may retry safely according to the external contract.

---

# 69. Asynchronous Commands

Some commands are inherently asynchronous.

Examples:

* large report generation;
* large XLSX export;
* large file processing;
* lifecycle deletion;
* bulk processing;
* heavy reconciliation.

The API may return:

```http
202 Accepted
```

with a job identifier.

---

# 70. Synchronous Command

A command should remain synchronous when:

* execution is normally short;
* the result is required immediately;
* the operation fits the normal API latency budget;
* the transaction can complete safely.

Examples:

```text
Create Order
Add Order Item
Accept Order
Pay Order
Close Cash Session
```

subject to actual performance measurements.

---

# 71. Bulk Commands

Bulk commands may be used for bounded administrative operations.

Example:

```text
POST /employees/bulk-update
```

Bulk operations must:

* have strict item limits;
* validate each item;
* enforce authorization for each item;
* return per-item results where required;
* use bounded transactions;
* support idempotency where retryable.

---

# 72. Bulk Does Not Mean One Huge Transaction

A bulk request does not automatically represent one database transaction.

Example:

```text
100 employee changes
```

may produce:

```text
80 accepted
15 rejected
5 conflicts
```

when independent processing is appropriate.

This prevents large transactions from unnecessarily locking resources.

---

# 73. Command Batch

A command batch may contain several operations.

The API must clearly distinguish:

```text
Batch transport
```

from:

```text
Database transaction
```

A batch is not automatically atomic.

If atomicity is required, the endpoint must explicitly define that behavior.

---

# 74. Offline Commands

Trusted offline devices may execute already-authorized local operations.

The local command must retain:

```text
operation_id
device_id
employee_id
Business
Branch
created_at
entity_id
command_type
payload
```

When synchronized, the server revalidates the operation.

Offline execution does not grant permanent authority.

---

# 75. Offline Command Reconciliation

The synchronization API may return:

```text
ACCEPTED
ALREADY_PROCESSED
CONFLICT
INVALID
UNAUTHORIZED
TEMPORARY_FAILURE
```

The original operation UUID remains the idempotency identity.

Duplicate offline submission must not create duplicate financial or inventory effects.

---

# 76. Command Replay

The API must define replay behavior for commands.

For a successfully completed idempotent command:

```text
same operation
      ↓
return previous authoritative result
```

The command must not execute the business effect a second time.

---

# 77. Command Timeout

A client timeout does not prove that the command failed.

Example:

```text
Client
  ↓
POST /orders/{id}/pay
  ↓
Server commits
  ↓
Network timeout
```

The client may retry with the same idempotency key.

The server must return the authoritative existing result instead of creating another payment.

---

# 78. Command Failure Before Commit

If the command fails before commit:

```text
Transaction
   ↓
Rollback
```

No authoritative business effect should remain.

The API returns the appropriate error.

---

# 79. Command Failure After Commit

If the core transaction commits successfully but a secondary effect fails:

```text
DB Commit
   ↓
Secondary failure
```

the business state remains committed.

The system should use:

* outbox;
* retry;
* background jobs;
* reconciliation.

The API must not falsely report the core transaction as rolled back.

---

# 80. Command Result Authority

The authoritative command result is based on committed server state.

Client-side optimistic state must not become authoritative.

After a successful command, the client may update local UI immediately, but it must reconcile with the server response.

---

# 81. Command and Caching

Commands must not use cache as authoritative transaction state.

For example:

```text
POST /orders/{id}/pay
```

must validate authoritative Order/payment state.

Cache may be used for supporting reads, but not as the final financial authority.

---

# 82. Command and Database Constraints

Commands should rely on database constraints where appropriate.

Examples:

* unique payment operation;
* unique operation UUID;
* Business-scoped uniqueness;
* Branch-scoped uniqueness;
* foreign-key integrity;
* valid version relationships.

Application validation improves usability, while database constraints protect final correctness.

---

# 83. Command and Repository

The command handler should use Application/Repository abstractions.

It must not execute raw SQL directly from the API route.

Correct:

```text
API
 ↓
Use Case
 ↓
Repository
```

Not:

```text
API
 ↓
SQL
```

---

# 84. Command and Domain Services

Commands may invoke Domain Services when the operation crosses multiple aggregates or requires reusable business logic.

Examples:

* inventory deduction;
* refund calculation;
* payroll calculation;
* configuration activation;
* cash reconciliation.

The API should remain unaware of the internal Domain Service structure.

---

# 85. Command Result vs Resource Result

A command may return:

* updated resource;
* command result;
* job reference;
* operation result;
* status representation.

The response should contain only information useful to the client.

Internal Domain objects should not be serialized directly.

---

# 86. Command Status

Long-running commands should expose a status resource.

Example:

```text
POST /reports
    ↓
202
{
  "job_id": "..."
}
```

Then:

```text
GET /jobs/{job_id}
```

Possible states:

```text
PENDING
PROCESSING
COMPLETED
FAILED
CANCELLED
```

---

# 87. Command Documentation

Every command endpoint must document:

* purpose;
* actor requirements;
* Business scope;
* Branch scope;
* permission;
* subscription restrictions;
* request body;
* idempotency;
* concurrency behavior;
* possible state transitions;
* errors;
* retry behavior;
* synchronous/asynchronous behavior;
* audit behavior.

---

# 88. Command Naming Consistency

The API should use consistent business vocabulary.

For example:

```text
accept
cancel
pay
refund
approve
archive
activate
deactivate
close
adjust
transfer
submit
confirm
reject
```

The same business action must not have different names in different modules without a clear reason.

---

# 89. HTTP Method Rules

Initial rules:

| Operation                       | Method |
| ------------------------------- | ------ |
| List resource                   | GET    |
| Read resource                   | GET    |
| Create resource                 | POST   |
| Simple partial update           | PATCH  |
| Full replacement where required | PUT    |
| Explicit business command       | POST   |
| Physical deletion               | DELETE |
| Bulk operation                  | POST   |
| Async job creation              | POST   |

The exact method must reflect the public contract, not database implementation.

---

# 90. PUT Usage

PUT should be used only when the API truly supports full resource replacement semantics.

If the operation is partial or business-specific:

```text
PATCH
```

or:

```text
POST /resource/{id}/{command}
```

should be preferred.

---

# 91. DELETE Usage

DELETE should be limited to resources where physical deletion is actually valid.

It must not be used to hide:

* cancellation;
* archival;
* deactivation;
* refund;
* correction;
* historical reversal.

Those are business commands.

---

# 92. Command and Correction

Corrections are business operations.

Example:

```text
POST /cash-sessions/{id}/corrections
POST /inventory/adjustments
```

A correction should:

* preserve original state/history;
* record reason;
* identify actor;
* obey permission;
* create an audit event;
* preserve financial/inventory integrity.

It must not silently overwrite the original record.

---

# 93. Command and Approval

Approval is always an explicit business action where it changes authority or effective state.

Example:

```text
POST /recipes/{id}/approve
```

The API must validate the approver's authority independently from the original creator.

---

# 94. Command and Effective Configuration

Configuration changes that become effective at a future boundary should expose that behavior explicitly.

Example:

```text
POST /configurations/{id}/approve
```

may produce:

```json
{
  "data": {
    "status": "SCHEDULED",
    "effective_boundary": "NEXT_CASH_SESSION"
  }
}
```

The API must not imply immediate effect if the business rule defines a future effective boundary.

---

# 95. Command and Existing Orders

A menu or price command must not invalidate existing Order Items merely because current configuration changed.

Existing Order snapshots remain authoritative.

---

# 96. Command and Historical Prices

Price commands may create a new effective configuration.

They must not rewrite:

* historical Order Item prices;
* historical payments;
* historical refunds;
* historical reports.

---

# 97. Command and Historical Recipes

Recipe commands must create new versions where required.

Historical Inventory Transactions retain the Recipe Version used at the time.

---

# 98. Command and Historical Sets

Set configuration commands must preserve historical Set configuration.

A current Set configuration must not reinterpret historical Set Orders.

---

# 99. Command and Subscription Lifecycle

Subscription-related commands may include:

```text
POST /subscriptions/{id}/activate
POST /subscriptions/{id}/renew
POST /subscriptions/{id}/cancel
```

Platform-level subscription commands are restricted to authorized platform actors.

A Business cannot alter its own entitlement merely by calling a Business-level API.

---

# 100. Command and Business Deletion

Business deletion is a controlled lifecycle operation.

It must not be represented as an ordinary:

```text
DELETE /businesses/{id}
```

when deletion includes:

* 60-day lifecycle;
* notification;
* background processing;
* backup retention;
* audit;
* cascading data handling.

It should use an explicit lifecycle command.

---

# 101. Command and Data Lifecycle

Lifecycle commands may include:

```text
POST /businesses/{id}/mark-deletion-eligible
POST /businesses/{id}/start-deletion
```

Exact endpoint exposure depends on whether the operation is user-triggered or system-triggered.

Background workers may perform internal lifecycle operations without exposing them as public API commands.

---

# 102. System Commands vs User Commands

Not every internal command needs a public HTTP endpoint.

For example:

```text
Subscription expiry processor
Report generation worker
Cache invalidation worker
Deletion worker
Notification worker
```

may execute Application commands internally.

The public API should expose only capabilities that clients legitimately need.

---

# 103. Internal Command Bus

The Application layer may use an internal command abstraction.

Example:

```text
API Command
    ↓
Application Command
    ↓
Use Case
```

The HTTP endpoint must not dictate the internal command architecture.

Internal command buses are optional implementation details.

---

# 104. API Command vs Domain Command

The public API command and Domain command are related but not necessarily identical.

Example:

```text
HTTP:
POST /orders/{id}/pay

Application:
PayOrderCommand

Domain:
Order.pay(...)
PaymentService.process(...)
```

This separation prevents HTTP concepts from leaking into the Domain.

---

# 105. Endpoint Composition

An endpoint should represent one coherent client capability.

Avoid endpoints that perform unrelated business operations.

Bad:

```text
POST /orders/{id}/process
```

where the endpoint secretly:

* accepts;
* pays;
* prints;
* closes;
* archives.

Prefer explicit operations with clear boundaries.

---

# 106. Composite Business Operations

A command may legitimately perform several internal effects when they form one atomic business operation.

Example:

```text
Accept Order
```

may atomically perform:

* Order transition;
* inventory deduction;
* relevant financial/operational snapshot;
* audit;
* outbox creation.

The client still sees one coherent business command.

---

# 107. Atomicity

When multiple changes are required for one business command, the Application layer must define whether they are:

* atomic;
* independently processed;
* asynchronous.

The API contract must not imply atomicity when it does not exist.

---

# 108. Command Transaction Size

Commands should keep core transactions:

* short;
* bounded;
* deterministic.

They must not include:

* large report generation;
* XLSX creation;
* printer waiting;
* email delivery;
* long external API calls.

---

# 109. Command Performance

Initial targets:

| Operation                          |   Target |
| ---------------------------------- | -------: |
| Simple CRUD mutation p95           | ≤ 300 ms |
| Normal business command p95        | ≤ 500 ms |
| Core POS command p95               | ≤ 500 ms |
| Command authorization overhead p95 | ≤ 100 ms |
| Idempotency lookup p95             |  ≤ 50 ms |
| Version/concurrency validation p95 |  ≤ 50 ms |
| Normal command error mapping p95   |  ≤ 50 ms |

Large operations should move to asynchronous processing.

---

# 110. Command Availability

Core API availability target:

**≥ 99.9% monthly**

For financial duplicate prevention and authorization correctness:

* duplicate financial effects must be prevented;
* authorization must fail closed;
* committed state must remain recoverable.

Availability must never be achieved by weakening correctness or security.

---

# 111. Testing CRUD Endpoints

CRUD tests must verify:

* schema validation;
* authorization;
* Business scope;
* Branch scope;
* allowed fields;
* persistence;
* response contract;
* optimistic concurrency where applicable;
* audit where required;
* historical integrity.

---

# 112. Testing Command Endpoints

Command tests must verify:

* valid state transition;
* invalid state transition;
* authorization;
* subscription;
* Business scope;
* Branch scope;
* idempotency;
* duplicate request;
* concurrent requests;
* rollback;
* post-commit secondary failure;
* audit;
* historical integrity;
* retry behavior.

---

# 113. Contract Testing

Every public command must have API contract tests covering:

* HTTP method;
* path;
* request;
* response;
* status codes;
* error codes;
* idempotency;
* authorization;
* concurrency behavior where exposed.

OpenAPI must represent the public contract.

---

# 114. Security Testing

Security tests must verify:

* Business isolation;
* Branch isolation;
* permission enforcement;
* Manager authority;
* subscription restrictions;
* resource ownership;
* command enumeration;
* UUID tampering;
* unauthorized state transitions;
* replay attacks;
* idempotency-key misuse.

---

# 115. Failure Testing

Command failure scenarios must include:

* database timeout;
* deadlock;
* Redis unavailable;
* outbox failure;
* printer failure;
* notification failure;
* external API timeout;
* client timeout after commit;
* retry after unknown outcome.

The authoritative transaction must remain correct.

---

# 116. Recommended CRUD/Command Decision

Use the following decision model:

```text
Is the operation primarily a simple resource data change?
        │
       Yes
        ↓
      CRUD
        │
       No
        ↓
Does it represent business intent/state transition?
        │
       Yes
        ↓
    Command
        │
       No
        ↓
Review domain semantics before choosing endpoint
```

---

# 117. Practical Examples

### Product Name

```text
PATCH /products/{id}
```

Appropriate.

### Product Activation

```text
POST /products/{id}/activate
```

Preferred.

### Product Archive

```text
POST /products/{id}/archive
```

Preferred when historical integrity applies.

### Order Payment

```text
POST /orders/{id}/pay
```

Required.

### Order Cancellation

```text
POST /orders/{id}/cancel
```

Preferred.

### Cash Session Close

```text
POST /cash-sessions/{id}/close
```

Required.

### Recipe Approval

```text
POST /recipes/{id}/approve
```

Required.

### Inventory Adjustment

```text
POST /inventory/adjustments
```

Preferred.

---

# 118. Anti-Pattern Examples

The following are prohibited:

```text
PATCH /orders/{id}
{
  "status": "PAID"
}
```

```text
PATCH /cash-sessions/{id}
{
  "status": "CLOSED"
}
```

```text
PATCH /inventory/{id}
{
  "quantity": 0
}
```

```text
PATCH /recipes/{id}
{
  "approved": true
}
```

when these fields represent business state transitions.

The correct approach is explicit business commands.

---

# 119. Command Endpoint Guardrails

The API must not:

* hide business actions inside generic PATCH;
* trust client-provided state transitions;
* use DELETE for business cancellation;
* use DELETE to hide historical records;
* execute business logic in route handlers;
* bypass Application use cases;
* bypass Domain rules;
* bypass authorization;
* bypass idempotency for retryable commands;
* bypass concurrency controls;
* use cache as authoritative command state;
* wait for printers inside transactions;
* wait for notifications inside transactions;
* expose internal command implementation details.

---

# 120. System Invariants

The following invariants apply to CRUD and Command Endpoint Architecture:

1. The API is not a direct database CRUD interface.
2. CRUD endpoints operate through Application use cases.
3. Command endpoints operate through Application use cases.
4. API routes do not contain core business logic.
5. API routes do not directly mutate PostgreSQL.
6. Resource identity does not grant authorization.
7. Business scope is server-authoritative.
8. Branch scope is server-authoritative.
9. Client-provided state is not automatically authoritative.
10. Simple resource changes may use CRUD.
11. Important business actions use explicit commands.
12. Business state transitions are not exposed as unrestricted PATCH operations.
13. Payment is an explicit business operation.
14. Refund is an explicit business operation.
15. Cash Session closure is an explicit business operation.
16. Inventory adjustment is an explicit business operation.
17. Recipe approval is an explicit business operation.
18. Configuration approval is an explicit business operation.
19. Employee activation/deactivation is an explicit lifecycle operation where required.
20. Cancellation is not equivalent to deletion.
21. Archival is not equivalent to deletion.
22. Closing is not equivalent to deletion.
23. Physical deletion is permitted only when lifecycle rules allow it.
24. Historical resources must not be physically deleted merely for API convenience.
25. Commands express business intent.
26. The server determines whether a requested state transition is valid.
27. Client-provided totals are not authoritative.
28. Server-side pricing is authoritative.
29. Server-side inventory state is authoritative.
30. Server-side payment state is authoritative.
31. Retryable commands support idempotency.
32. Duplicate idempotent commands do not duplicate business effects.
33. Reused idempotency keys with conflicting payloads are rejected.
34. Commands validate current authoritative state.
35. Commands remain safe under concurrent requests.
36. Optimistic concurrency is used where appropriate.
37. Pessimistic locking is used only where required.
38. Database constraints remain final correctness guards.
39. Core command transactions remain short.
40. Core transactions do not wait for printer hardware.
41. Core transactions do not wait for notification delivery.
42. Core transactions do not unnecessarily wait for external APIs.
43. Secondary effects occur after successful commit where appropriate.
44. Secondary failure does not falsely rollback committed business state.
45. Audit is generated for important business commands.
46. Operation UUID is retained for important retryable commands.
47. Historical financial state remains immutable.
48. Historical Order prices are not rewritten by current configuration.
49. Historical Recipe Versions are not rewritten by current Recipes.
50. Historical Set configurations are not rewritten by current Sets.
51. Commands cannot bypass subscription restrictions.
52. READ_ONLY Businesses cannot perform prohibited mutations.
53. DELETED Businesses cannot perform normal business commands.
54. Managers cannot grant permissions beyond their authority.
55. Command authorization is server-side.
56. Frontend command visibility is not authorization.
57. Command availability depends on current resource and operational state.
58. Resource UUIDs cannot be used to cross Business boundaries.
59. Resource UUIDs cannot be used to cross Branch boundaries.
60. Explicit command endpoints use business-oriented verbs.
61. Generic command endpoints are used only when domain semantics justify them.
62. HTTP methods remain semantically consistent.
63. PUT is not used as a disguised business command.
64. DELETE is not used to represent cancellation or archival.
65. Bulk operations are bounded.
66. Bulk requests do not automatically imply one huge database transaction.
67. Asynchronous commands return a job/status reference.
68. Long-running operations do not block normal POS API requests unnecessarily.
69. Offline commands preserve stable operation identity.
70. Offline commands are revalidated by the server during synchronization.
71. Offline retries do not duplicate financial or inventory effects.
72. Command timeouts do not imply business failure.
73. Client retries use the same idempotency identity.
74. Authoritative command results come from committed server state.
75. Cache is never command authority.
76. Read models are derived representations.
77. Read models do not become financial authority.
78. Command response contracts expose only authorized data.
79. Internal Domain objects are not serialized directly.
80. Command contracts are documented in OpenAPI.
81. CRUD contracts are documented in OpenAPI.
82. Contract tests cover public CRUD operations.
83. Contract tests cover public command operations.
84. Security tests cover command authorization.
85. Concurrency tests cover important commands.
86. Failure tests cover uncertain commit outcomes.
87. Performance targets exist for CRUD and command operations.
88. Core POS commands target p95 ≤ 500 ms under normal conditions.
89. Normal business commands target p95 ≤ 500 ms under normal conditions.
90. Authorization overhead target remains within defined API SLO.
91. Idempotency lookup target remains within defined API SLO.
92. Version/concurrency validation remains bounded.
93. Large commands use asynchronous processing where appropriate.
94. Commands do not expose database implementation details.
95. Command naming remains consistent across modules.
96. Business vocabulary remains consistent across API contracts.
97. One public command represents one coherent client business capability.
98. Composite internal effects are allowed when they form one atomic business operation.
99. Atomicity behavior is explicitly defined.
100. Batch transport is not automatically database atomicity.
101. Corrections preserve original historical records.
102. Approval preserves creator and approver identity.
103. Configuration changes preserve version history.
104. Effective configuration boundaries are explicit.
105. Existing Orders are not invalidated by unrelated current configuration changes.
106. Menu changes do not rewrite existing Order snapshots.
107. Price changes do not rewrite historical financial transactions.
108. Recipe changes do not rewrite historical inventory deductions.
109. Set changes do not rewrite historical Set Orders.
110. Subscription lifecycle commands preserve historical subscription state.
111. Business deletion is controlled by lifecycle architecture.
112. System-internal commands do not need public HTTP endpoints unless clients require them.
113. API command design remains independent from internal command-bus implementation.
114. Domain logic remains independent from HTTP.
115. Application transaction ownership remains independent from HTTP route implementation.
116. Repository access remains independent from HTTP.
117. Command behavior remains deterministic under retries.
118. Command behavior remains safe under concurrent execution.
119. API design favors explicit business intent over generic state mutation.
120. The simplest endpoint that preserves correctness, security and business meaning is preferred.

---

# 121. Related Documents

### API

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/13_API_POS_and_Order_Endpoints.md`
* `docs/04_Architecture/09_API/14_API_Payment_Cash_and_Financial_Endpoints.md`
* `docs/04_Architecture/09_API/15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`
* `docs/04_Architecture/09_API/16_API_Employee_Attendance_and_Payroll_Endpoints.md`
* `docs/04_Architecture/09_API/17_API_Report_File_and_Notification_Endpoints.md`
* `docs/04_Architecture/09_API/18_API_Configuration_and_Subscription_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/06_Backend/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend

* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/26_Frontend_Error_Handling_and_Recovery_Architecture.md`

### System Analysis

* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/11_Inventory_and_Warehouse.md`
* `docs/02_System_Analysis/12_Products_and_Recipes.md`
* `docs/02_System_Analysis/13_Menu_and_Pricing.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 122. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `12_API_CRUD_and_Command_Endpoint_Architecture.md`

**Previous Document:** `11_API_Pagination_Search_Filtering_and_Sorting.md`

**Next Document:** `13_API_POS_and_Order_Endpoints.md`

---

## Final Principle

> CRUD describes resource management; commands describe business intent. The API must use the simplest contract that preserves domain rules, authorization, concurrency, idempotency, auditability and historical integrity.

