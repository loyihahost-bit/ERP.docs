# API Payment, Cash and Financial Endpoints

**Document ID:** API-14
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the API contract architecture for payment, cash, refund and other core financial operations in FastFood ERP.

The purpose is to provide explicit, secure and idempotent API contracts for:

* Order payment;
* payment methods;
* payment records;
* payment state;
* refunds;
* refund approval;
* Cash Register operations;
* Cash Session opening;
* Cash Session closing;
* cash discrepancy;
* cash correction;
* shift handover;
* cash transfer;
* financial snapshots;
* financial corrections;
* financial history;
* offline financial boundaries;
* concurrency;
* duplicate financial operation prevention;
* auditability;
* historical integrity.

Financial API operations are among the most security-sensitive operations in the system.

The API must therefore prioritize:

1. financial correctness;
2. duplicate prevention;
3. authorization;
4. historical integrity;
5. concurrency safety;
6. auditability;
7. predictable recovery.

Performance remains important, but performance must never weaken financial correctness.

---

# 2. Scope

This document covers:

* Payment API;
* payment methods;
* payment creation;
* payment state;
* payment amount validation;
* Order financial finalization;
* refund API;
* refund authorization;
* refund approval;
* Cash Register API;
* Cash Session API;
* opening Cash Session;
* closing Cash Session;
* expected cash;
* actual cash;
* discrepancy;
* cash correction;
* shift handover;
* incoming/outgoing cashier confirmation;
* cash transfer;
* financial snapshots;
* financial corrections;
* financial audit;
* offline payment boundaries;
* idempotency;
* concurrency;
* retry safety;
* financial API errors;
* financial performance;
* financial observability;
* financial invariants.

Generic API behavior remains defined by:

* `06_API_Authentication_and_Request_Context.md`
* `07_API_Authorization_and_Scope_Enforcement.md`
* `09_API_Error_Handling_and_Error_Codes.md`
* `10_API_Idempotency_and_Concurrency.md`
* `12_API_CRUD_and_Command_Endpoint_Architecture.md`

---

# 3. Financial API Boundary

The financial API sits between the client and the Application layer:

```text
Client
   ↓
API
   ↓
Authentication
   ↓
Authorization
   ↓
Financial Validation
   ↓
Application Use Case
   ↓
Financial Domain
   ↓
Order / Cash / Payment / Refund
   ↓
PostgreSQL Transaction
   ↓
Audit / Outbox
   ↓
Commit
```

The API must not directly modify:

* payment tables;
* Cash Session balances;
* Order financial state;
* refund state;
* discrepancy state.

---

# 4. Financial Authority

The authoritative financial state is stored in PostgreSQL.

The following are authoritative:

```text
Payment Transactions
Refund Transactions
Cash Sessions
Cash Movements
Cash Handover Records
Financial Snapshots
Financial Corrections
Immutable Audit Records
```

The following are not authoritative:

```text
Frontend calculated totals
Browser state
Redis cache
Local POS cache
Client-side payment status
Printer state
Notification state
```

---

# 5. Financial Security Principle

Every financial mutation must validate:

* authenticated employee;
* employee status;
* Business;
* Branch;
* permission;
* subscription entitlement;
* Order state where applicable;
* Cash Session state where applicable;
* Device restrictions where applicable;
* operation idempotency;
* concurrency.

The API must fail closed when authoritative authorization cannot be established.

---

# 6. Payment Resource

A Payment represents an authoritative financial transaction associated with an Order.

Conceptually:

```json
{
  "id": "018f...",
  "order_id": "018f...",
  "method": "CASH",
  "amount": "75000.00",
  "status": "COMPLETED",
  "created_at": "2026-10-07T09:00:00Z"
}
```

The exact financial representation is defined by the Database layer.

---

# 7. Supported Payment Methods

The initial API may support:

```text
CASH
CARD
```

Additional payment methods may be introduced later.

Payment method values are controlled enums.

Clients must not invent payment method identifiers.

---

# 8. Payment Endpoint

Primary endpoint:

```http
POST /api/v1/orders/{order_id}/payments
```

Example:

```json
{
  "method": "CASH",
  "amount": "75000.00"
}
```

The server determines whether the requested payment is valid.

---

# 9. Payment Amount Authority

The client-provided amount is an input.

It is not authoritative.

The server validates the payment amount against:

* current authoritative Order financial state;
* already completed payments;
* discounts;
* refunds where applicable;
* payment rules;
* currency;
* Order state.

The server determines the remaining payable amount.

---

# 10. Payment Amount Example

If:

```text
Order Total = 75,000
Already Paid = 25,000
```

then:

```text
Remaining = 50,000
```

A payment request for 100,000 must not silently overpay the Order unless an explicit business rule supports that behavior.

---

# 11. Payment Idempotency

Payment creation must always be idempotent.

Example:

```http
POST /api/v1/orders/{order_id}/payments
Idempotency-Key: 018f-payment-operation
```

If the client retries the request:

```text
Same operation
→ Same authoritative result
```

The backend must not create a second payment.

---

# 12. Payment Duplicate Prevention

The system must protect against duplicate payment caused by:

* double-click;
* network retry;
* timeout;
* client retry;
* browser refresh;
* offline synchronization;
* concurrent POS devices.

The same operation UUID must never create multiple financial effects.

---

# 13. Payment State

Payment states may include:

```text
PENDING
COMPLETED
FAILED
CANCELLED
REFUNDED
PARTIALLY_REFUNDED
```

The exact state machine is owned by the financial Domain.

Clients cannot arbitrarily set payment status.

---

# 14. Payment Completion

A Payment becomes financially authoritative only after the server commits the corresponding transaction.

The API must not report:

```text
COMPLETED
```

before the authoritative financial transaction is committed.

---

# 15. Payment and Order State

Successful payment may transition the Order to a finalized/paid state according to Domain rules.

Conceptually:

```text
Payment Completed
        ↓
Order Financial State Updated
        ↓
Order Finalized
```

The exact lifecycle remains controlled by the Order Domain.

---

# 16. Payment and Order Separation

The following states must remain conceptually distinct:

```text
Order Accepted
Order Paid
Payment Created
Payment Completed
Order Finalized
```

One must not be inferred from another without Domain rules.

---

# 17. Payment Read Endpoint

Primary endpoint:

```http
GET /api/v1/orders/{order_id}/payments
```

The response may include:

* Payment UUID;
* method;
* amount;
* status;
* created timestamp;
* actor;
* Cash Session where applicable.

Sensitive payment metadata must be filtered according to authorization.

---

# 18. Payment Detail Endpoint

```http
GET /api/v1/payments/{payment_id}
```

The server validates that the requesting actor may access the Payment.

A Payment UUID alone does not grant access.

---

# 19. Payment History

Where required:

```http
GET /api/v1/orders/{order_id}/payments/history
```

Historical financial records must be immutable.

Corrections are represented as new financial events rather than silently rewriting old records.

---

# 20. Payment Cancellation

A completed Payment must not be deleted.

If a payment needs reversal, the system uses an explicit financial operation such as:

```text
Refund
Correction
Reversal
```

The exact operation depends on the business rule.

---

# 21. Payment Deletion Prohibition

The API must not expose:

```http
DELETE /api/v1/payments/{id}
```

as a normal business operation.

Historical financial transactions must remain reconstructable.

---

# 22. Partial Payments

If the business allows partial payment, the API may accept multiple payments against one Order.

Example:

```text
Order = 100,000

Payment A = 40,000
Payment B = 60,000
```

The server validates the cumulative financial state.

If partial payment is not permitted by the configured business rule, the API rejects it.

---

# 23. Multiple Payment Methods

If supported, an Order may have multiple completed payments.

Example:

```text
Cash = 40,000
Card = 60,000
Total = 100,000
```

The financial Domain must enforce the configured payment policy.

---

# 24. Overpayment

Overpayment behavior must be explicit.

The default rule is:

```text
Completed Payments
≤
Authoritative Payable Amount
```

The API rejects unsupported overpayment.

If a future payment provider requires a different settlement model, that behavior must be explicitly modeled.

---

# 25. Currency

Financial API amounts must use the system-defined Business currency.

Money must use a deterministic decimal representation.

Example:

```json
{
  "amount": "75000.00"
}
```

Floating-point financial values must not be treated as authoritative.

---

# 26. Payment Precision

The API must standardize:

* decimal precision;
* scale;
* rounding;
* currency.

The client must not decide authoritative rounding behavior.

---

# 27. Payment Concurrency

Two concurrent payment requests against the same Order must be serialized or otherwise protected.

Example:

```text
Order Remaining = 50,000

Request A = 50,000
Request B = 50,000

Result:
A → SUCCESS
B → REJECTED / ALREADY PAID
```

The system must not allow total completed payments to exceed the authoritative payable amount.

---

# 28. Payment Transaction Boundary

The core payment transaction may include:

```text
Validate Order
      ↓
Validate Payment State
      ↓
Validate Amount
      ↓
Validate Cash Session where required
      ↓
Create Payment
      ↓
Update Order Financial State
      ↓
Create Audit / Outbox
      ↓
Commit
```

External integrations must not unnecessarily hold this transaction open.

---

# 29. Cash Payment

For:

```text
method = CASH
```

the payment must be associated with the appropriate:

* Branch;
* Cash Register;
* Cash Session;
* cashier context.

A Cash Payment must not be attached to an unrelated Cash Session.

---

# 30. Card Payment

For:

```text
method = CARD
```

the API may record the payment transaction without requiring the system to become a card processor.

External payment terminal integration, if introduced, belongs to the external integration boundary.

The API must still preserve the authoritative internal payment state.

---

# 31. External Payment Provider Boundary

If an external payment provider is introduced:

```text
POS
 ↓
Payment API
 ↓
Payment Application Service
 ↓
Provider Integration
```

The API must not expose provider-specific implementation details unnecessarily.

Provider failures must be mapped into stable API errors.

---

# 32. External Payment Timeout

If an external payment operation times out and the final provider state is uncertain, the system must not blindly create a second payment.

The operation must use:

* provider transaction ID where applicable;
* internal operation UUID;
* idempotency;
* reconciliation.

The generic external integration architecture remains authoritative.

---

# 33. Payment Receipt

After successful payment, a receipt/financial document may be generated asynchronously.

Receipt generation must not rollback a committed Payment.

---

# 34. Refund Resource

A Refund represents an authorized reversal of previously completed financial value.

Conceptually:

```json
{
  "id": "018f...",
  "order_id": "018f...",
  "payment_id": "018f...",
  "amount": "25000.00",
  "reason": "Incorrect order",
  "status": "COMPLETED"
}
```

---

# 35. Refund Endpoint

Primary endpoint:

```http
POST /api/v1/orders/{order_id}/refunds
```

Example:

```json
{
  "amount": "25000.00",
  "reason": "Incorrect order"
}
```

The server validates the refund against historical financial state.

---

# 36. Refund Permission

Refund requires explicit permission.

The API validates:

* employee status;
* Business scope;
* Branch scope;
* refund permission;
* subscription entitlement;
* Order state;
* payment state;
* refund limits.

Frontend visibility is not authorization.

---

# 37. Refund Approval

Where business rules require approval, the refund may enter:

```text
PENDING_APPROVAL
```

before becoming financially effective.

An unauthorized employee must not bypass approval through a direct API request.

---

# 38. Refund Approval Endpoint

Where required:

```http
POST /api/v1/refunds/{refund_id}/approve
```

Approval validates:

* approver identity;
* permission;
* Branch scope;
* approval policy;
* current refund state.

Approval itself is auditable.

---

# 39. Refund Rejection

Where approval workflow exists:

```http
POST /api/v1/refunds/{refund_id}/reject
```

A rejection must preserve the request history.

The rejected refund must not be treated as a completed financial reversal.

---

# 40. Refund Amount

The server validates:

```text
Total Refunded
≤
Total Completed Payment
```

unless an explicit business rule defines another model.

Current Product price must never be used to calculate historical refund value.

---

# 41. Refund Historical Authority

Refund calculations use:

* original Payment;
* original Order financial snapshot;
* previous Refunds;
* authoritative financial history.

Current Product price is irrelevant to the historical refund calculation.

---

# 42. Refund Idempotency

Refund creation must be idempotent.

Repeated requests using the same operation UUID must return the original authoritative result rather than creating another refund.

---

# 43. Refund Concurrency

Concurrent refund requests must be protected.

Example:

```text
Paid = 100,000

Refund A = 70,000
Refund B = 70,000

Result:
Only one combination within the refundable amount is accepted.
```

The system must never allow total refunds to exceed the refundable amount.

---

# 44. Refund Read Endpoint

```http
GET /api/v1/orders/{order_id}/refunds
```

The response may include:

* refund ID;
* amount;
* status;
* reason;
* requester;
* approver;
* timestamps.

---

# 45. Refund Detail Endpoint

```http
GET /api/v1/refunds/{refund_id}
```

Access is controlled by Business, Branch and permission scope.

---

# 46. Refund Deletion Prohibition

Refunds must never be physically deleted through a normal API endpoint.

Corrections create new financial records.

---

# 47. Cash Register Resource

The Cash Register represents the physical/logical cash point associated with a Branch.

Initial business model:

```text
Branch
   ↓
Cash Register
   ↓
Cash Sessions
```

The current operational model assumes one register per Branch.

The API must not prevent future multiple-register support.

---

# 48. Cash Register Read

```http
GET /api/v1/cash-registers
```

or:

```http
GET /api/v1/branches/{branch_id}/cash-registers
```

The response may include:

* register ID;
* Branch;
* status;
* active Cash Session.

---

# 49. Cash Register Isolation

A Cash Register belongs to one Branch.

The API must reject attempts to:

* use another Branch's register;
* open a session on an unauthorized register;
* attach a payment to an unrelated register.

---

# 50. Cash Session Resource

A Cash Session represents one cashier's operational cash period.

Conceptually:

```json
{
  "id": "018f...",
  "cash_register_id": "018f...",
  "branch_id": "018f...",
  "cashier_id": "018f...",
  "status": "OPEN",
  "opened_at": "2026-10-07T08:00:00Z"
}
```

---

# 51. Cash Session States

Initial states:

```text
OPEN
CLOSING
CLOSED
```

The exact state machine is controlled by the Domain.

A closed Cash Session cannot be reopened through the normal API.

---

# 52. Open Cash Session

Primary endpoint:

```http
POST /api/v1/cash-sessions
```

Example:

```json
{
  "cash_register_id": "018f...",
  "opening_cash": "500000.00"
}
```

The server validates:

* Branch;
* register;
* employee;
* permissions;
* existing active session;
* subscription;
* device;
* opening amount.

---

# 53. One Active Session

The current business model expects one active Cash Session per operational register.

The database and Domain must enforce the relevant uniqueness rule.

Two concurrent open-session requests must not create two active sessions for the same register.

---

# 54. Opening Cash

The opening cash amount becomes part of the Cash Session financial snapshot.

It must not be silently changed after the session starts.

If correction is permitted, it must use an explicit correction workflow.

---

# 55. Cash Session Read

```http
GET /api/v1/cash-sessions/{session_id}
```

The response may include:

* session state;
* cashier;
* register;
* opening amount;
* cash sales;
* cash refunds;
* handovers;
* expected cash;
* actual cash where available;
* discrepancy;
* timestamps.

Sensitive information must be filtered according to permission.

---

# 56. Active Cash Session

POS may use:

```http
GET /api/v1/cash-sessions/active
```

The server resolves the active session for the authenticated operational context.

The client must not use an arbitrary Cash Session UUID to impersonate another cashier's session.

---

# 57. Cash Session and Order

Applicable Orders created through POS must be associated with the relevant Cash Session.

The association must remain historically identifiable.

An Order cannot silently move between Cash Sessions.

---

# 58. Cash Session and Payment

Cash Payments must be associated with the Cash Session that accepted the payment.

This enables:

* cashier reporting;
* cash reconciliation;
* discrepancy calculation;
* shift handover.

---

# 59. Cash Session Closing

Primary endpoint:

```http
POST /api/v1/cash-sessions/{session_id}/close
```

Example:

```json
{
  "actual_cash": "1235000.00",
  "comment": "End of shift"
}
```

The server calculates expected cash from authoritative financial state.

The client-provided actual cash is the counted physical amount.

---

# 60. Expected Cash

Expected cash is derived from authoritative Cash Session activity.

Conceptually:

```text
Opening Cash
+ Cash Sales
+ Cash In
- Cash Refunds
- Cash Out
± Other Authorized Cash Movements
=
Expected Cash
```

The exact calculation is owned by the financial Domain.

The client must not submit `expected_cash` as authoritative.

---

# 61. Actual Cash

Actual cash represents the physical cash counted by the cashier.

The API records the reported amount.

The server compares:

```text
Actual Cash
vs
Expected Cash
```

---

# 62. Cash Discrepancy

Conceptually:

```text
Discrepancy = Actual Cash - Expected Cash
```

The server calculates the authoritative discrepancy.

Example:

```text
Expected = 1,000,000
Actual   =   980,000

Discrepancy = -20,000
```

---

# 63. Discrepancy Comment

When required by policy, a closing discrepancy may require a comment.

The API validates required fields before closing the session.

---

# 64. Cash Shortage Notification

A shortage may trigger an asynchronous notification to:

* Owner;
* authorized Manager;
* responsible previous cashier where applicable.

Notification failure must not rollback Cash Session closure.

---

# 65. Cash Surplus

A surplus must also be recorded.

The system should preserve:

* expected;
* actual;
* difference;
* actor;
* timestamp;
* comment.

A surplus must not be silently discarded.

---

# 66. Closed Cash Session

After successful closure:

```text
OPEN
 ↓
CLOSED
```

The session cannot be reopened through the normal endpoint.

Historical session state remains immutable except through authorized correction mechanisms.

---

# 67. Cash Session Reopen

The API must not expose a normal:

```http
POST /cash-sessions/{id}/reopen
```

operation.

If reopening is ever required, it must be a privileged correction workflow with:

* explicit authority;
* reason;
* audit;
* controlled limits;
* concurrency protection.

---

# 68. Cash Correction

A correction endpoint may be provided for authorized financial corrections.

Example:

```http
POST /api/v1/cash-sessions/{session_id}/corrections
```

Example:

```json
{
  "amount": "-20000.00",
  "reason": "Incorrect closing count"
}
```

The exact correction semantics must be defined by the financial Domain.

---

# 69. Correction Does Not Rewrite History

A correction must not modify the original:

* Payment;
* Cash Session closing;
* cash movement;
* refund;
* discrepancy record.

Instead:

```text
Original Financial Event
        +
Correction Event
        ↓
Reconstructed Financial State
```

---

# 70. Correction Permission

Financial corrections require explicit permission.

The server validates:

* employee;
* Branch;
* scope;
* correction permission;
* correction limit;
* session state;
* subscription;
* reason.

---

# 71. Correction Limits

Where a correction-count limit is configured, the API must enforce it server-side.

Example business rule:

```text
Maximum normal corrections = 3
```

After the configured limit, a privileged workflow may be required.

The client must not bypass the counter.

---

# 72. Privileged Reopen/Correction

If a privileged correction is required after the normal correction limit:

```http
POST /api/v1/cash-sessions/{session_id}/privileged-correction
```

The exact endpoint name may be refined during implementation.

It must require:

* elevated permission;
* reason;
* actor identity;
* audit;
* current state validation.

---

# 73. Shift Handover

Cash handover transfers operational responsibility between cashiers.

The workflow may involve:

```text
Outgoing Cashier
        ↓
Count Cash
        ↓
Handover Record
        ↓
Incoming Cashier
        ↓
Confirm Cash
        ↓
New Cashier Context
```

The dedicated data model is defined in:

`17_Shift_Handover_Data_Model.md`

---

# 74. Create Handover

Primary endpoint:

```http
POST /api/v1/cash-sessions/{session_id}/handover
```

Example:

```json
{
  "transferred_cash": "850000.00"
}
```

The server validates:

* outgoing cashier;
* active session;
* Branch;
* register;
* actual cash;
* permission;
* session state.

---

# 75. Incoming Cashier Confirmation

Incoming cashier must authenticate under their own employee identity.

Example:

```http
POST /api/v1/handovers/{handover_id}/accept
```

The request may include:

```json
{
  "counted_cash": "850000.00"
}
```

The server compares the count with the handover amount.

---

# 76. Handover Confirmation

The incoming cashier must not automatically inherit the outgoing cashier's identity.

The handover must preserve:

```text
Outgoing Employee
Incoming Employee
Device context
Cash amount
Timestamp
Confirmation result
```

---

# 77. Handover Mismatch

If:

```text
Outgoing = 850,000
Incoming = 820,000
```

the API records a mismatch.

The system may require:

* recount;
* confirmation;
* discrepancy handling;
* notification.

The API must not silently accept the mismatch as zero difference.

---

# 78. Recount

Where the workflow requires recount:

```http
POST /api/v1/handovers/{handover_id}/recount
```

The new count is recorded as a new event/attempt.

The previous count must remain historically visible.

---

# 79. Handover Finalization

Once the incoming cashier confirms the correct amount:

```text
Handover
→ ACCEPTED
```

The new cashier becomes the operational owner of the subsequent Cash Session context according to Domain rules.

---

# 80. Handover Cancellation

A handover that has not yet been accepted may be cancelled if business rules permit.

Accepted historical handovers must not be deleted.

---

# 81. Cash Handover and Session Boundaries

The API must preserve the distinction between:

```text
Cash Session
Cashier Shift
Handover
```

A handover must not silently rewrite historical Cash Session records.

---

# 82. Cash Movement

Where explicit cash movements are supported, the API may expose:

```http
POST /api/v1/cash-sessions/{session_id}/movements
```

Examples:

```text
CASH_IN
CASH_OUT
```

Each movement must contain:

* amount;
* reason;
* actor;
* timestamp;
* session;
* Branch;
* operation UUID.

---

# 83. Cash Movement Authorization

Cash movements require explicit permission.

The API must not allow arbitrary employee-created cash movements without authorization.

---

# 84. Cash Movement History

Cash movements are immutable financial events.

A correction creates a new event rather than rewriting the original movement.

---

# 85. Financial Correction Resource

Financial corrections should have an explicit resource where needed.

Conceptually:

```json
{
  "id": "018f...",
  "type": "CASH_CORRECTION",
  "amount": "-20000.00",
  "reason": "Incorrect count",
  "status": "COMPLETED"
}
```

The resource remains auditable.

---

# 86. Correction Endpoint

Generic correction:

```http
POST /api/v1/financial-corrections
```

The implementation should prefer specialized commands where the correction affects a known domain such as:

* Cash Session;
* Payment;
* Refund;
* Order.

Generic financial correction must not become a mechanism for bypassing Domain rules.

---

# 87. Financial History

Authorized users may access financial history through dedicated read endpoints.

Examples:

```http
GET /api/v1/cash-sessions/{id}/movements
GET /api/v1/orders/{id}/payments
GET /api/v1/orders/{id}/refunds
GET /api/v1/financial-corrections
```

All results remain scope-controlled.

---

# 88. Financial Reports

Detailed financial reporting belongs to the Reporting API.

This financial API provides authoritative transactional data required by reporting.

Report generation must not modify financial state.

---

# 89. Cash Session Report

A lightweight operational report may be available:

```http
GET /api/v1/cash-sessions/{session_id}/summary
```

It may include:

* opening cash;
* cash sales;
* cash refunds;
* cash movements;
* expected cash;
* actual cash;
* discrepancy.

Large historical reports belong to the Reporting API.

---

# 90. Financial Snapshot

The system should preserve the financial snapshot relevant to the transaction.

Examples include:

* Order amount;
* Payment amount;
* Discount;
* Refund;
* Cash discrepancy.

Historical snapshots must remain reconstructable.

---

# 91. Current Price Is Not Financial History

The API must never calculate a historical refund or financial correction using the current Product price.

