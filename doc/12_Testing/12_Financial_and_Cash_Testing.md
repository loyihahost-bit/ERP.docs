# Financial and Cash Testing

**Document ID:** TEST-12
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing architecture and mandatory testing rules for financial operations and cash management in FastFood.

Financial operations are among the highest-risk areas of the system because incorrect behavior can directly affect:

* business revenue;
* cashier balances;
* refunds;
* cash discrepancies;
* branch financial reports;
* employee accountability;
* inventory and order state;
* audit records.

The purpose of this document is to verify that financial operations remain correct, atomic, traceable, idempotent, and recoverable under normal, concurrent, offline, and failure conditions.

The testing scope includes:

* payments;
* payment completion;
* payment failures;
* refunds;
* refund approval;
* cash sessions;
* cash opening;
* cash closing;
* cashier handover;
* cash counting;
* discrepancies;
* corrections;
* privileged reopening;
* financial reporting;
* audit records;
* offline financial operations;
* concurrent financial operations;
* synchronization;
* duplicate requests;
* transaction failures;
* reconciliation.

---

# 2. Financial Testing Principles

Financial testing follows these principles:

1. Money-related operations must be tested more strictly than ordinary CRUD operations.
2. A financial operation must have one clearly defined business effect.
3. Duplicate requests must not create duplicate financial effects.
4. Financial state changes must be atomic.
5. Failed financial operations must not leave partial state.
6. Every financial operation must remain traceable.
7. Cash session ownership must be explicit.
8. Cash discrepancies must not be silently hidden.
9. Refunds must respect authorization and approval requirements.
10. Offline financial operations must be reconciled safely.
11. Concurrent financial operations must preserve financial invariants.
12. Historical financial records must remain stable.
13. Corrections must never silently rewrite historical financial facts.
14. Financial reports must reconcile with underlying transactions.
15. Test results must be deterministic and auditable.

---

# 3. Financial State Model

The testing architecture should distinguish between:

```text
Order State
Payment State
Cash Session State
Financial Transaction State
```

These states are related but must not be treated as identical.

A simplified lifecycle is:

```text
Order Created
     ↓
Order Accepted
     ↓
Payment Pending
     ↓
Payment Completed
     ↓
Order Completed
     ↓
Financial Record
     ↓
Cash Session Impact
     ↓
Reporting / Reconciliation
```

A refund introduces a separate flow:

```text
Completed Payment
      ↓
Refund Requested
      ↓
Authorization / Approval
      ↓
Refund Completed
      ↓
Financial Adjustment
      ↓
Audit / Reporting
```

The exact internal implementation may differ, but tests must verify equivalent business behavior.

---

# 4. Payment Testing Objectives

Payment testing must verify:

* correct amount;
* correct order;
* correct branch;
* correct cashier;
* correct cash session;
* correct payment status;
* correct financial effect;
* duplicate protection;
* failure handling;
* retry behavior;
* auditability;
* reconciliation.

Payment success must not be inferred solely from a client-side response.

The authoritative business result must be validated through the system's financial state.

---

# 5. Successful Payment Testing

Basic successful payment scenario:

```text
Order
  ↓
Valid Amount
  ↓
Authorized Cashier
  ↓
Payment
  ↓
Successful Completion
  ↓
Order Financial State Updated
```

Verify:

* payment amount equals expected amount;
* order becomes appropriately paid;
* payment record exists;
* cashier is correct;
* branch is correct;
* cash session is correct where applicable;
* financial report includes the payment;
* audit information is available.

---

# 6. Payment Amount Testing

Test:

* exact amount;
* zero amount where prohibited;
* negative amount;
* excessively large amount;
* decimal amount;
* rounding boundary;
* amount mismatch;
* changed order total before payment.

Invalid amounts must not create financial effects.

The test suite must verify that the server determines and validates the authoritative amount.

---

# 7. Payment and Order Total Consistency

Test:

```text
Order Total = 100
Payment = 100
```

