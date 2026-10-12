# 09 — End-to-End and POS Testing

**Document ID:** TEST-09
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-05, TEST-07, TEST-08
**Related:** TEST-10, TEST-11, TEST-12, TEST-13, TEST-14, TEST-15, TEST-17, TEST-18, TEST-19

---

## 1. Purpose

This document defines the end-to-end testing architecture for the FastFood POS system.

The primary purpose is to verify complete user-visible business workflows from the beginning of an operation to its expected final state.

POS end-to-end testing validates that the major components of the system work together as experienced by actual branch staff.

The most important workflow is:

```text
Cashier
   ↓
Open Cash Session
   ↓
Create Order
   ↓
Accept Order
   ↓
Kitchen / Preparation
   ↓
Payment
   ↓
Order Completion
   ↓
Cash / Financial State
   ↓
Archive / History
   ↓
Cash Session Close
```

The system must be tested not only when everything works normally, but also when important failures, interruptions, retries, and operational exceptions occur.

---

# 2. E2E Testing Boundary

End-to-end testing validates the complete business workflow across system boundaries.

```text
User
 ↓
Frontend / POS UI
 ↓
API
 ↓
Application
 ↓
Domain
 ↓
Database
 ↓
Queues / Workers / Devices
 ↓
Final Business State
```

The key question is:

> **Can a real operator complete an important business workflow and does the entire system reach the correct final state?**

E2E tests should represent real operational scenarios rather than internal implementation details.

---

# 3. What E2E Testing Proves

E2E POS tests provide evidence that:

* the cashier can authenticate;
* the correct branch context is established;
* the cash session can be opened;
* orders can be created;
* order items are represented correctly;
* orders reach the intended operational state;
* kitchen processing receives the expected order;
* payment can complete the order;
* cash and financial state are updated;
* completed orders are archived correctly;
* the cashier can close the session;
* handover works where applicable;
* reports reflect the completed operation;
* failures do not leave the system in an invalid operational state.

---

# 4. What E2E Testing Does Not Replace

E2E testing does not replace lower-level testing.

### TEST-03

Unit behavior.

### TEST-04

Domain rules and invariants.

### TEST-05

Application/use-case orchestration.

### TEST-06

Repository and database integration.

### TEST-07

API contract and schema compatibility.

### TEST-08

Subsystem integration.

### TEST-10

Offline and synchronization testing.

### TEST-11

Concurrency and consistency testing.

### TEST-12

Detailed financial and cash testing.

### TEST-13

Detailed inventory and recipe testing.

### TEST-14

Detailed authentication, authorization, and security testing.

E2E tests validate that these capabilities work together in realistic workflows.

---

# 5. E2E Testing Philosophy

E2E tests should be:

* business-oriented;
* user-visible;
* realistic;
* deterministic;
* limited to high-value workflows;
* failure-aware;
* representative of actual branch operations.

E2E tests should not attempt to test every possible combination.

The lower testing layers provide broad coverage.

E2E tests provide deep confidence in selected critical workflows.

---

# 6. POS Operating Model

The POS system operates around a branch-level cash session.

The core relationship is:

```text
Branch
  ↓
Cash Register
  ↓
Cash Session
  ↓
Cashier
  ↓
Orders
  ↓
Payments
```

The system assumes one active cash register per branch.

The customer-facing opening/closing number may reset for each session while the database maintains a separate persistent identifier.

E2E tests must verify both:

* operator-facing behavior;
* persistent business state.

---

# 7. Primary POS E2E Workflow

The primary happy-path workflow is:

```text
1. Cashier authenticates
2. Branch context is established
3. Cashier opens cash session
4. Starting cash is confirmed
5. Customer order is created
6. Order type is selected
7. Products are added
8. Quantities are confirmed
9. Order is accepted
10. Kitchen receives the order
11. Order status progresses
12. Payment is completed
13. Order is marked completed
14. Financial records are updated
15. Order becomes historical/archived according to policy
16. Cashier continues operations
17. Cashier closes cash session
18. Closing result is generated
```

This workflow should exist as a critical release-level E2E scenario.

---

# 8. Cashier Authentication