Historical financial state is authoritative.

---

# 92. Financial State Immutability

The following must not be silently overwritten:

```text
Payment
Refund
Cash Session closing
Cash movement
Financial correction
Historical Order amount
```

Corrections are additive historical events.

---

# 93. Payment and Refund Relationship

A Refund must reference the historical financial transaction it reverses.

Where applicable:

```text
Refund
 ↓
Payment
 ↓
Order
```

This allows financial reconstruction.

---

# 94. Refund and Multiple Payments

If an Order contains multiple Payments, refund allocation must be explicit.

The server must determine which Payment(s) can support the requested Refund.

The client must not arbitrarily rewrite historical Payment relationships.

---

# 95. Financial Operation Context

Important financial operations should preserve:

```text
Business
Branch
Employee
Device
Cash Register
Cash Session
Order
Payment / Refund / Correction
Operation UUID
Request ID
Timestamp
```

Only applicable fields need to be recorded.

---

# 96. Offline Payment Boundary

Offline financial operations require special restrictions.

A trusted device may perform offline financial operations only when explicitly allowed by offline authorization.

The default design should minimize offline financial risk.

---

# 97. Offline Cash Payment

Where offline cash payment is permitted:

```text
Local Payment
    ↓
Local Financial Snapshot
    ↓
Sync Queue
    ↓
Server Validation
```

The operation must have a stable operation UUID.

Duplicate replay must not create duplicate Payment records.

---

# 98. Offline Card Payment

Offline card operations should generally require an external terminal/provider capability that can establish payment independently.

The ERP API must not treat:

```text
Client says "CARD PAID"
```

as sufficient proof of payment.

---

# 99. Offline Refund

Offline Refund should normally be restricted unless the security/business model explicitly authorizes it.

Refunds are higher-risk than normal Order creation.

If offline Refund is permitted, it must have:

* explicit offline capability;
* strict authorization;
* stable operation UUID;
* server reconciliation;
* historical audit.

---

# 100. Synchronization of Financial Operations

Financial synchronization must preserve:

```text
Original operation UUID
Original client context
Original transaction snapshot
Server result
Conflict state
```

The server remains authoritative.

---

# 101. Financial Synchronization Conflict

Possible results:

```text
ACCEPTED
ALREADY_PROCESSED
CONFLICT
REJECTED
TEMPORARY_FAILURE
```

A conflict must not be resolved by silently creating another financial transaction.

---

# 102. Payment Synchronization Example

```text
Offline Payment
    ↓
Operation UUID = X
    ↓
Network retry
    ↓
Same Operation UUID = X
    ↓
Server detects existing operation
    ↓
Original Payment result returned
```

No duplicate Payment is created.

---

# 103. Financial API and Subscription

When the Business is `READ_ONLY`:

* new financial mutations are blocked;
* historical financial reads remain available according to permissions;
* allowed reports/exports remain available.

Offline authorization cannot bypass subscription restrictions.

---

# 104. Deleted Business

Financial operations for a deleted Business must be rejected.

Old offline financial operations must not resurrect or modify deleted Business data.

---

# 105. Financial Authorization

Authorization should distinguish:

```text
View Financial Data
Create Payment
Create Refund
Approve Refund
Close Cash Session
Create Cash Movement
Create Correction
Approve Privileged Correction
View Other Cashier Sessions
```

These permissions should not be collapsed into one unrestricted financial permission.

---

# 106. Manager Financial Authority

Manager permissions remain limited by the general permission model.

A Manager may perform only financial actions explicitly granted to them.

A Manager cannot grant themselves additional financial authority.

---

# 107. Cashier Financial Authority

Cashier permissions may include:

* accepting cash payments;
* operating active Cash Session;
* closing own session;
* handover participation.

Other financial actions such as refunds/corrections require explicit permissions.

---

# 108. Owner Financial Authority

Owner may have broad financial visibility and management authority according to Business configuration.

Owner authority remains subject to:

* Business scope;
* subscription;
* system-level restrictions;
* audit requirements.

---

# 109. Cross-Branch Financial Access

Cross-Branch financial access requires explicit authority.

A Branch-scoped employee must not read or modify another Branch's:

* Payments;
* Refunds;
* Cash Sessions;
* Cash movements;
* corrections.

---

# 110. Financial Concurrency

Financial operations must use appropriate concurrency controls.

Possible mechanisms:

* optimistic versioning;
* database row locks;
* unique constraints;
* idempotency records;
* transaction isolation.

Redis must not be the sole correctness mechanism.

---

# 111. Cash Session Concurrency

Opening/closing/handover operations must prevent race conditions such as:

```text
Two cashiers opening same register
Two users closing same session
Two users accepting same handover
```

Only one valid authoritative transition may succeed.

---

# 112. Financial Idempotency Storage

The system must retain sufficient information to identify processed financial operations.

The stored record may include:

```text
Operation UUID
Business
Branch
Actor
Device
Operation Type
Request Hash
Result Reference
Status
Created At
Completed At
```

The exact schema is defined in the Database architecture.

---

# 113. Conflicting Idempotency Key

If the same operation UUID is reused with a materially different payload:

```text
409 Conflict
```

The API must not execute the second payload.

---

# 114. Uncertain Commit

If the client times out after sending a payment but before receiving the response, it must retry using the same idempotency key.

The server returns the original authoritative result if the transaction already committed.

This prevents:

```text
Timeout
→ Blind retry
→ Duplicate Payment
```

---

# 115. Database Failure

If the authoritative financial transaction fails before commit:

```text
Payment
→ Not committed
→ Error returned
```

No secondary success event may be published as if payment succeeded.

---

# 116. Secondary Failure After Commit

If the financial transaction commits but:

* notification fails;
* receipt generation fails;
* analytics event fails;

the financial transaction remains successful.

Secondary processing is retried asynchronously.

---

# 117. Financial Audit

Important financial mutations must create audit records.

Examples:

* Payment;
* Refund;
* Refund approval;
* Cash Session open;
* Cash Session close;
* cash movement;
* discrepancy;
* correction;
* privileged correction;
* handover.

Audit records must be immutable.