and invalid cases:

```text
Order Total = 100
Payment = 90
```

```text
Order Total = 100
Payment = 110
```

where the business rules do not permit such differences.

Also test:

* discount applied before payment;
* product removed before payment;
* product quantity changed before payment;
* order modification during payment;
* stale order total.

The payment must correspond to the correct financial state of the order.

---

# 8. Duplicate Payment Testing

Duplicate payment is a release-blocking financial defect.

Test:

```text
Payment Request
      ↓
Processed
      ↓
Response Lost
      ↓
Retry
```

The final state must contain one financial effect.

Also test:

* same request submitted twice;
* same idempotency key submitted twice;
* simultaneous duplicate requests;
* duplicate synchronization;
* duplicate background processing.

Expected result:

```text
N Requests
    ↓
One Intended Payment
```

---

# 9. Payment Timeout Testing

A client timeout does not prove that payment failed.

Test:

```text
Client → Payment
          ↓
       Server
          ↓
       Payment Applied
          ↓
      Response Lost
          ↓
       Client Timeout
```

The retry must not create another payment.

The test must verify that the final financial state remains correct.

---

# 10. Payment Failure Testing

Test failures:

* invalid order;
* unauthorized cashier;
* invalid amount;
* closed cash session;
* wrong branch;
* duplicate payment;
* server error;
* database failure;
* network failure;
* transaction timeout;
* dependency failure.

A failed payment must not leave a partial financial effect.

---

# 11. Payment Transaction Atomicity

Where payment changes multiple business records, test atomicity.

For example:

```text
Payment
  ├── Payment Record
  ├── Order Financial State
  ├── Cash Session Effect
  └── Audit Record
```

Simulate failure between each stage.

The final state must follow the defined transaction and side-effect policy.

No invalid combination such as:

```text
Order = Paid
Payment Record = Missing
```

or:

```text
Payment Record = Exists
Cash Effect = Missing
```

may remain when those records are required to represent one atomic business transaction.

---

# 12. Payment Concurrency Testing

Test simultaneous payment attempts:

```text
Cashier A ─┐
            ├──→ Same Order
Cashier B ─┘
```

Verify:

* one valid payment effect where only one payment is allowed;
* correct final order state;
* no duplicate financial record;
* no incorrect cash balance;
* correct audit history.

Detailed concurrency strategy is defined in:

`docs/12_Testing/11_Concurrency_and_Consistency_Testing.md`

---

# 13. Payment and Cash Session Relationship

Where cash payment affects a cash session, verify:

* payment is associated with the correct branch;
* payment is associated with the correct active cash session;
* closed sessions cannot receive new ordinary payments;
* wrong cashier/session association is rejected;
* payment totals reconcile with the session.

A payment must never silently appear in the wrong cashier's session.

---

# 14. Cash Payment Testing

Test normal cash payment:

```text
Order Total = 50
Cash Received = 100
Change = 50
```

Verify:

* order financial state;
* cash received;
* change;
* net cash impact;
* cash session balance;
* report totals.

Where the system does not explicitly store cash denominations, tests should still verify the financial meaning of received cash and returned change.

---

# 15. Non-Cash Payment Testing

Where non-cash payment methods are supported, test:

* successful payment;
* failed payment;
* timeout;
* duplicate callback/request;
* external confirmation;
* missing confirmation;
* retry;
* reconciliation.

The exact external provider behavior is outside the core financial domain, but the resulting FastFood financial state must remain correct.

---

# 16. Payment Cancellation Testing

If payment cancellation is supported, test:

* cancellation before completion;
* cancellation after completion;
* repeated cancellation;
* unauthorized cancellation;
* cancellation during synchronization;
* cancellation during concurrent payment.

The system must not confuse cancellation with refund.

---

# 17. Payment Historical Integrity

Completed payment records must remain historically meaningful.

Test:

* later order price change;
* later product price change;
* later discount change;
* later menu change;
* later recipe change;
* later employee change.