The E2E workflow begins with a valid cashier identity.

The test must verify:

* login succeeds;
* correct employee is identified;
* correct branch scope is established;
* cashier receives the expected POS access;
* unauthorized functions are not presented as usable;
* the system reaches the POS-ready state.

The exact authentication mechanism is tested more deeply by TEST-14.

E2E testing verifies the user-visible result.

---

# 9. Branch Context

After authentication, the POS must operate within the correct branch.

The E2E test should verify that:

```text
Cashier
  ↓
Branch
  ↓
Cash Register
  ↓
Orders
```

remain associated with the same operational context.

A test must fail if an order unexpectedly appears under another branch.

---

# 10. Cash Session Opening

The cashier must be able to open the branch cash session.

The E2E test should verify:

* no active session exists before opening;
* cashier starts a new session;
* starting cash is entered or confirmed according to the UI;
* session becomes active;
* customer-facing opening number is generated;
* persistent session identity exists;
* POS operations become available.

The session must not become active if the opening operation fails.

---

# 11. Cash Session Opening Number

The customer-facing opening/closing number is intentionally separate from the persistent database identifier.

E2E tests must verify:

```text
Customer-facing number
        ≠
Persistent database identity
```

The customer-facing number may reset for a new opening/closing cycle.

The persistent identity must remain unique.

---

# 12. Starting Cash

Where starting cash is required, the test should verify:

* valid amount accepted;
* invalid amount rejected;
* session records the opening amount;
* opening information is visible to the cashier;
* later cash calculations include the opening amount correctly.

Detailed monetary calculations belong to TEST-12.

---

# 13. Order Creation

The cashier must be able to create a new order.

The E2E test should verify:

* new order can be started;
* order receives an identifier;
* correct branch context is retained;
* cashier is associated with the operation;
* order remains editable before acceptance.

---

# 14. Order Types

The POS must support the currently defined order types:

* dine-in;
* takeaway;
* phone delivery.

E2E tests should cover each important order type.

For delivery orders, the workflow should verify the required order information such as:

* phone number;
* delivery address.

The system should not require a permanent customer record merely to process a delivery order.

---

# 15. Dine-In Workflow

The dine-in workflow should verify:

```text
Select Dine-In
      ↓
Select / Assign Table
      ↓
Add Items
      ↓
Accept Order
      ↓
Table Becomes Busy
```

The test should verify that the table state is correctly represented.

If the system supports waiting/table states, those states should also be tested.

---

# 16. Takeaway Workflow

The takeaway workflow should verify:

```text
Takeaway
   ↓
Add Items
   ↓
Accept
   ↓
Prepare
   ↓
Payment
   ↓
Complete
```

The system should not require unnecessary table information.

---

# 17. Phone Delivery Workflow

The delivery workflow should verify:

```text
Phone Delivery
      ↓
Phone / Address
      ↓
Items
      ↓
Accept
      ↓
Preparation
      ↓
Payment
      ↓
Complete
```

The test should verify that delivery information remains associated with the order.

It should also verify that delivery data does not unintentionally create or require a permanent customer profile.

---

# 18. Adding Products

The cashier should be able to add products to an order.

E2E tests should verify:

* product can be selected;
* quantity can be changed;
* multiple products can be added;
* order total updates;
* product price is represented correctly;
* unavailable products cannot be sold when business rules prohibit the sale.

The exact inventory and recipe rules are covered more deeply by TEST-13.

---

# 19. Quantity Changes

The E2E workflow should verify:

```text
Product × 1
      ↓
Product × 2
      ↓
Correct order quantity
      ↓
Correct total
```

It should also verify invalid quantities are rejected.

Examples include:

* zero where not permitted;
* negative quantity;
* invalid numeric input;
* quantity exceeding business limits where applicable.

---

# 20. Recipe-Driven Products

For products with recipes, E2E testing should verify the user-visible effect of recipe availability.

Example:

```text
Order Product
      ↓
Recipe
      ↓
Required Ingredients
      ↓
Stock Availability
```

If required stock is unavailable and the business rule blocks sale, the cashier must receive an appropriate result.

