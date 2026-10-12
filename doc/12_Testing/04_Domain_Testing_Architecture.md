# 04 — Domain Testing Architecture

**Document ID:** TEST-04
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-03
**Related:** TEST-05, TEST-06, TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14

---

## 1. Purpose

This document defines the architecture and strategy for testing FastFood domain rules, business invariants, state transitions, and business behavior.

Domain testing verifies that the system's business model behaves correctly regardless of:

* database implementation;
* API transport;
* frontend implementation;
* infrastructure;
* external services;
* deployment environment.

The primary question is:

> Does the business model allow valid business operations and reject invalid ones according to the defined rules?

Domain tests provide the foundation for higher-level application, integration, and end-to-end tests.

---

## 2. Scope

This document covers testing of:

* domain entities;
* value objects;
* domain services;
* business rules;
* domain invariants;
* state transitions;
* business constraints;
* calculations;
* eligibility rules;
* lifecycle rules;
* relationships between domain concepts;
* valid and invalid business operations;
* domain-level error conditions;
* historical/business-state preservation.

This document does not define:

* database integration testing;
* API contract testing;
* frontend testing;
* infrastructure testing;
* production load testing;
* detailed security testing;
* concurrency testing methodology;
* detailed financial testing;
* detailed inventory testing.

Those concerns are covered by their dedicated testing documents.

---

# 3. Domain Testing Role

Domain tests validate the business meaning of the system.

They should answer questions such as:

* Can an order move from one state to another?
* Can a paid order be paid again?
* Can an invalid refund be created?
* Can inventory become negative?
* Can a recipe be changed without the required approval?
* Can a semi-finished product correctly represent its components?
* Can a cashier close a session that is already closed?
* Can an expired subscription continue to authorize restricted functionality?
* Can a branch use a product that is not available to that branch?
* Can a discount produce an invalid final price?
* Can a business rule be bypassed by supplying an unexpected value?

Domain tests therefore focus on **business behavior rather than implementation details**.

---

# 4. Domain Testing Principles

## 4.1 Test Business Meaning

Tests should describe business behavior rather than internal implementation.

Prefer:

```text
when a paid order is refunded,
the refund amount cannot exceed the refundable amount
```

over:

```text
RefundService calls calculateRefund()
```

The first verifies a business rule.

The second verifies implementation structure.

---

## 4.2 Test Invariants Explicitly

Important domain invariants must have explicit tests.

An invariant is a condition that must remain true whenever the relevant domain state is valid.

Examples:

```text
Inventory quantity must never become negative.
```

```text
A closed cash session cannot accept normal cashier operations.
```

```text
A paid order cannot return to an unpaid state.
```

```text
A recipe version used by historical operations must remain historically identifiable.
```

---

## 4.3 Test Both Acceptance and Rejection

Domain testing must verify:

1. valid operations are accepted;
2. invalid operations are rejected;
3. boundary values behave correctly;
4. state transitions are controlled;
5. invalid combinations cannot produce valid-looking states.

Testing only successful scenarios is insufficient.

---

## 4.4 Business Rules Are Executable Requirements

Where a business requirement can be expressed as a deterministic rule, the rule should be represented by executable tests.

Example:

```text
Given:
- current stock = 5
- required quantity = 3

When:
- the product is sold

Then:
- remaining stock = 2
```

And:

```text
Given:
- current stock = 2
- required quantity = 3

When:
- the product is sold

Then:
- the operation is rejected
- stock remains 2
```

---

## 4.5 Domain Tests Must Be Deterministic

Domain tests must not depend on:

* network availability;
* database timing;
* printer availability;
* external APIs;
* random external state;
* uncontrolled system time;
* execution order.

Deterministic testing principles are defined in TEST-03.

---

# 5. Domain Model Test Boundaries

Domain tests should normally operate around the following conceptual boundaries:

```text
Domain Entity
     │
     ├── Value Object
     │
     ├── Domain Rule
     │
     ├── State Transition
     │
     └── Domain Service
            │
            └── Business Decision
```

The test should observe the resulting business state or business decision.

Infrastructure should remain outside the domain test boundary.

---

# 6. Domain Entities

Domain entities represent business concepts that have identity and lifecycle.

Examples include:

* Business;
* Branch;
* Employee;
* Role;
* Permission;
* Product;
* Recipe;
* Recipe Version;
* Semi-Finished Product;
* Menu Item;
* Order;
* Order Item;
* Payment;
* Refund;
* Cash Session;
* Cash Handover;
* Inventory Item;
* Stock Movement;
* Expense;
* Subscription;
* Device;
* Attendance record.

Domain tests should verify the valid behavior of these entities.

---

## 6.1 Entity Identity

Tests should verify that identity is handled according to business semantics.

For example:

* two different orders remain different orders;
* historical references remain distinguishable;
* customer-facing order numbers may reset according to the business cycle;
* internal identifiers remain stable;
* archived entities remain distinguishable from newly created entities.

The distinction between internal identity and customer-facing identifiers must be explicitly tested where applicable.

---

## 6.2 Entity Lifecycle

Entities with lifecycle states should have explicit transition tests.

Example:

```text
Created
   ↓
Active
   ↓
Completed
   ↓
Archived
```

Tests must verify:

* valid transitions;
* invalid transitions;
* terminal states;
* repeated transitions;
* required conditions for transitions.

---

# 7. Value Objects

Value objects represent domain values whose meaning is determined by their value rather than independent identity.

Examples may include:

* Money;
* Quantity;
* Percentage;
* Product Code;
* Branch Scope;
* Order Number;
* Date Range;
* Payroll Rate;
* Subscription Period.

Tests should verify:

* valid construction;
* invalid construction;
* boundary values;
* equality semantics;
* normalization rules;
* arithmetic rules;
* invalid combinations.

Example:

```text
Money(amount = -100)
→ rejected when negative money is not valid for that domain operation
```

The exact validity depends on the business concept.

A negative value must not automatically be considered invalid everywhere; the test must follow the relevant domain rule.

---

# 8. Business Rule Testing

Business rules should be tested independently from the mechanism used to execute them.

Typical rule categories include:

| Rule Category | Example                                                  |
| ------------- | -------------------------------------------------------- |
| Eligibility   | Employee can perform an operation only when eligible     |
| State         | Closed order cannot receive normal payment               |
| Quantity      | Stock cannot become negative                             |
| Calculation   | Final price follows configured discount rules            |
| Approval      | Certain changes require approval                         |
| Scope         | Branch-specific configuration applies only where allowed |
| Lifecycle     | Archived entity cannot behave as active                  |
| Subscription  | Restricted functionality is unavailable after expiry     |
| Refund        | Refund cannot exceed refundable amount                   |
| Recipe        | Recipe changes follow version/approval rules             |
| Cash          | Closed session cannot accept normal cashier operations   |

Each important rule should have positive and negative tests.

---

# 9. Invariant Testing

## 9.1 Definition

An invariant is a business condition that must remain true throughout valid domain operations.

Examples:

```text
Stock quantity >= 0
```

```text
Refunded amount <= refundable amount
```

```text
Closed cash session cannot accept normal cash operations
```

```text
Completed order cannot return to an earlier operational state
```

```text
Archived recipe version remains historically identifiable
```

---

## 9.2 Invariant Categories

FastFood domain invariants should be grouped into:

### Identity invariants

* identities remain unique within their required scope;
* historical identities remain distinguishable;
* customer-facing identifiers do not replace internal identity.

### Lifecycle invariants

* invalid state transitions are rejected;
* terminal states cannot be reopened through normal domain operations;
* archived records cannot silently behave as active records.

### Financial invariants

* payment amounts follow business rules;
* refund amounts cannot exceed refundable amounts;
* financial totals remain internally consistent;
* invalid monetary states are rejected.

### Inventory invariants

* negative stock is not permitted;
* stock movements have valid quantities;
* recipe consumption follows configured quantities;
* inventory calculations preserve required precision.

### Recipe invariants

* recipe components follow valid quantities;
* semi-finished products maintain valid component relationships;
* historical recipe versions remain identifiable;
* invalid recipe states cannot be activated.

### Order invariants

* order lifecycle follows valid transitions;
* payment state is consistent with order state;
* completed/archived orders cannot receive arbitrary normal mutations;
* order item quantities follow domain rules.

### Cash invariants

* only valid cash-session states allow corresponding operations;
* closed sessions cannot accept normal cashier transactions;
* handover follows required state transitions;
* correction limits are respected.

### Subscription invariants