Historical financial records must not silently change because configuration changed later.

---

# 18. Refund Testing Objectives

Refund testing must verify:

* authorization;
* reason;
* approval;
* amount;
* original payment relationship;
* duplicate protection;
* financial adjustment;
* cash impact where applicable;
* audit;
* reporting.

Refunds must not be implemented or tested as simple deletion of the original payment.

---

# 19. Refund Authorization Testing

Test:

* authorized staff;
* unauthorized staff;
* employee without refund permission;
* manager with permitted refund capability;
* owner;
* incorrect branch;
* disabled employee.

Unauthorized refund attempts must produce no financial effect.

---

# 20. Refund Reason Testing

Refund requires a reason according to the approved business rules.

Test:

* valid reason;
* missing reason;
* empty reason;
* excessively long reason;
* invalid input;
* reason preserved in audit/reporting.

A successful refund must remain explainable.

---

# 21. Refund Approval Testing

Where approval is required, test:

```text
Refund Requested
      ↓
Approval Required
      ↓
Approved
      ↓
Refund Completed
```

and:

```text
Refund Requested
      ↓
Rejected
      ↓
No Refund Effect
```

Test:

* unauthorized approval;
* duplicate approval;
* approval after cancellation;
* approval for wrong refund;
* concurrent approval attempts.

---

# 22. Refund Amount Testing

Test:

* full refund;
* permitted partial refund;
* zero refund;
* negative refund;
* amount greater than original payment;
* amount greater than remaining refundable amount;
* repeated partial refunds.

The final refundable amount must never become negative.

If partial refunds are not supported for a specific workflow, attempts must be rejected.

---

# 23. Duplicate Refund Testing

Test:

```text
Refund Request
      ↓
Processed
      ↓
Response Lost
      ↓
Retry
```

and:

```text
Refund A ─┐
          ├──→ Same Payment
Refund B ─┘
```

The system must not create duplicate refund effects.

---

# 24. Refund and Order State Testing

Test refund behavior for:

* completed order;
* already refunded order;
* partially refunded order where supported;
* cancelled order;
* unpaid order;
* invalid order;
* archived order.

The refund must follow the approved order/payment lifecycle.

---

# 25. Refund and Cash Testing

For a cash refund, verify:

```text
Original Cash In
      ↓
Refund Cash Out
      ↓
Cash Session Adjustment
```

The cash balance and refund record must reconcile.

For non-cash refunds, the cash session must not incorrectly receive a cash deduction unless explicitly required.

---

# 26. Large Refund Alert Testing

The system has a requirement to notify the Owner for large refunds.

Test:

* refund below threshold;
* refund at threshold;
* refund above threshold;
* repeated refunds;
* approved large refund;
* rejected large refund.

Verify that:

* the correct alert is generated;
* unauthorized users cannot suppress it;
* the financial operation remains correct;
* the alert does not create duplicate financial effects.

---

# 27. Cash Session Testing

FastFood uses one cash register per branch.

Testing must verify the lifecycle:

```text
Closed
  ↓
Opening
  ↓
Open
  ↓
Handover / Activity
  ↓
Closing
  ↓
Closed
```

Invalid transitions must be rejected.

---

# 28. Cash Session Opening

Test:

* valid cashier;
* authorized cashier;
* correct branch;
* already-open register;
* second opening attempt;
* invalid opening amount where applicable;
* application restart during opening;
* network failure during opening;
* duplicate opening request.

Only one valid active cash session may exist for the branch/register according to the approved business model.

---

# 29. Customer-Facing Session Number

The customer-facing three-digit session number is distinct from the persistent database identity.

Test:

* first opening;
* closing;
* next opening;
* customer-facing number reset;
* database identity remains unique;
* reports use the correct persistent identity;
* no collision causes incorrect historical data.

Example:

```text
Cash Session A
Customer Number = 001
Database ID = 4821

Closed

Cash Session B
Customer Number = 001
Database ID = 4822
```