If the product is allowed after a valid modification to its recipe components, the resulting order must reflect the permitted change.

Detailed recipe logic belongs to TEST-13.

---

# 21. Order Modification

Before order acceptance, the cashier should be able to modify the order according to permissions.

E2E tests should verify:

* add item;
* remove item;
* change quantity;
* apply permitted discount;
* modify permitted recipe components;
* updated price;
* updated order total;
* updated kitchen information.

A completed or otherwise locked order must not remain freely editable if business rules prohibit modification.

---

# 22. Price Calculation

The E2E test must verify that the displayed total matches the expected business result.

Examples may include:

```text
Base product price
+
Additional permitted components
-
Discount
=
Order total
```

The test should verify the final amount rather than implementation details.

Detailed financial calculations belong to TEST-12.

---

# 23. Discounts

Where discounts are supported, E2E testing should cover:

* permitted discount;
* correct total;
* unauthorized discount attempt;
* discount visibility;
* completed payment using discounted total.

The test should ensure that the discount is reflected consistently across:

* order;
* payment;
* cash session;
* report.

---

# 24. Order Acceptance

Order acceptance is a major POS boundary.

The E2E test should verify:

```text
Draft Order
    ↓
Accept
    ↓
Operational Order
```

After acceptance:

* order receives its operational number;
* kitchen workflow begins;
* order becomes visible in the appropriate operational interface;
* required printing/event behavior occurs;
* prohibited modifications are blocked.

---

# 25. Kitchen Order Printing

Where printers are configured, acceptance may trigger kitchen printing.

The E2E test should verify the software-level workflow:

```text
Order Accepted
      ↓
Print Request
      ↓
Correct Printer Routing
      ↓
Print Result
```

For example, pizza-related items may be routed to one configured printer while lavash-related items are routed to another.

Hardware-independent printer integration tests belong to TEST-08.

Physical printer validation may be covered separately when required.

---

# 26. Order Number

The accepted order must have a customer/operator-visible order number where the POS workflow requires one.

E2E tests should verify:

* number is generated;
* number is visible;
* number is associated with the correct order;
* number does not unexpectedly collide with another active order.

---

# 27. Kitchen Status Flow

Where item/order statuses are configurable, E2E testing should verify the operational flow.

Example:

```text
Accepted
   ↓
Preparing
   ↓
Ready
```

If the system supports per-item status visibility, the test should verify that the cashier sees the intended state.

The test should not assume a fixed status vocabulary if the business configuration allows statuses to change.

---

# 28. Waiting and Busy Tables

For dine-in workflows, E2E tests should verify table state.

Example:

```text
Available
   ↓
Order Assigned
   ↓
Busy
   ↓
Order Completed
   ↓
Available
```

If the system supports a waiting state, that state must be tested separately.

---

# 29. Payment Workflow

Payment is the final major step of the order workflow.

The E2E test should verify:

```text
Accepted Order
      ↓
Payment
      ↓
Payment Success
      ↓
Order Completed
```

A successful payment must result in the correct final order state.

---

# 30. Payment Failure

The E2E workflow must also cover payment failure.

Example:

```text
Order
 ↓
Payment Attempt
 ↓
Failure
 ↓
Order Remains Correctly Uncompleted
```

The system must not accidentally mark an unpaid order as completed.

The expected failure state must be explicit.

---

# 31. Duplicate Payment Protection

Where payment operations can be retried, E2E testing should verify that an accidental repeated action does not create an unintended duplicate financial operation.

For example:

```text
Payment
  ↓
Timeout / Unclear Result
  ↓
Retry
```

must not result in an unintended second payment.

Detailed concurrency and idempotency testing belongs to TEST-11 and TEST-12.

---

# 32. Order Completion

After successful payment, the E2E workflow should verify:

* payment is recorded;
* order is completed;
* order is no longer treated as active;
* inventory effects are finalized according to policy;
* cash session totals are updated;
* relevant reports include the order;
* historical state is available.

---

# 33. Order Archiving

Completed orders should move to their defined historical/archive state.

E2E testing should verify:

```text
Active Order
     ↓
Completed
     ↓
Historical / Archived
```