* subscription state determines allowed business capabilities;
* expiration does not silently reactivate restricted functionality;
* historical business data remains distinguishable from active functionality.

### Scope invariants

* branch-specific business state remains associated with its branch;
* business-wide state is not accidentally converted into branch-local state;
* domain operations respect the defined ownership/scope model.

---

# 10. State Transition Testing

Many FastFood concepts are state machines.

A domain state machine should be tested as:

```text
Current State
      │
      │ command
      ▼
Business Rule Evaluation
      │
   ┌──┴──┐
   │     │
 Valid  Invalid
   │     │
   ▼     ▼
New State Rejection
```

---

## 10.1 Transition Test Matrix

For each stateful domain object, tests should define:

| Current State         | Operation         | Expected Result                          |
| --------------------- | ----------------- | ---------------------------------------- |
| Valid state           | Valid operation   | New valid state                          |
| Valid state           | Invalid operation | Rejection                                |
| Terminal state        | Normal operation  | Rejection                                |
| Unknown/invalid state | Any operation     | Rejection                                |
| Repeated operation    | Same operation    | Defined idempotent or rejection behavior |

---

## 10.2 Example: Order Lifecycle

A conceptual order lifecycle may include:

```text
Created
   ↓
Accepted
   ↓
Preparing
   ↓
Ready
   ↓
Completed
   ↓
Archived
```

Domain tests must verify the actual accepted state model rather than assume that every possible transition is allowed.

For example:

* `Created → Accepted` may be valid;
* `Accepted → Preparing` may be valid;
* `Completed → Preparing` must normally be rejected;
* `Archived → Preparing` must be rejected.

The exact states and transitions are defined by the domain model.

---

# 11. Order Domain Testing

Order testing should verify business behavior around:

* order creation;
* order type;
* order items;
* quantities;
* status;
* pricing;
* discounts;
* recipe-dependent availability;
* payment state;
* completion;
* cancellation;
* archival;
* customer delivery information where applicable.

Tests should cover:

```text
Valid order
Invalid order
Empty order
Invalid quantity
Unavailable product
Recipe-related restriction
Price calculation
Discount application
Payment transition
Completion
Invalid state transition
```

The detailed POS workflow is covered by TEST-09.

---

# 12. Payment and Refund Domain Rules

Domain tests should establish fundamental financial rules without duplicating the detailed financial test strategy from TEST-12.

Examples:

```text
Payment cannot exceed the allowed business conditions.
```

```text
Refund cannot exceed refundable amount.
```

```text
A completed refund changes the refundable state consistently.
```

```text
A completed payment cannot silently become unpaid.
```

Tests should cover:

* valid payment;
* invalid payment;
* repeated payment;
* partial payment if supported;
* refund eligibility;
* refund boundaries;
* refund reason requirements;
* approval-dependent operations;
* invalid refund amount;
* already-refunded amount.

---

# 13. Cash Session Domain Testing

Cash sessions have explicit lifecycle rules.

Tests should verify:

```text
Closed
  ↓
Opened
  ↓
Active
  ↓
Closing
  ↓
Closed
```

The exact state model is defined by the domain.

Important rules include:

* only a valid opening operation creates an active session;
* an already-open session cannot be opened again through normal flow;
* a closed session cannot accept normal cashier operations;
* closing requires required business information;
* handover follows its required state;
* correction limits are enforced;
* privileged reopening rules are explicit.

Detailed cash and financial testing is covered by TEST-12.

---

# 14. Inventory Domain Testing

Inventory is governed by strong domain invariants.

Core tests should verify:

```text
stock_after = stock_before + stock_in - stock_out ± allowed_adjustments
```

subject to the domain's actual movement model.

Tests should cover:

* stock addition;
* stock deduction;
* insufficient stock;
* zero quantity;
* invalid quantity;
* recipe consumption;
* semi-finished product consumption;
* stock adjustment;
* shrink/yield behavior;
* FIFO-related domain decisions;
* inventory discrepancy;
* product availability.

The detailed inventory and recipe test architecture is defined by TEST-13.

---

# 15. Recipe and Semi-Finished Product Testing

Recipes represent business rules rather than simple static data.

Tests should verify:

* valid recipe composition;
* required quantities;
* raw ingredient relationships;
* semi-finished product relationships;
* recipe activation;
* recipe approval;
* archived recipe behavior;
* historical recipe identification;
* recipe-dependent stock requirements;
* invalid component relationships;
* recipe modification rules.