The repeated customer-facing number must not merge the two sessions.

---

# 30. Cash Session Closing

Test:

* normal close;
* cashier comment;
* correct cash count;
* payment reconciliation;
* shortage;
* surplus where applicable;
* network interruption;
* duplicate close request;
* close after already closed;
* application restart during closing.

Closing must produce a durable final state.

---

# 31. Cashier Closing Comment

Where a cashier closing comment is required, test:

* valid comment;
* missing comment;
* empty comment;
* maximum length;
* special characters;
* comment stored with closing record;
* Owner notification.

The comment must remain associated with the correct cash session.

---

# 32. Cash Count Testing

Test:

* exact expected cash;
* shortage;
* surplus where applicable;
* invalid amount;
* repeated count;
* recount;
* count after payment activity;
* count during attempted concurrent transaction.

The system must clearly distinguish:

```text
Expected Cash
Actual Cash
Difference
```

---

# 33. Discrepancy Testing

Discrepancy is calculated from the approved cash-session rules.

At minimum test:

```text
Expected Cash = Actual Cash
Difference = 0
```

```text
Expected Cash > Actual Cash
Difference = Shortage
```

```text
Expected Cash < Actual Cash
Difference = Surplus
```

The sign and representation must remain consistent throughout:

* session report;
* Owner notification;
* cashier report;
* financial report;
* audit record.

---

# 34. Shortage Testing

Test:

* small shortage;
* large shortage;
* shortage exactly at alert threshold;
* shortage above threshold;
* repeated shortage;
* shortage during handover;
* shortage during final close.

The system must not silently adjust the cashier balance simply to remove the discrepancy.

---

# 35. Owner Notification for Shortage

Where a shortage occurs, verify:

* prior cashier is identifiable;
* Owner receives the required notification;
* notification contains sufficient context;
* notification is associated with the correct session;
* notification does not reveal unrelated business data;
* notification generation does not duplicate the financial effect.

---

# 36. Handover Testing

Cashier handover is a controlled transition.

Test:

```text
Outgoing Cashier
      ↓
Cash Count
      ↓
Handover
      ↓
Incoming Cashier
      ↓
Confirmation
```

Verify:

* correct outgoing cashier;
* correct incoming cashier;
* correct branch;
* correct session;
* cash count;
* confirmation;
* audit;
* final ownership state.

---

# 37. Handover Without Confirmation

Test:

* incoming cashier does not confirm;
* incoming cashier rejects;
* network fails during confirmation;
* application closes during confirmation;
* duplicate confirmation.

The system must not incorrectly mark a handover as complete without the required confirmation.

---

# 38. Handover Discrepancy

Test shortage during handover.

Verify:

* shortage is recorded;
* previous cashier is identified;
* incoming cashier confirmation is recorded;
* Owner notification occurs where required;
* session state remains consistent.

---

# 39. Handover and Concurrent Operations

Test an order/payment arriving while handover is occurring.

Possible states include:

```text
Cashier A → Handover
Cashier B → Confirm
Cashier A → Payment Request
```

The system must apply the approved session ownership and authorization rules.

No payment should be silently attributed to the wrong cashier/session.

---

# 40. Cash Correction Testing

Corrections must be tested as controlled operations.

Test:

* permitted correction;
* unauthorized correction;
* correction reason;
* correction count;
* correction after close;
* correction during open session;
* repeated correction;
* failed correction;
* concurrent correction.

Historical information must remain auditable.

---

# 41. Three-Correction Limit

The approved business rule allows a maximum of three corrections before privileged reopening is required.

Test:

```text
Correction 1 → Allowed
Correction 2 → Allowed
Correction 3 → Allowed
Correction 4 → Rejected
                  ↓
          Privileged Reopen
```

Verify:

* exact counting;
* no off-by-one error;
* rejected fourth correction has no financial effect;
* privileged reopen is separately authorized;
* reopen is audited.

---

# 42. Privileged Reopen Testing