The order must remain retrievable according to retention and access policy.

Archive behavior must not be confused with physical deletion.

---

# 34. Cash Session Impact

A completed payment must affect the active cash session according to the payment method and financial rules.

The E2E test should verify the relationship between:

```text
Order
 ↓
Payment
 ↓
Cash Session
```

The exact calculation rules belong to TEST-12.

---

# 35. Cashier Report

After completed orders, the cashier's operational report should reflect the relevant activity.

E2E tests should verify:

* completed order count;
* payment totals;
* relevant cash movement;
* session association;
* cashier association.

The test should compare business-level results, not database implementation details.

---

# 36. Cash Session Continuation

After completing an order, the cashier must remain able to process another order without reopening the cash session.

The test should verify:

```text
Order 1
  ↓
Completed
  ↓
New Order
  ↓
Order 2
```

This prevents a common class of state-management defects where completion incorrectly resets or closes the active session.

---

# 37. Multiple Orders in One Session

A critical E2E scenario should process multiple orders within one cash session.

Example:

```text
Open Session
   ↓
Order A → Paid
   ↓
Order B → Paid
   ↓
Order C → Paid
   ↓
Close Session
```

The final session state must contain the correct aggregate results.

---

# 38. Cash Session Closing

The cashier must be able to close the active session.

The E2E test should verify:

* active session exists;
* cashier initiates close;
* required cash count is entered;
* cashier comment is captured where required;
* closing operation completes;
* session becomes closed;
* closing report is generated;
* owner notification is produced according to policy.

---

# 39. Cash Count

Closing should verify the actual cash count against the expected amount.

The E2E test should cover:

### Exact Match

```text
Expected Cash = Counted Cash
```

### Shortage

```text
Expected Cash > Counted Cash
```

### Excess

```text
Counted Cash > Expected Cash
```

The resulting status and notifications must match the approved business policy.

Detailed financial calculations belong to TEST-12.

---

# 40. Cash Shortage

A shortage is a high-risk E2E scenario.

The test should verify:

```text
Close Session
      ↓
Shortage Detected
      ↓
Shortage Recorded
      ↓
Prior Cashier Notified
      ↓
Owner Notified According to Policy
```

The exact notification behavior must follow the accepted business rules.

---

# 41. Cash Handover

Where a cashier hands over the register, the E2E workflow should verify:

```text
Current Cashier
      ↓
Handover
      ↓
Incoming Cashier
      ↓
Cash Count
      ↓
Confirmation
      ↓
New Operational Ownership
```

The system should not treat handover as an unrelated new register.

---

# 42. Handover Recount

If the incoming cashier disputes the count, the E2E test should verify the defined recount process.

The workflow must not silently finalize disputed cash.

---

# 43. Cash Correction

Where authorized correction is allowed, E2E tests should verify:

* authorized user can perform correction;
* correction requires the required information;
* correction appears in the resulting report;
* unauthorized user cannot perform it;
* correction limits are enforced.

The accepted business rule limits normal correction to three attempts before privileged reopening is required.

Detailed financial testing belongs to TEST-12.

---

# 44. Register Reopen

After the correction limit is reached, privileged reopening may be required.

The E2E test should verify:

```text
Correction Limit Reached
       ↓
Normal Correction Blocked
       ↓
Privileged Reopen
       ↓
Correction / Reconciliation
```

The test must verify that ordinary cashier permissions do not bypass this boundary.

---

# 45. Owner Notification

The system should notify the Owner for important operational events without requiring Owner involvement in every routine action.

E2E tests should verify notifications for important events such as:

* cash shortage;
* register close where required;
* large refund;
* significant inventory discrepancy.

Routine operations should not generate unnecessary Owner interaction if business policy does not require it.

---

# 46. Refund Workflow

Refunds are an important secondary POS E2E workflow.

A representative flow is:

```text
Completed Order
      ↓
Refund Request
      ↓
Reason
      ↓
Approval
      ↓
Refund
      ↓
Financial Adjustment
      ↓
Order / Refund History
```

The E2E test should verify the complete user-visible workflow.

Detailed financial behavior belongs to TEST-12.