Example:

```text
Semi-finished Product:
1 kg meat
200 g mayonnaise
defined spices
```

Tests should verify that the resulting domain composition is interpreted consistently.

A recipe must be testable even when the current physical inventory is empty, because recipe definition and current stock availability are separate domain concepts.

---

# 16. Pricing and Discount Rules

Domain tests should verify:

* base price;
* branch-specific price where permitted;
* discount eligibility;
* discount boundaries;
* final price calculation;
* invalid discount values;
* price changes;
* product/recipe modification effects on price where defined;
* historical transaction price preservation.

Tests must distinguish between:

```text
Configured price
```

and:

```text
Historical transaction price
```

A later price change must not silently rewrite the financial meaning of an already completed transaction.

---

# 17. Employee and Permission-Related Domain Rules

Authorization testing is primarily covered by TEST-14, but domain rules that define business eligibility should also be tested.

Examples:

* an employee may have a role;
* a role may have permitted capabilities;
* branch assignment affects business scope;
* Owner and Manager responsibilities follow domain rules;
* a Manager cannot perform an operation explicitly restricted by the business model;
* employee lifecycle changes affect eligibility where defined.

The domain test should verify the business rule, while security tests verify the complete authorization boundary.

---

# 18. Subscription Domain Testing

Subscription state affects business capability.

Tests should verify:

* active subscription;
* approaching expiration;
* expired subscription;
* restricted functionality;
* data-view rules after expiration;
* reactivation;
* data-deletion eligibility after the defined retention period;
* subscription-related state transitions.

A domain test must distinguish:

```text
Data exists
```

from:

```text
Business functionality is currently enabled
```

Expiration must not imply immediate destruction of data.

The exact two-month post-expiration deletion policy must remain consistent with the approved business rules.

---

# 19. Branch and Business Scope Rules

Domain tests should verify scope-related business rules such as:

* branch belongs to the correct business;
* branch-specific configuration remains branch-specific;
* global configuration applies only where intended;
* branch overrides follow defined rules;
* cross-branch domain operations are allowed only where explicitly defined.

These tests validate business semantics.

Security enforcement of tenant and branch isolation is covered by TEST-14 and the Security documentation.

---

# 20. Archive and Historical State Testing

FastFood uses archival instead of deletion for many business records.

Domain tests should verify:

* active records can become archived where allowed;
* archived records are not treated as active;
* historical transactions remain understandable;
* archived recipes remain identifiable;
* archived products do not unexpectedly appear in active business flows;
* historical prices and relationships remain meaningful.

Archival must not create hidden changes to historical financial or inventory meaning.

---

# 21. Error and Rejection Testing

Domain rejection is part of normal business behavior.

Tests should verify that invalid operations produce:

1. a defined domain rejection;
2. no invalid state transition;
3. no partial business state;
4. no silent acceptance;
5. sufficient information for the application layer to respond appropriately.

Examples:

```text
Insufficient stock
Invalid refund amount
Invalid order transition
Invalid recipe state
Invalid cash-session operation
Invalid discount
Invalid quantity
Invalid subscription state
```

Domain tests should focus on the business decision, not on HTTP status codes or API response formatting.

---

# 22. Boundary Testing

Important domain rules require boundary-value tests.

Examples:

```text
quantity = 0
quantity = minimum valid quantity
quantity = maximum valid quantity
quantity = maximum + 1
```

For monetary values:

```text
minimum valid amount
exact boundary
just below boundary
just above boundary
```

For percentages:

```text
0%
minimum valid value
maximum valid value
maximum + 1
```

For correction limits:

```text
0 corrections
1 correction
maximum allowed corrections
maximum + 1
```

Boundary values should come from business rules rather than arbitrary test numbers.

---

# 23. Cross-Domain Business Rules

Some business rules involve more than one domain concept.

Examples:

```text
Order
  ↓
Recipe
  ↓
Inventory
```

or:

```text
Cash Session
  ↓
Payment
  ↓
Order
```

or:

```text
Subscription
  ↓
Business Capability
```

Cross-domain domain tests should verify the business rule when it genuinely belongs to the domain layer.

However, orchestration across application components should be tested at the application/integration levels defined by TEST-05 and TEST-08.