Test:

* authorized privileged user;
* unauthorized user;
* reopen reason;
* already-open session;
* already-closed session;
* repeated reopen;
* correction after reopen;
* final close after correction.

Privileged reopening must never silently rewrite the original close event.

---

# 43. Cash Session Reconciliation

At session close, test reconciliation between:

```text
Opening State
+
Cash Payments
+
Cash Adjustments
-
Cash Refunds
± Approved Corrections
=
Expected Closing Cash
```

The exact formula may be extended by the business rules, but the financial meaning must remain consistent.

---

# 44. Cash and Order Reconciliation

Test that all cash-affecting completed orders are represented in the appropriate session.

Verify:

* order payment;
* cash amount;
* cashier;
* branch;
* session;
* final report.

An order must not be financially completed without the required cash/financial effect.

---

# 45. Cash and Refund Reconciliation

Verify that cash refunds are reflected in the same financial accounting model as cash payments.

Test:

```text
Cash In
  +
Cash Adjustments
  -
Cash Refunds
=
Expected Cash
```

No refund should disappear from the cash session merely because the original order is archived.

---

# 46. Offline Financial Testing

Financial operations performed offline must be tested with special care.

Test:

* offline payment;
* offline cash activity;
* offline order completion;
* offline refund where supported;
* network loss immediately after operation;
* synchronization retry;
* duplicate synchronization;
* conflict;
* device restart;
* server restart.

Detailed synchronization scenarios are defined in:

`docs/12_Testing/10_Offline_and_Synchronization_Testing.md`

---

# 47. Offline Payment Reconciliation

Example:

```text
Branch Offline
     ↓
Payment Accepted Locally
     ↓
Network Restored
     ↓
Synchronization
     ↓
Server Financial State
```

Verify:

* one payment;
* correct amount;
* correct order;
* correct cashier;
* correct branch;
* correct session;
* correct final report.

---

# 48. Concurrent Financial Operations

Financial operations must be tested under concurrency.

Required scenarios:

* two payments for one order;
* two refunds for one payment;
* payment and refund simultaneously;
* two cash-session openings;
* two cash-session closings;
* payment during handover;
* correction during closing;
* synchronization from multiple devices.

The expected result must preserve financial invariants.

---

# 49. Transaction Rollback Testing

For every critical financial transaction, simulate failure at different points.

Example:

```text
Payment Started
     ↓
Payment Record
     ↓
Failure
     ↓
Rollback / Recovery
```

Verify that the final state does not contain an incomplete financial transaction.

Test failure:

* before database write;
* after primary write;
* after related financial write;
* during audit creation;
* during notification generation;
* during synchronization acknowledgment.

Side effects must follow the approved transaction policy.

---

# 50. Database Constraint Testing

Financial integrity must be protected by appropriate persistence constraints where applicable.

Test concurrent attempts against:

* unique payment identifiers;
* unique operation identifiers;
* valid foreign keys;
* valid session relationships;
* valid order relationships;
* valid refund relationships.

Application validation alone must not be considered sufficient evidence of concurrency safety.

---

# 51. Financial Audit Testing

Important financial actions must be traceable.

Test audit records for:

* payment;
* failed payment;
* refund;
* refund approval;
* cash opening;
* cash closing;
* handover;
* discrepancy;
* recount;
* correction;
* privileged reopen.

Where applicable, audit information should identify:

* actor;
* role;
* branch;
* cash session;
* operation;
* timestamp;
* result;
* reason.

---

# 52. Historical Financial Integrity

Historical records must remain stable.

Test that later changes to:

* menu;
* product;
* price;
* recipe;
* employee;
* branch configuration;
* permissions

do not rewrite historical financial facts.

Corrections must create controlled financial history rather than silently replacing the original record.

---

# 53. Financial Reporting Testing

Financial reports must reconcile with underlying records.

Test:

* daily payment totals;
* cashier totals;
* branch totals;
* refund totals;
* cash-session totals;
* discrepancy totals;
* date filtering;
* branch filtering;
* cashier filtering.

Reports must not double-count:

* payments;
* refunds;
* sessions;
* corrections.

---

# 54. Selected-Day Reporting

The dashboard supports selected-day reporting.

Test:

* one day;
* date boundary;
* day with no transactions;
* day with payment;
* day with refund;
* day with cash discrepancy;
* day containing multiple cash sessions;
* historical day after later corrections.

The selected-day report must use the correct business date and financial records.

---

# 55. Financial Import and Export Testing

Where financial data can be exported or imported, test:

* authorized access;
* correct business scope;
* correct branch scope;
* correct totals;
* duplicate import protection;
* malformed financial data;
* audit trail.

Financial imports must not silently create duplicate financial effects.

---

# 56. Financial Data Precision Testing

Test:

* integer amounts where applicable;
* decimal amounts;
* rounding;
* repeated calculations;
* discounts;
* refund calculations;
* totals;
* aggregation.

Floating-point rounding errors must not create unexplained financial discrepancies.

The representation must preserve the precision required by the business rules.

---

# 57. Time and Date Testing

Financial reports depend on dates and session boundaries.

Test:

* order date;
* payment date;
* refund date;
* session opening date;
* session closing date;
* synchronization date;
* selected-day boundaries;
* timezone behavior;
* operations near midnight.

An operation synchronized later must not automatically change its original business date unless the approved accounting rule requires it.

---

# 58. Financial Failure Matrix

| Failure                    | Expected Result                |
| -------------------------- | ------------------------------ |
| Invalid amount             | No financial effect            |
| Unauthorized payment       | No financial effect            |
| Duplicate payment          | One effect                     |
| Payment timeout            | Safe retry/reconciliation      |
| Database failure           | Rollback or safe recovery      |
| Duplicate refund           | One effect                     |
| Unauthorized refund        | No effect                      |
| Invalid refund amount      | No effect                      |
| Cash close failure         | No invalid partial close       |
| Duplicate close            | One final close                |
| Handover failure           | No false confirmation          |
| Recount failure            | Previous valid state preserved |
| Fourth correction          | Rejected                       |
| Unauthorized reopen        | Rejected                       |
| Offline sync duplicate     | One financial effect           |
| Server restart during sync | Recoverable                    |
| Network loss               | Operation remains recoverable  |

---

# 59. Financial Test Data

Financial tests should use deterministic fixtures containing:

* business;
* branch;
* owner;
* cashier;
* manager where applicable;
* trusted device;
* cash session;
* order;
* products;
* prices;
* discounts;
* payment;
* refund;
* cash balance;
* discrepancy.

Test data must allow exact expected totals to be calculated independently.

---

# 60. Financial Test Oracle

A financial test should not verify only that an API returned success.

The test oracle should compare the final business state.

For example:

```text
Expected:
Order Paid
Payment = 100
Cash Session +100
Refund = 0

Actual:
Order Paid
Payment = 100
Cash Session +100
Refund = 0
```

A response status of `200` or equivalent is not sufficient evidence of financial correctness.

---

# 61. Test Layer Strategy

## Unit and Domain Tests

Verify:

* amount calculations;
* refund limits;
* discrepancy calculations;
* correction limits;
* state transitions;
* financial invariants.

## Application Tests

Verify:

* payment workflow;
* refund workflow;
* cash session workflow;
* handover;
* approval;
* correction;
* transaction orchestration.

## Repository and Database Tests

Verify:

* financial persistence;
* constraints;
* transaction rollback;
* concurrent updates;
* unique identifiers;
* aggregation.

## Integration Tests

Verify:

* payment to order;
* payment to cash session;
* refund to financial state;
* notifications;
* synchronization.

## E2E Tests

Verify complete real-world cashier workflows.

---

# 62. Critical Financial Regression Suite

The following scenarios should be mandatory:

1. successful cash payment;
2. successful non-cash payment where supported;
3. duplicate payment;
4. payment timeout and retry;
5. failed payment with no financial effect;
6. simultaneous payment attempts;
7. full refund;
8. unauthorized refund;
9. invalid refund amount;
10. duplicate refund;
11. large refund alert;
12. cash session opening;
13. duplicate session opening;
14. normal cash closing;
15. shortage at closing;
16. Owner shortage notification;
17. cashier handover;
18. handover confirmation failure;
19. discrepancy and recount;
20. three allowed corrections;
21. fourth correction rejection;
22. privileged reopen;
23. offline payment synchronization;
24. duplicate offline payment synchronization;
25. concurrent offline financial operations;
26. server restart during financial synchronization;
27. final financial reconciliation.

---

# 63. CI Testing Strategy

## Fast CI

Run:

* financial calculations;
* refund rules;
* discrepancy calculations;
* correction limits;
* state transitions;
* idempotency rules.

## Integration CI

Run:

* payment persistence;
* cash-session persistence;
* refund persistence;
* transaction rollback;
* database constraints;
* concurrency scenarios.

## E2E CI

Run:

* complete payment workflow;
* cash session;
* handover;
* refund;
* discrepancy;
* Owner notification.

## Release Testing

Run:

* complete critical financial suite;
* offline financial tests;
* concurrency tests;
* reconciliation;
* performance under realistic branch load;
* failure and recovery tests.

---

# 64. Performance and Concurrency

Financial correctness has priority over raw throughput.

Performance tests should still verify that:

* payment processing remains responsive;
* lock contention is reasonable;
* cash-session operations do not unnecessarily block;
* reports do not destabilize payment operations;
* synchronization does not duplicate financial effects.

Detailed performance testing is defined in:

`docs/12_Testing/17_Performance_Load_and_SLO_Testing.md`

---

# 65. Flaky Financial Tests

Financial tests must be highly deterministic.

Avoid:

* random amounts without expected calculations;
* uncontrolled timing;
* real external payment providers in ordinary CI;
* shared mutable cash sessions;
* uncontrolled retries;
* approximate financial assertions.

Use exact expected financial values and controlled transaction states.

A flaky financial test must not simply be retried until it passes.

---

# 66. Regression Requirements

Every confirmed financial defect should produce a regression test whenever practical.

Example:

```text
Defect:
Duplicate payment after network timeout.

Regression:
1. Create unpaid order.
2. Submit payment.
3. Process payment.
4. Drop response.
5. Retry payment.
6. Verify one payment.
7. Verify one cash-session effect.
8. Verify correct final order state.
```

The regression test must remain at the lowest appropriate test level and be supplemented by integration/E2E coverage when required.

---

# 67. Change Impact Testing

Financial impact analysis is required when changing:

* order lifecycle;
* payment;
* refund;
* cash session;
* handover;
* inventory;
* discounts;
* pricing;
* authorization;
* synchronization;
* database transactions;
* reports;
* notifications;
* background workers;
* external payment integrations.

A change to an apparently non-financial workflow must be reviewed for possible financial consequences.

---

# 68. Relationship to Other Testing Documents

### TEST-04 — Domain Testing

Defines the financial business rules and invariants that must be proven.

### TEST-05 — Application and Use Case Testing

Tests financial workflow orchestration.

### TEST-06 — Repository and Database Integration Testing

Tests financial persistence and database integrity.

### TEST-08 — Integration Testing

Tests financial subsystem boundaries.

### TEST-09 — End-to-End and POS Testing

Tests complete cashier-facing payment and cash workflows.

### TEST-10 — Offline and Synchronization Testing

Defines offline synchronization behavior used by offline financial operations.

### TEST-11 — Concurrency and Consistency Testing

Defines deeper race-condition, locking, and concurrent financial testing.

### TEST-13 — Inventory and Recipe Testing

Tests the inventory effects that can be connected to completed financial orders.

### TEST-14 — Authentication, Authorization and Security Testing