---

# 47. Refund Authorization

The E2E workflow should verify that:

* permitted staff can initiate the appropriate workflow;
* required approval is enforced;
* unauthorized users cannot bypass approval;
* refund reason is recorded;
* final refund state is visible.

Detailed authorization testing belongs to TEST-14.

---

# 48. Large Refund

If the system has a threshold for large refunds, E2E testing should verify that the threshold triggers the intended notification or approval behavior.

The threshold itself should be configurable according to business policy.

---

# 49. POS Failure Scenarios

Critical E2E scenarios should include operational failures.

Examples:

* API temporarily unavailable;
* database temporarily unavailable;
* printer unavailable;
* payment operation fails;
* network connection drops;
* browser/application refresh;
* cashier session interruption;
* worker temporarily unavailable;
* duplicate user action;
* stale UI state.

The expected recovery behavior must be verified.

---

# 50. Browser or POS Refresh

A cashier may accidentally refresh or reopen the POS interface.

E2E testing should verify that:

* active session state remains correct;
* completed orders are not duplicated;
* draft order behavior follows the approved policy;
* cashier can continue safely;
* no financial operation is repeated unintentionally.

---

# 51. Network Interruption

Where the POS operates online and offline, network interruption is an important E2E scenario.

The workflow may be:

```text
Online
  ↓
Order Started
  ↓
Network Lost
  ↓
Offline Operation
  ↓
Network Restored
  ↓
Synchronization
```

Detailed offline and synchronization testing belongs to TEST-10.

TEST-09 should still include at least one complete operational scenario to prove the user-visible experience.

---

# 52. Offline POS Boundary

The offline POS workflow must verify that the cashier can operate within the permitted offline capability.

The test should verify:

* correct device/session state;
* allowed operations remain available;
* prohibited operations are blocked;
* local order state is preserved;
* synchronization occurs after reconnection;
* final server state is correct.

The exact synchronization protocol is outside this document.

---

# 53. POS Session Recovery

If the POS application is interrupted during an active session, E2E testing should verify recovery.

Examples:

```text
Active Cash Session
      ↓
POS Restart
      ↓
Cash Session Still Active
      ↓
Cashier Can Continue
```

A restart must not automatically create a second cash session.

---

# 54. Order Recovery

If an interruption occurs during order processing, the system must reach one of the explicitly supported states.

Possible outcomes:

```text
Draft Preserved
```

or:

```text
Order Not Created
```

or:

```text
Accepted Order Recoverable
```

The system must not create an ambiguous duplicate order.

---

# 55. POS State Machine Testing

The E2E suite should validate major POS state transitions.

### Cash Session

```text
Closed
  ↓
Open
  ↓
Active
  ↓
Closing
  ↓
Closed
```

### Order

```text
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Paid / Completed
  ↓
Historical
```

Actual configurable statuses may differ.

Tests must validate the accepted state model rather than hard-code unnecessary UI labels.

---

# 56. Multi-User Operational Scenarios

Where relevant, E2E tests should verify workflows involving multiple staff members.

Examples:

```text
Cashier
   ↓
Order
   ↓
Cook
   ↓
Order Status
   ↓
Cashier
   ↓
Payment
```

and:

```text
Cashier
   ↓
Close
   ↓
Manager / Owner Review
```

The test should verify that each role sees only the workflow appropriate to its permissions.

---

# 57. E2E Test Data

E2E environments should contain realistic but controlled data.

Typical fixture:

```text
Business
 └── Branch
      ├── Cash Register
      ├── Cashier
      ├── Cook
      ├── Tables
      ├── Products
      ├── Recipes
      ├── Inventory
      └── Printers
```

The fixture should be deterministic.

E2E tests must not depend on manually prepared production-like data.

---

# 58. E2E Environment

A dedicated E2E environment should provide the complete required stack.

Typical components:

```text
Frontend / POS
Backend API
PostgreSQL
Redis / Cache
Queue
Worker
File Storage
Test Printer Adapter
External Service Test Doubles
```

The environment should reproduce the important operational architecture without requiring uncontrolled external systems.

---

# 59. Physical Hardware Testing