---

# 118. Financial Audit Context

Audit events should include:

```text
Event UUID
Business UUID
Branch UUID
Employee UUID
Device UUID
Cash Session UUID
Order UUID
Payment/Refund/Correction UUID
Operation UUID
Previous State
New State
Amount where appropriate
Reason
Timestamp
Result
```

Sensitive payment secrets must never be logged.

---

# 119. Financial Error Codes

Financial-specific error codes may include:

```text
PAYMENT_AMOUNT_INVALID
PAYMENT_ALREADY_COMPLETED
PAYMENT_NOT_ALLOWED
ORDER_NOT_PAYABLE
ORDER_ALREADY_PAID
PAYMENT_NOT_FOUND
PAYMENT_LIMIT_EXCEEDED
REFUND_AMOUNT_INVALID
REFUND_LIMIT_EXCEEDED
REFUND_NOT_ALLOWED
REFUND_APPROVAL_REQUIRED
REFUND_ALREADY_COMPLETED
REFUND_ALREADY_REJECTED
CASH_REGISTER_NOT_FOUND
CASH_REGISTER_BRANCH_MISMATCH
CASH_SESSION_ALREADY_OPEN
CASH_SESSION_NOT_FOUND
CASH_SESSION_CLOSED
CASH_SESSION_NOT_CLOSABLE
CASH_DISCREPANCY_REQUIRES_COMMENT
CASH_CORRECTION_NOT_ALLOWED
CORRECTION_LIMIT_EXCEEDED
PRIVILEGED_CORRECTION_REQUIRED
HANDOVER_NOT_FOUND
HANDOVER_ALREADY_ACCEPTED
HANDOVER_ALREADY_REJECTED
HANDOVER_AMOUNT_MISMATCH
CASH_MOVEMENT_NOT_ALLOWED
FINANCIAL_VERSION_CONFLICT
FINANCIAL_OPERATION_ALREADY_PROCESSED
OFFLINE_FINANCIAL_OPERATION_NOT_ALLOWED
FINANCIAL_SYNC_CONFLICT
```

Generic API error semantics remain defined by:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 120. Financial Retry Rules

Typical behavior:

```text
Network timeout
→ Retry with same idempotency key

503
→ Retry with bounded backoff

Payment already completed
→ Return authoritative result

Refund limit exceeded
→ Do not retry blindly

Cash Session closed
→ User action required

Financial version conflict
→ Refresh and resolve

Temporary synchronization failure
→ Retry later
```

---

# 121. Financial API Performance

Initial targets:

| Operation                  |   Target |
| -------------------------- | -------: |
| Payment creation p95       | ≤ 500 ms |
| Payment read p95           | ≤ 200 ms |
| Refund creation p95        | ≤ 500 ms |
| Refund read p95            | ≤ 200 ms |
| Cash Session open p95      | ≤ 400 ms |
| Cash Session close p95     | ≤ 500 ms |
| Cash movement p95          | ≤ 400 ms |
| Handover creation p95      | ≤ 400 ms |
| Handover confirmation p95  | ≤ 400 ms |
| Financial summary read p95 | ≤ 300 ms |

External payment provider latency is excluded where the provider is outside the ERP's control.

---

# 122. Financial Availability

The API follows the broader target:

**≥ 99.9% monthly availability**

Financial correctness requirements have higher priority than availability when the two conflict.

The system must not accept an uncertain financial transaction merely to preserve availability.

---

# 123. Financial Observability

Metrics should include:

```text
payment_success_count
payment_failure_count
payment_duplicate_count
payment_conflict_count
refund_success_count
refund_failure_count
cash_session_open_count
cash_session_close_count
cash_discrepancy_count
cash_correction_count
handover_mismatch_count
financial_sync_conflict_count
```

Metrics must avoid uncontrolled high-cardinality labels.

---

# 124. Financial Alerts

Operational alerts may include:

* repeated payment failures;
* abnormal duplicate attempts;
* large refund activity;
* repeated Cash Session discrepancies;
* repeated privileged corrections;
* unusual synchronization conflicts;
* financial API latency degradation.

Alert thresholds should be configurable.

---

# 125. Financial Tracing

A financial trace should allow operators to connect:

```text
API Request
   ↓
Operation UUID
   ↓
Payment / Refund / Cash Operation
   ↓
Database Transaction
   ↓
Audit
   ↓
Outbox
   ↓
Secondary Processing
```

This is important for investigating uncertain transaction outcomes.

---

# 126. Financial API Testing

Required tests include:

* payment success;
* duplicate payment;
* partial payment;
* unsupported overpayment;
* concurrent payment;
* refund success;
* refund limit;
* refund approval;
* duplicate refund;
* concurrent refund;
* Cash Session opening;
* duplicate session opening;
* Cash Session closing;
* discrepancy;
* correction;
* correction limit;
* privileged correction;
* handover;
* handover mismatch;
* duplicate handover;
* offline payment;
* financial synchronization;
* Business isolation;
* Branch isolation;
* authorization;
* historical integrity.

---

# 127. Financial Security Testing

Security tests must verify:

```text
Business A cannot access Business B financial data.

Branch A cannot access Branch B Cash Sessions.

Unauthorized employee cannot refund.

Unauthorized employee cannot close another cashier's session.

Manager cannot exceed granted financial permissions.

Client-provided amount cannot bypass server validation.

Client-provided Cash Session ID cannot bypass scope.

Client-provided Payment ID cannot bypass authorization.
```

---

# 128. Financial Historical Integrity Tests

The system must verify:

```text
Current Product Price
≠
Historical Payment Calculation
```

```text
Current Product Price
≠
Historical Refund Calculation
```

```text
Current Cash Session State
≠
Historical Closed Session Snapshot
```

```text
Current Discount Configuration
≠
Historical Payment Snapshot
```

---

# 129. Financial API Contract Testing

Each financial endpoint must have contract tests for:

* HTTP method;
* request schema;
* response schema;
* status code;
* error codes;
* idempotency;
* authorization;
* Business scope;
* Branch scope;
* concurrency;
* retry behavior;
* historical integrity.

---

# 130. Recommended Endpoint Map