---

# 24. Domain Invariant Catalog

The project should maintain a living catalog of important domain invariants.

Example:

| ID          | Invariant                                                       | Domain        |
| ----------- | --------------------------------------------------------------- | ------------- |
| DOM-INV-001 | Inventory cannot become negative                                | Inventory     |
| DOM-INV-002 | Refund cannot exceed refundable amount                          | Finance       |
| DOM-INV-003 | Closed cash session rejects normal operations                   | Cash          |
| DOM-INV-004 | Completed order cannot return to an earlier normal state        | Order         |
| DOM-INV-005 | Historical transaction price remains stable                     | Pricing       |
| DOM-INV-006 | Archived recipe remains historically identifiable               | Recipe        |
| DOM-INV-007 | Invalid recipe state cannot become active                       | Recipe        |
| DOM-INV-008 | Subscription state controls defined capabilities                | Subscription  |
| DOM-INV-009 | Branch-scoped business state remains associated with its branch | Branch        |
| DOM-INV-010 | Invalid quantities are rejected                                 | Shared Domain |

The catalog should evolve with the domain model.

---

# 25. Property-Oriented Domain Testing

Where a rule can be expressed as a general property, tests may use property-based techniques.

Examples:

### Inventory

For valid stock movements:

```text
resulting_stock = initial_stock + net_valid_movement
```

### Discounts

For valid discounts:

```text
final_price <= applicable_base_price
```

subject to the configured discount model.

### Quantities

For valid positive quantities:

```text
quantity > 0
```

### Refunds

```text
total_refunded <= refundable_amount
```

Property-based testing is especially useful for discovering unexpected combinations of valid values.

It must not replace explicit examples for important business scenarios.

---

# 26. Example-Based Testing

Important business rules should also have explicit scenario tests.

Example:

```text
Given:
- stock = 10
- recipe requires 3 units

When:
- one product is sold

Then:
- stock = 7
```

Negative scenario:

```text
Given:
- stock = 2
- recipe requires 3 units

When:
- one product is sold

Then:
- operation is rejected
- stock remains 2
```

Example-based tests make business requirements understandable to developers, reviewers, and future maintainers.

---

# 27. Domain Test Organization

Domain tests should be organized around business concepts rather than technical implementation files where practical.

Example:

```text
tests/
└── domain/
    ├── orders/
    ├── payments/
    ├── refunds/
    ├── cash/
    ├── inventory/
    ├── recipes/
    ├── products/
    ├── pricing/
    ├── employees/
    ├── subscriptions/
    └── branches/
```

The exact repository structure may differ.

The important principle is that a developer should be able to locate tests by domain behavior.

---

# 28. Test Naming

Domain test names should express business behavior.

Prefer:

```text
rejects_refund_when_amount_exceeds_refundable_balance
```

```text
does_not_allow_stock_to_become_negative
```

```text
rejects_payment_for_closed_order
```

```text
requires_approval_before_activating_changed_recipe
```

```text
preserves_historical_price_after_product_price_change
```

Avoid names based only on implementation:

```text
test_service_method_3
```

```text
test_internal_flag
```

---

# 29. Domain Test Fixtures

Fixtures should represent meaningful business states.

Useful fixtures may include:

```text
valid_order
paid_order
completed_order
open_cash_session
closed_cash_session
available_inventory
insufficient_inventory
approved_recipe
draft_recipe
archived_recipe
active_subscription
expired_subscription
```

Fixtures should remain small and explicit.

A fixture should not hide important business conditions.

---

# 30. Test Independence

Each domain test should establish the business state it requires.

Tests must not depend on:

* another test running first;
* shared mutable global state;
* previous test results;
* execution order;
* hidden persistent state.

This follows the isolation principles established in TEST-03.

---

# 31. Domain Testing and Unit Testing

Domain tests are frequently implemented as unit tests.

However, the concepts are different:

| Unit Testing                      | Domain Testing                            |
| --------------------------------- | ----------------------------------------- |
| Defines test execution boundary   | Defines business behavior being verified  |
| Focuses on isolation              | Focuses on domain correctness             |
| Controls dependencies             | Verifies business rules                   |
| Uses test doubles where necessary | Verifies invariants and state transitions |
| Technical test architecture       | Business-semantic test architecture       |

Therefore:

> Domain testing is a business-focused testing responsibility that can be implemented using unit-testing techniques.

TEST-03 defines how isolated unit tests should be structured.

TEST-04 defines what domain behavior those tests must prove.

---

# 32. Domain Testing and Application Testing

Domain tests should not attempt to verify the entire application workflow.

For example:

### Domain test

```text
Refund amount cannot exceed refundable amount.
```

### Application test

```text
Refund request is accepted,
permission is evaluated,
domain refund operation is executed,
audit event is created,
notification is generated.
```

The first belongs to domain testing.

The second belongs to application/use-case testing.

---

# 33. Domain Testing and Database Testing

Domain tests should not depend on PostgreSQL to prove a pure business rule.

For example:

```text
Stock cannot become negative.
```

can be verified at the domain level.

Database integration tests should additionally verify that the persistence layer correctly stores and retrieves the resulting state.

Both layers are valuable because they provide different evidence.

---

# 34. Domain Testing and API Testing

API tests verify the external contract.

Domain tests verify the business decision behind the contract.

For example:

```text
API:
POST /refunds
```

may be tested for:

* request schema;
* authentication;
* authorization;
* response contract.

The domain test verifies:

```text
refund_amount <= refundable_amount
```

These responsibilities must remain separate.

---

# 35. Domain Testing and Concurrency

Some invariants can be tested without concurrency.

Concurrency-specific behavior belongs to TEST-11.

For example:

```text
Refund cannot exceed refundable amount
```

is a domain invariant.

But:

```text
Two simultaneous refund requests cannot both consume the same refundable balance
```

is a concurrency/consistency concern.

The first belongs to domain testing.

The second requires higher-level concurrency testing.

---

# 36. Domain Test Coverage

Coverage should be evaluated by business risk rather than line count alone.

High-priority domain behavior includes:

* order lifecycle;
* payment;
* refund;
* cash sessions;
* inventory deduction;
* recipe calculation;
* semi-finished products;
* pricing;
* discounts;
* subscription restrictions;
* branch scope;
* employee eligibility;
* approval rules;
* archival;
* historical state preservation.

A high code-coverage percentage does not prove that domain invariants are sufficiently tested.

---

# 37. Mutation Testing

Mutation testing may be applied to critical domain rules.

Examples of useful mutations:

```text
< becomes <=
```

```text
+ becomes -
```

```text
allowed state becomes rejected state
```

```text
refund limit removed
```

```text
stock validation removed
```

If the test suite does not detect an intentionally introduced business-rule mutation, the relevant domain tests may be insufficient.

Mutation testing should focus on high-risk domain logic rather than every line of the system.

---

# 38. Regression Protection

Every confirmed domain defect should normally result in a regression test when practical.

Example:

```text
Defect:
A discount boundary allowed an invalid final price.

Required response:
1. identify the business rule;
2. add a regression test;
3. fix the domain behavior;
4. verify the regression test;
5. run the relevant broader test set.
```

This prevents previously discovered business defects from silently returning.

---

# 39. Domain Testing for Offline Operations

Offline behavior must preserve domain correctness.

Domain rules should not become weaker simply because the operation is performed offline.

Examples:

* inventory rules remain valid;
* order state rules remain valid;
* cash rules remain valid;
* subscription validity rules remain valid within the approved offline policy;
* operation integrity remains valid.

Synchronization-specific behavior is covered by TEST-10.

The domain layer must remain authoritative for business validity wherever the operation is evaluated.

---

# 40. Domain Testing for Auditability

Where the domain requires an important business transition to remain explainable, tests should verify that the transition preserves the information required by the domain.

Examples include:

* refund reason;
* approval-dependent change;
* inventory discrepancy;
* cash correction;
* recipe version change;
* subscription state change.

The test should verify the domain's required business information, while detailed audit implementation is handled by application/security layers.

---

# 41. Failure-Oriented Domain Testing

Critical domain tests should deliberately attempt invalid operations.

Examples:

```text
Pay twice
Refund too much
Deduct unavailable stock
Use invalid quantity
Activate invalid recipe
Close already closed session
Modify terminal order state
Apply invalid discount
Use expired business capability
Perform invalid branch-scoped operation
```

The expected result must be explicit.

Invalid input is not an exceptional testing case; it is a normal part of domain behavior.

---

# 42. Domain Test Review Checklist