Physical hardware testing may be required for:

* receipt printers;
* kitchen printers;
* POS terminals;
* scanners;
* other branch peripherals.

However, physical hardware should not be required for every automated E2E test.

The testing strategy should separate:

```text
Software E2E
```

from:

```text
Physical Hardware Validation
```

This allows normal CI to remain deterministic and efficient.

---

# 60. E2E Test Data Cleanup

E2E tests generate realistic business data.

After execution, the environment must be reset or isolated.

Cleanup must not remove data needed for:

* failure diagnosis;
* test evidence;
* debugging.

Temporary test environments may be disposable.

Persistent shared environments must use isolated test identifiers and controlled cleanup.

---

# 61. E2E Test Naming

Names should describe complete business scenarios.

Good examples:

```text id="8d6p70"
cashier_opens_session_and_completes_takeaway_order
cashier_completes_dine_in_order_and_closes_session
cashier_completes_delivery_order_with_phone_and_address
cashier_receives_payment_failure_without_completing_order
cash_shortage_is_recorded_when_cashier_closes_session
authorized_staff_completes_refund_with_approval
cashier_recovers_active_session_after_pos_restart
completed_orders_are_reflected_in_cash_session_report
```

Avoid names based only on UI controls:

```text id="0kv4z3"
clicks_button_x
opens_modal_y
calls_endpoint_z
```

E2E tests represent business scenarios, not UI implementation.

---

# 62. Critical E2E Suite

The minimum critical POS E2E suite should include:

1. Cashier login.
2. Cash session opening.
3. Dine-in order.
4. Takeaway order.
5. Phone delivery order.
6. Product quantity modification.
7. Order acceptance.
8. Kitchen workflow.
9. Successful payment.
10. Payment failure.
11. Completed order history.
12. Multiple orders in one session.
13. Cash session closing.
14. Exact cash count.
15. Cash shortage.
16. Cash handover.
17. Authorized refund.
18. POS restart recovery.
19. Network interruption / offline boundary where supported.
20. Synchronization after reconnection where applicable.

---

# 63. E2E Coverage by Business Risk

| Workflow          | Risk     | E2E Priority |
| ----------------- | -------- | ------------ |
| Cashier login     | High     | Critical     |
| Cash session open | Critical | Critical     |
| Order creation    | Critical | Critical     |
| Order acceptance  | Critical | Critical     |
| Kitchen flow      | High     | Critical     |
| Payment           | Critical | Critical     |
| Refund            | Critical | Critical     |
| Cash close        | Critical | Critical     |
| Cash handover     | Critical | Critical     |
| Inventory effect  | Critical | Critical     |
| Dine-in           | High     | Critical     |
| Takeaway          | High     | Critical     |
| Delivery          | High     | Critical     |
| Printer           | High     | Important    |
| Reports           | High     | Important    |
| Offline POS       | Critical | Critical     |
| Recovery          | High     | Important    |

---

# 64. E2E Assertions

E2E tests should assert business outcomes rather than only UI appearance.

Weak:

```text
Button is visible.
```

Stronger:

```text
Order is completed and payment is reflected in the active cash session.
```

The UI assertion may still be useful, but the final business state is more important.

---

# 65. Cross-Layer Assertions

Important E2E tests should verify the relationship between user-visible behavior and persistent state.

Example:

```text
Cashier sees:
"Order Completed"

AND

System state:
Order = Completed
Payment = Completed
Cash Session = Updated
```

This prevents false-positive E2E tests where the UI appears correct while the underlying state is incorrect.

---

# 66. E2E Failure Diagnosis

When an E2E test fails, diagnostic evidence should identify:

* test scenario;
* user/role;
* branch;
* order/session identifier;
* request identifier where available;
* relevant timestamps;
* final UI state;
* final database state;
* relevant event/job state;
* failure location.

Sensitive credentials and protected data must not appear in test output.

---

# 67. Flaky E2E Tests

E2E tests are inherently more susceptible to:

* timing problems;
* UI synchronization;
* environment instability;
* asynchronous processing;
* external dependency failures.

A flaky test must not be hidden by unlimited automatic retries.