Verifies financial permissions and privileged operations.

### TEST-17 — Performance, Load and SLO Testing

Verifies financial behavior under realistic load.

### TEST-18 — Resilience and Chaos Testing

Verifies financial recovery during infrastructure failures.

---

# 69. Mandatory Financial Invariants

The following invariants are mandatory:

1. A successful payment creates exactly the intended financial effect.
2. A failed payment creates no unintended financial effect.
3. Duplicate payment requests do not duplicate the financial effect.
4. Payment amount must match the authoritative business state.
5. Payment must belong to the correct order.
6. Payment must belong to the correct business and branch.
7. Cash payment must affect the correct cash session.
8. A completed payment must remain historically traceable.
9. Refunds require the required authorization.
10. Refunds require the required reason.
11. Refunds must not exceed the permitted refundable amount.
12. Duplicate refunds must not create duplicate financial effects.
13. Refunds must remain linked to the original financial transaction.
14. Large refunds must trigger the required notification.
15. Only one valid active cash session may exist for the branch/register according to the approved model.
16. Cash session opening must be idempotent.
17. Cash session closing must be idempotent.
18. A closed session must not receive ordinary new cash transactions.
19. Cashier handover must require the approved confirmation.
20. Cash discrepancies must be explicitly recorded.
21. Shortages must not be silently hidden.
22. Recount must not silently rewrite the original count.
23. Only the allowed number of corrections may be performed.
24. A fourth correction requires the approved privileged reopen flow.
25. Privileged reopening must be authorized and audited.
26. Historical financial records must not be silently rewritten.
27. Financial reports must reconcile with underlying transactions.
28. Offline financial operations must remain idempotent during synchronization.
29. Concurrent financial operations must preserve financial invariants.
30. Transaction failure must not leave an invalid partial financial state.
31. Retry after timeout must not duplicate financial effects.
32. Financial operations must remain within the correct tenant and branch scope.
33. Financial audit records must remain traceable.
34. Financial correctness takes priority over synchronization or processing speed.

---

# 70. Acceptance Criteria

TEST-12 is considered successfully implemented when:

* successful payment scenarios are covered;
* failed payment scenarios are covered;
* duplicate and retry payment scenarios are covered;
* payment concurrency is covered;
* payment and cash-session relationships are verified;
* refund authorization is tested;
* refund reasons are tested;
* refund approval is tested;
* refund limits are tested;
* duplicate refunds are tested;
* large refund alerts are tested;
* cash session opening is tested;
* cash session closing is tested;
* customer-facing session number behavior is tested;
* persistent session identity is tested;
* cashier handover is tested;
* cash counting is tested;
* shortage and discrepancy are tested;
* Owner notification is tested;
* recount is tested;
* correction limits are tested;
* privileged reopen is tested;
* offline financial synchronization is tested;
* financial concurrency is tested;
* transaction rollback is tested;
* financial reconciliation is tested;
* critical scenarios are included in CI;
* release-blocking financial invariants are enforced;
* financial defects generate regression tests.

---

# 71. Final Rule

Financial testing must verify the complete business effect rather than only individual API responses or database records.

The core financial verification model is:

```text
Business Action
      ↓
Authorization
      ↓
Amount / State Validation
      ↓
Atomic Financial Operation
      ↓
Order / Payment / Cash State
      ↓
Audit
      ↓
Reporting
      ↓
Reconciliation
```

For critical operations, the system must remain correct under:

```text
Normal Operation
       +
Duplicate Request
       +
Retry
       +
Timeout
       +
Concurrency
       +
Offline Mode
       +
Synchronization
       +
Failure / Recovery
```

The final rule is:

> A financial operation is correct only when the intended amount, business state, cash state, authorization, audit history, and final report all agree on one valid financial outcome.

No payment, refund, cash session, handover, discrepancy, or financial correction is considered production-ready until its normal, concurrent, offline, duplicate, failure, and recovery paths have been tested.