Every important domain feature should be reviewed against:

* [ ] Main valid business scenario tested.
* [ ] Invalid scenario tested.
* [ ] Boundary values tested.
* [ ] Domain invariant identified.
* [ ] State transitions tested where applicable.
* [ ] Terminal states tested.
* [ ] Repeated operations tested.
* [ ] Historical behavior tested where applicable.
* [ ] Business rejection behavior tested.
* [ ] Important cross-domain rules identified.
* [ ] Regression coverage exists for known defects.
* [ ] Tests describe business behavior clearly.
* [ ] Infrastructure is not required for pure domain behavior.
* [ ] Higher-level integration responsibilities remain outside domain tests.

---

# 43. Mandatory Domain Testing Rules

The following rules are mandatory:

1. Every critical business invariant must have explicit test coverage.
2. Critical state transitions must have valid and invalid transition tests.
3. Business rules must be tested independently of API and frontend behavior.
4. Invalid business operations must be tested explicitly.
5. Boundary conditions must be tested for important rules.
6. Historical business meaning must be protected by tests where required.
7. Domain tests must remain deterministic.
8. Domain tests must not rely on external infrastructure to prove pure business behavior.
9. Domain tests must not replace application, integration, or end-to-end testing.
10. High-risk financial, inventory, order, recipe, subscription, and cash rules require stronger test depth.
11. Confirmed domain defects should produce regression tests where practical.
12. Domain test names must communicate business behavior.
13. Domain invariants must remain documented and reviewable.
14. Domain rules must remain valid regardless of whether an operation is initiated through the frontend, API, offline workflow, or another supported entry point.
15. No test should make an invalid domain state appear valid merely to simplify the test.

---

# 44. Domain Testing Invariants

The testing architecture itself must preserve these invariants:

```text
Domain tests verify business behavior, not implementation structure.
```

```text
Critical business invariants have explicit tests.
```

```text
Invalid business operations are tested.
```

```text
Valid state transitions are tested.
```

```text
Invalid state transitions are rejected.
```

```text
Historical business meaning is protected.
```

```text
Domain correctness does not depend on infrastructure availability.
```

```text
Domain tests remain deterministic and independently executable.
```

```text
Business rules cannot be considered sufficiently tested only because happy-path tests pass.
```

```text
High-risk business rules receive greater testing depth.
```

---

# 45. Acceptance Criteria

This document is considered correctly implemented when:

* the domain-testing responsibility is clearly separated from general unit testing;
* critical domain rules are identifiable;
* important invariants are explicitly testable;
* state transitions have defined testing expectations;
* invalid business operations are covered;
* order, payment, refund, cash, inventory, recipe, pricing, subscription, branch, and archival rules have clear domain-testing expectations;
* domain tests remain independent from API and persistence concerns;
* specialized testing documents can build on the domain invariant catalog;
* business defects can be converted into regression tests;
* domain test coverage is evaluated by business risk rather than code coverage alone.

---

# 46. Relationship to the Testing Architecture

The testing hierarchy is:

```text
TEST-01
Testing Architecture Overview
        │
        ▼
TEST-02
Testing Strategy and Test Pyramid
        │
        ▼
TEST-03
Unit Testing Architecture
        │
        ▼
TEST-04
Domain Testing Architecture
        │
        ├── TEST-05 Application / Use Cases
        ├── TEST-06 Repository / Database
        ├── TEST-08 Integration
        ├── TEST-09 End-to-End / POS
        ├── TEST-10 Offline / Synchronization
        ├── TEST-11 Concurrency / Consistency
        ├── TEST-12 Financial / Cash
        ├── TEST-13 Inventory / Recipe
        └── TEST-14 Authentication / Authorization
```

TEST-04 therefore establishes the business correctness foundation on which the later specialized test architectures depend.

---

# 47. Final Rule

The purpose of domain testing is not to prove that the code executes.

It is to prove that the system's business model behaves correctly.

A domain test suite is successful when it can provide strong evidence that:

```text
Valid business operations are accepted.
Invalid business operations are rejected.
Business invariants remain true.
State transitions remain controlled.
Historical business meaning remains stable.
Critical rules are protected against regression.
```

For FastFood, domain correctness is a foundational requirement for financial integrity, inventory integrity, POS reliability, subscription behavior, branch operations, and overall system trustworthiness.