Retries may be used as a diagnostic aid, but persistent flakiness must be investigated.

---

# 68. E2E Parallelization

E2E tests may run in parallel if their business state is isolated.

Tests must not share:

* active cash registers;
* cash sessions;
* order numbers;
* inventory;
* branch state;
* mutable users;
* device state.

A dedicated business/branch fixture per test or isolated execution context is preferred where necessary.

---

# 69. E2E Performance

E2E tests are expensive.

Therefore:

* maintain a small critical suite;
* avoid duplicating lower-level tests;
* run broad E2E suites at appropriate CI stages;
* run critical smoke workflows earlier;
* isolate slow hardware/external tests;
* avoid arbitrary waits.

E2E testing provides confidence, not maximum test volume.

---

# 70. Release Gates

Production release should require passing critical POS E2E tests.

At minimum:

```text
Cashier Login
     ↓
Cash Session Open
     ↓
Order
     ↓
Payment
     ↓
Order Complete
     ↓
Cash Session Close
```

must succeed in the release environment or an equivalent production-representative environment.

Any failure affecting financial integrity, order completion, inventory integrity, or branch isolation must block release unless an explicit risk decision is recorded.

---

# 71. Regression Testing

Every important POS production defect should produce a regression test when practical.

Examples:

* duplicate order;
* incorrect payment state;
* incorrect cash total;
* order lost after refresh;
* wrong branch order;
* incorrect inventory deduction;
* refund bypass;
* cash shortage not recorded;
* session incorrectly reopened.

The regression test should be placed at the lowest layer capable of reliably reproducing the defect, with an E2E test added when the defect represents a critical user workflow.

---

# 72. Relationship to Financial Testing

TEST-09 proves the complete user-visible payment and cash workflow.

TEST-12 proves detailed financial correctness.

Example:

```text
TEST-09
Cashier completes payment and closes session successfully.

TEST-12
Expected cash, payment totals, refund effects, discrepancy calculations,
and financial invariants are mathematically correct.
```

Both layers are required.

---

# 73. Relationship to Inventory Testing

TEST-09 proves that an order can progress through the complete POS workflow.

TEST-13 proves detailed inventory and recipe correctness.

For example:

```text
TEST-09
Order completes successfully.

TEST-13
Correct recipe components and quantities are deducted according to
inventory rules.
```

---

# 74. Relationship to Security Testing

E2E tests verify the user-visible permission boundaries needed for critical workflows.

TEST-14 performs broader authorization and security testing.

For example:

```text
E2E:
Cashier cannot perform an Owner-only operation.

TEST-14:
System-wide authorization and privilege-escalation resistance are tested.
```

---

# 75. Relationship to Offline Testing

TEST-09 verifies the POS user experience around the offline boundary.

TEST-10 provides deeper testing of:

* synchronization;
* conflicts;
* retries;
* replay protection;
* operation ordering;
* offline authorization;
* reconciliation.

---

# 76. Anti-Patterns

The following practices are prohibited or strongly discouraged.

## 76.1 Testing Only the UI

A visually correct UI does not prove business correctness.

---

## 76.2 Testing Only the Happy Path

Critical failures must have E2E coverage.

---

## 76.3 Replacing Business Assertions With Screenshots

Screenshots may provide evidence, but they do not prove persistent business state.

---

## 76.4 One Huge E2E Test

A single enormous workflow is difficult to diagnose and maintain.

Critical workflows should be separated into meaningful scenarios.

---

## 76.5 Excessive E2E Coverage

Every validation rule does not need an E2E test.

Lower layers should provide broad coverage.

---

## 76.6 Hard-Coded Timing

Fixed delays create slow and flaky tests.

---

## 76.7 Shared Cash Session

Multiple parallel E2E tests must not mutate the same cash session unless concurrency is the explicit subject of the test.

---

## 76.8 Real Production Payments

Production financial operations must never be used for normal automated testing.

Controlled test environments must be used.

---

# 77. E2E Review Checklist

For every critical E2E scenario:

* [ ] Does it represent a real business workflow?
* [ ] Does it begin with a realistic user state?
* [ ] Is the correct business selected?
* [ ] Is the correct branch selected?
* [ ] Is the correct role used?
* [ ] Is the cash session state correct?
* [ ] Is the order state correct?
* [ ] Is payment verified?
* [ ] Is the final business state verified?
* [ ] Are important side effects verified?
* [ ] Is failure behavior covered where required?
* [ ] Is test data isolated?
* [ ] Is the scenario deterministic?
* [ ] Is the test independent of unrelated scenarios?
* [ ] Is the test valuable enough to justify E2E execution cost?

---

# 78. Mandatory E2E Rules

The following rules are mandatory.

1. Critical POS workflows must have E2E coverage.
2. E2E tests must represent real business scenarios.
3. Cash session lifecycle must be tested.
4. Order creation and completion must be tested.
5. Payment success and important payment failures must be tested.
6. Cash session closing must be tested.
7. Cash shortage behavior must be tested.
8. Cash handover must be tested where supported.
9. Dine-in, takeaway, and phone delivery workflows must be represented.
10. Important order status transitions must be tested.
11. Critical inventory and financial side effects must be verified at the appropriate level.
12. E2E tests must verify final business state, not only UI appearance.
13. POS recovery after interruption must be tested.
14. Offline boundaries must be tested where supported.
15. Critical E2E tests must participate in release validation.
16. E2E tests must use isolated and controlled test data.
17. Automated E2E tests must not perform real production financial operations.
18. Arbitrary sleeps must not be used as the primary synchronization mechanism.
19. E2E tests must not be used as a replacement for lower-level tests.
20. Important production POS defects should produce regression coverage.

---

# 79. POS E2E Invariants

### Invariant 1

A cashier cannot perform normal order operations without the required active cash session.

### Invariant 2

Every completed POS order remains associated with the correct business and branch.

### Invariant 3

A successful payment results in the correct completed order state.

### Invariant 4

A failed payment does not silently complete an unpaid order.

### Invariant 5

Repeated payment attempts cannot create unintended duplicate financial effects.

### Invariant 6

Completed orders affect the correct cash session.

### Invariant 7

Cash session closing produces a consistent final state.

### Invariant 8

Cash shortages are recorded and handled according to policy.

### Invariant 9

Cash handover preserves correct operational ownership.

### Invariant 10

POS restart or temporary interruption does not create duplicate financial or order operations.

### Invariant 11

Orders from one branch cannot silently appear in another branch's operational workflow.

### Invariant 12

Critical user-visible workflows correspond to valid persistent business state.

---

# 80. Acceptance Criteria

This document is considered correctly implemented when:

* a critical POS happy path exists;
* cashier authentication is covered;
* cash session opening is covered;
* order creation is covered;
* dine-in, takeaway, and delivery workflows are covered;
* order acceptance is covered;
* kitchen/status workflow is covered;
* payment success is covered;
* payment failure is covered;
* completed order state is verified;
* cash session impact is verified;
* cash session closing is covered;
* cash shortage is covered;
* handover is covered;
* refund workflow is covered where applicable;
* POS interruption recovery is covered;
* offline boundaries are covered where supported;
* critical business state is verified beyond UI appearance;
* critical E2E tests participate in release validation;
* E2E test data and environments are deterministic and isolated.

---

# 81. Final E2E Testing Rule

End-to-end testing must answer:

> **Can a real branch employee complete a critical business operation from start to finish, and does the entire system reach the correct final state?**

For POS, the most important complete workflow is:

```text
Cashier Login
      ↓
Correct Branch
      ↓
Cash Session Open
      ↓
Order Creation
      ↓
Order Acceptance
      ↓
Kitchen / Preparation
      ↓
Payment
      ↓
Order Completion
      ↓
Cash / Financial Update
      ↓
Order History
      ↓
Cash Session Close
      ↓
Final Report
```

A POS system is not considered production-ready merely because individual screens, endpoints, or services work independently.

The complete operational workflow must also work.

**The purpose of TEST-09 is therefore to prove that the FastFood POS behaves correctly as one complete business system from the cashier's perspective while preserving the underlying financial, inventory, security, branch, and operational state.**