The initial endpoint map is:

```text
Payments

POST   /api/v1/orders/{order_id}/payments
GET    /api/v1/orders/{order_id}/payments
GET    /api/v1/payments/{payment_id}
GET    /api/v1/orders/{order_id}/payments/history

Refunds

POST   /api/v1/orders/{order_id}/refunds
GET    /api/v1/orders/{order_id}/refunds
GET    /api/v1/refunds/{refund_id}
POST   /api/v1/refunds/{refund_id}/approve
POST   /api/v1/refunds/{refund_id}/reject

Cash Registers

GET    /api/v1/cash-registers
GET    /api/v1/branches/{branch_id}/cash-registers

Cash Sessions

POST   /api/v1/cash-sessions
GET    /api/v1/cash-sessions/{session_id}
GET    /api/v1/cash-sessions/active
POST   /api/v1/cash-sessions/{session_id}/close
GET    /api/v1/cash-sessions/{session_id}/summary

Cash Movements

POST   /api/v1/cash-sessions/{session_id}/movements
GET    /api/v1/cash-sessions/{session_id}/movements

Corrections

POST   /api/v1/cash-sessions/{session_id}/corrections
POST   /api/v1/cash-sessions/{session_id}/privileged-correction
GET    /api/v1/financial-corrections

Shift Handover

POST   /api/v1/cash-sessions/{session_id}/handover
POST   /api/v1/handovers/{handover_id}/accept
POST   /api/v1/handovers/{handover_id}/recount
```

The exact route names may be refined during OpenAPI contract design.

---

# 131. Endpoint Classification

| Endpoint              | Type    | Idempotency | Financial Mutation      |
| --------------------- | ------- | ----------- | ----------------------- |
| Create Payment        | Command | Required    | Yes                     |
| Read Payment          | Query   | N/A         | No                      |
| Create Refund         | Command | Required    | Yes                     |
| Approve Refund        | Command | Required    | Yes                     |
| Reject Refund         | Command | Required    | No financial completion |
| Open Cash Session     | Command | Required    | Yes                     |
| Close Cash Session    | Command | Required    | Yes                     |
| Cash Movement         | Command | Required    | Yes                     |
| Cash Correction       | Command | Required    | Yes                     |
| Privileged Correction | Command | Required    | Yes                     |
| Create Handover       | Command | Required    | Yes                     |
| Accept Handover       | Command | Required    | Yes                     |
| Recount Handover      | Command | Required    | Yes                     |
| Financial Read        | Query   | N/A         | No                      |

---

# 132. API and Financial Snapshots

Every financial mutation must preserve enough immutable information to reconstruct the authoritative transaction.

The API must never depend on future mutable configuration to reinterpret:

* Payment;
* Refund;
* Cash Session;
* cash movement;
* financial correction.

---

# 133. API and Reporting

Financial APIs provide transactional truth.

Reporting APIs consume financial data but do not modify it.

```text
Financial API
     ↓
Authoritative Financial State
     ↓
Reporting
```

A report must not become a source of financial truth.

---

# 134. API and Audit

Audit records and financial records serve different purposes.

Financial record:

> What financial event occurred?

Audit record:

> Who performed the operation, under what context, and what changed?

Both must remain available where required.

---

# 135. API and Notifications

Financial operations may trigger asynchronous notifications:

```text
Refund
Cash discrepancy
Privileged correction
Handover mismatch
Large financial event
```

Notification failure must not rollback committed financial state.

---

# 136. API and Printing

Financial receipt printing is a secondary operation.

A printer failure must not invalidate an already committed Payment.

The client may retrieve the financial state again after printing failure.

---

# 137. API and Offline Security

Offline financial operations must remain bounded by:

* trusted device;
* signed offline authorization;
* expiration;
* permitted capabilities;
* Branch;
* Business;
* employee;
* device;
* synchronization rules.

The device cannot extend its own offline authority.

---

# 138. API and Historical Corrections

Correction is not deletion.

The financial history should remain reconstructable:

```text
Original Event
+
Correction Event
+
Audit Event
=
Reconstructable Financial History
```

---

# 139. Architectural Guardrails

The Financial API must prohibit:

* deleting Payments;
* deleting Refunds;
* deleting closed Cash Sessions;
* client-authoritative financial totals;
* client-authoritative expected cash;
* duplicate financial operations;
* payment without idempotency;
* refund without required authorization;
* Cash Session access across Branch boundaries;
* reopening closed sessions through ordinary APIs;
* bypassing correction limits;
* bypassing refund approval;
* using current Product price for historical refunds;
* using cached data as final financial authority;
* treating printer success as payment success;
* treating notification success as financial commit;
* treating client “paid” state as authoritative;
* using Redis locks as the sole financial correctness mechanism.

---

# 140. System Invariants

The following invariants apply to Payment, Cash and Financial APIs:

1. PostgreSQL is the authoritative financial source.
2. Financial mutations are executed through Application use cases.
3. API routes do not directly mutate financial database state.
4. Payment UUID is distinct from Order UUID.
5. Refund UUID is distinct from Payment UUID.
6. Cash Session UUID is distinct from Cash Register UUID.
7. Client-provided financial amounts are not automatically authoritative.
8. Server validates payment amount.
9. Server validates refundable amount.
10. Server calculates expected cash.
11. Server calculates cash discrepancy.
12. Payment creation is idempotent.
13. Duplicate payment requests do not duplicate financial effects.
14. Refund creation is idempotent.
15. Duplicate refund requests do not duplicate financial effects.
16. Cash Session opening is concurrency-safe.
17. Only one valid active session exists per applicable register according to business rules.
18. Cash Session closing is concurrency-safe.
19. Closed Cash Sessions cannot be reopened through normal APIs.
20. Payment state transitions are Domain-controlled.
21. Refund state transitions are Domain-controlled.
22. Cash Session state transitions are Domain-controlled.
23. Clients cannot arbitrarily set financial states.
24. Payment cannot exceed the authoritative payable amount unless explicitly supported.
25. Total completed payments remain financially consistent.
26. Total refunds cannot exceed the refundable amount.
27. Current Product price cannot reinterpret historical Payment.
28. Current Product price cannot reinterpret historical Refund.
29. Current discount configuration cannot reinterpret historical Payment.
30. Historical Order financial snapshots remain authoritative.
31. Financial corrections do not delete original events.
32. Financial corrections create new historical events.
33. Financial records remain reconstructable.
34. Financial audit records remain immutable.
35. Cash Payments belong to the appropriate Cash Session.
36. Cash Payments cannot be attached to unrelated Branches.
37. Cash Session belongs to one Branch.
38. Cash Register belongs to one Branch.
39. Cross-Branch financial access requires explicit authority.
40. Cross-Business financial access is prohibited.
41. Client-provided Cash Session UUID cannot bypass scope validation.
42. Client-provided Payment UUID cannot bypass authorization.
43. Client-provided Refund UUID cannot bypass authorization.
44. Employee UUID alone is never sufficient financial authorization.
45. Device UUID alone is never sufficient financial authorization.
46. Refund permission is explicit.
47. Refund approval is explicit where required.
48. Privileged correction authority is explicit.
49. Correction limits are enforced server-side.
50. Client cannot bypass correction limits.
51. Handover records preserve outgoing cashier identity.
52. Handover records preserve incoming cashier identity.
53. Incoming cashier must authenticate as themselves.
54. Handover mismatches are preserved.
55. Recounts do not erase previous counts.
56. Handover acceptance is concurrency-safe.
57. Cash movements are immutable financial events.
58. Cash movement corrections create new events.
59. Cash Session discrepancy remains historically identifiable.
60. Shortage notifications are secondary effects.
61. Notification failure does not rollback financial transactions.
62. Receipt printing is a secondary effect.
63. Printer failure does not rollback committed Payment.
64. External payment timeout does not justify blind duplicate payment.
65. External payment uncertainty requires reconciliation.
66. Provider transaction identity is preserved where applicable.
67. Payment retry uses the same idempotency identity.
68. Financial operation replay does not duplicate business effects.
69. Offline financial operations require explicit offline authorization.
70. Offline authorization cannot be extended by the client.
71. Offline financial operations preserve original operation UUID.
72. Offline financial synchronization is server-authoritative.
73. Financial synchronization cannot resurrect deleted Business data.
74. Financial synchronization cannot bypass subscription restrictions.
75. Financial synchronization cannot bypass Branch authorization.
76. Financial synchronization conflicts remain explicit.
77. Financial read APIs are scope-controlled.
78. Financial history is not inferred from current mutable configuration.
79. Report data does not become financial authority.
80. Cache does not become financial authority.
81. Redis does not become financial authority.
82. Browser state does not become financial authority.
83. Frontend payment status does not become financial authority.
84. Financial API errors use stable error codes.
85. Financial API errors do not expose secrets.
86. Payment operations require bounded timeouts.
87. External payment calls cannot block transactions indefinitely.
88. Core financial transactions remain short.
89. Secondary processing is asynchronous where appropriate.
90. Financial API performance must remain within defined SLOs.
91. Financial API authorization must fail closed.
92. Security-sensitive cache state has bounded lifetime.
93. Business isolation is mandatory.
94. Branch isolation is mandatory.
95. Financial duplicate prevention is mandatory.
96. Historical financial integrity is mandatory.
97. Payment state must be observable.
98. Refund state must be observable.
99. Cash discrepancy must be observable.
100. Privileged financial corrections must be observable.
101. Financial operations must remain attributable to an actor.
102. Important financial operations retain device context where applicable.
103. Important financial operations retain Cash Session context where applicable.
104. Important financial operations retain Operation UUID.
105. Financial audit retains Request ID where applicable.
106. Financial mutations commit before secondary success is reported.
107. Uncommitted financial transactions cannot emit authoritative success events.
108. Uncertain financial outcomes require reconciliation rather than blind retry.
109. API changes must consider POS clients.
110. API changes must consider offline synchronization.
111. API changes must consider reporting.
112. API changes must consider audit.
113. API changes must consider cash handover.
114. API changes must preserve backward compatibility or use explicit versioning.
115. Financial contract tests are required.
116. Financial concurrency tests are required.
117. Financial isolation tests are required.
118. Financial idempotency tests are required.
119. Financial historical integrity tests are required.
120. Financial offline synchronization tests are required.
121. Financial correction does not erase the original financial event.
122. Current configuration cannot rewrite historical financial state.
123. Current pricing cannot rewrite historical financial state.
124. Current Recipe cannot rewrite historical financial state.
125. Current menu cannot rewrite historical financial state.
126. Financial APIs must remain compatible with the modular monolith architecture.
127. Financial correctness has priority over cache hit rate.
128. Financial correctness has priority over availability when state is uncertain.
129. Financial correctness has priority over latency when necessary.
130. The API must never accept an uncertain financial transaction merely to preserve performance.

---

# 141. Recommended Implementation Structure

```text
backend/
└── app/
    ├── api/
    │   └── v1/
    │       ├── payments/
    │       ├── refunds/
    │       ├── cash/
    │       ├── cash_sessions/
    │       ├── handover/
    │       └── financial/
    │
    ├── application/
    │   └── financial/
    │       ├── payments/
    │       ├── refunds/
    │       ├── cash_sessions/
    │       ├── cash_movements/
    │       ├── handover/
    │       └── corrections/
    │
    └── domain/
        └── financial/
            ├── payment/
            ├── refund/
            ├── cash_session/
            ├── cash_movement/
            ├── handover/
            └── correction/
```

The exact module structure may evolve during implementation without changing the public API contract.

---

# 142. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/10_Shift_Handover.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/22_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
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
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/13_API_POS_and_Order_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 143. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `14_API_Payment_Cash_and_Financial_Endpoints.md`

**Previous Document:** `13_API_POS_and_Order_Endpoints.md`

**Next Document:** `15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`

---

## Final Principle

> Financial APIs must treat every payment, refund, cash operation and correction as an authoritative business event. The API must prevent duplicate effects, preserve historical financial state, enforce authorization and concurrency, and never sacrifice financial correctness for convenience or performance.

