# 15. Frontend Testing Architecture

**Document ID:** TEST-15
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing architecture for the FastFood ERP frontend.

Frontend testing must verify that the user interface correctly represents and interacts with the business system while preserving the rules enforced by the backend and security architecture.

The frontend is responsible for:

* presenting available functionality;
* collecting user input;
* validating user interaction where appropriate;
* displaying application state;
* handling loading and failure states;
* presenting permissions and available actions;
* communicating with backend APIs;
* supporting POS workflows;
* supporting online and offline user interaction;
* displaying synchronization state;
* presenting reports and operational information;
* providing consistent navigation and user experience.

The frontend must not become the authoritative source of business security or business integrity.

The central principle is:

> **Frontend tests verify user-visible behavior and client-side correctness; backend and server-side authorization remain authoritative for business rules, security, and data integrity.**

---

# 2. Scope

This document covers frontend testing for:

* UI components;
* pages;
* layouts;
* navigation;
* forms;
* validation;
* tables;
* filters;
* search;
* pagination;
* dialogs and modals;
* notifications;
* loading states;
* error states;
* empty states;
* permission-aware UI;
* branch-aware UI;
* tenant-aware UI;
* POS workflows;
* order entry;
* payment interaction;
* cash-session interaction;
* inventory interaction;
* recipe interaction;
* employee management;
* reports;
* file import/export interfaces;
* offline UI;
* synchronization indicators;
* responsive behavior;
* accessibility;
* browser behavior;
* frontend API integration;
* frontend state management;
* frontend caching;
* frontend error handling;
* E2E workflows.

This document does not replace:

* API contract testing;
* backend authorization testing;
* domain testing;
* database testing;
* offline synchronization testing;
* security testing;
* performance testing.

Those concerns are covered by the corresponding testing documents in `docs/12_Testing/`.

---

# 3. Frontend Testing Principles

Frontend testing MUST follow these principles:

1. Test observable user behavior rather than implementation details.
2. Prefer testing at the lowest reliable level.
3. Use integration tests when multiple frontend components must interact.
4. Use E2E tests for critical user workflows.
5. Do not duplicate every component behavior in E2E tests.
6. Backend authorization remains authoritative.
7. Hidden UI controls are not considered security enforcement.
8. Loading, error, empty, offline, and synchronization states are first-class behaviors.
9. POS workflows require stronger E2E coverage than low-risk configuration screens.
10. Tests must be deterministic.
11. Tests must not depend on arbitrary timing.
12. User interaction should be represented realistically.
13. Accessibility must be tested as part of frontend quality.
14. Responsive behavior must be tested for supported device classes.
15. Critical business states must be reflected correctly in the UI.
16. Frontend tests must verify that failed backend operations do not leave misleading UI state.
17. Security-sensitive UI behavior must have corresponding server-side tests.
18. Frontend tests must remain maintainable as the application grows.
19. Visual consistency must not be tested through excessive brittle snapshots.
20. User-visible correctness takes priority over implementation-specific assertions.

---

# 4. Frontend Test Layers

Frontend testing is divided into several complementary layers:

```text
Component / Unit Tests
        ↓
Frontend Integration Tests
        ↓
API / Boundary Tests
        ↓
Frontend Workflow Tests
        ↓
End-to-End Tests
```

Cross-cutting testing applies to all layers:

```text
Accessibility
Responsive Behavior
Permissions
Offline State
Error Handling
Performance
Browser Compatibility
```

Each layer must have a clearly defined responsibility.

---

# 5. Frontend Unit Testing

Frontend unit tests verify isolated frontend behavior.

Typical targets include:

* pure functions;
* formatters;
* validators;
* selectors;
* state transformations;
* calculation helpers;
* permission-display helpers;
* date/time formatting;
* currency formatting;
* quantity formatting;
* UI state transitions.

Unit tests should not require:

* a real backend;
* a real database;
* a real browser session where unnecessary;
* external network access;
* real printers;
* real authentication services.

---

# 6. Component Testing

Component tests verify an individual UI component in isolation.

Examples:

* Button;
* Input;
* Select;
* Date picker;
* Table;
* Pagination;
* Modal;
* Confirmation dialog;
* Notification;
* Status badge;
* Product card;
* Order item;
* Recipe component;
* Stock indicator.

Tests should verify observable behavior.

Example:

```text id="5s4e9m"
Given:
Stock is below threshold

Then:
Low-stock indicator is displayed
```

The test should not depend on internal implementation details such as private state variable names.

---

# 7. Component State Testing

Interactive components commonly have multiple states.

Every important state must be tested.

Example:

```text id="n5yt8e"
Button:
- enabled
- disabled
- loading
- success
- error
```

Example:

```text id="a2m8zq"
Data table:
- loading
- populated
- empty
- error
- filtered
- paginated
```

Tests must verify that each state produces the correct user-visible behavior.

---

# 8. Form Testing

Forms are a major frontend boundary.

Tests must cover:

* initial values;
* required fields;
* optional fields;
* valid input;
* invalid input;
* boundary values;
* empty input;
* whitespace;
* duplicate values;
* field dependencies;
* server validation errors;
* submission state;
* successful submission;
* failed submission;
* reset/cancel behavior.

Forms must not show a false success state when the backend rejects the operation.

---

# 9. Client-Side Validation

Client-side validation improves user experience but does not replace backend validation.

Tests must verify:

* expected validation messages;
* invalid input prevention where appropriate;
* valid input acceptance;
* correct field association;
* server-side validation error display;
* no loss of user-entered data after recoverable failure.

The test architecture must preserve the distinction:

```text
Frontend validation
        ↓
User experience

Backend validation
        ↓
Authoritative business rule
```

---

# 10. Frontend Integration Testing

Frontend integration tests verify interactions between multiple frontend elements.

Examples:

```text id="x0w4vi"
Product Selection
      ↓
Order State
      ↓
Order Summary
      ↓
Price Display
```

Tests must verify that changing one UI state correctly updates related UI state.

Other examples include:

* filter + table;
* form + validation;
* modal + confirmation;
* navigation + page state;
* branch selector + branch-specific data;
* permission state + available actions;
* order item + total;
* recipe modification + price;
* inventory state + product availability.

---

# 11. Frontend API Boundary Testing

Frontend integration tests must verify how the UI reacts to API outcomes.

Important API outcomes include:

* success;
* validation error;
* unauthorized;
* forbidden;
* not found;
* conflict;
* timeout;
* server error;
* network failure;
* offline state.

Example:

```text id="1vrj0a"
API:
403 Forbidden

Expected UI:
Operation is not presented as successful.
Protected action is not completed.
User receives appropriate feedback.
```

The frontend must not interpret an error response as a successful business operation.

---

# 12. Authentication UI Testing

Authentication screens must be tested for:

* login;
* invalid credentials;
* disabled account;
* session expiration;
* logout;
* verification flow;
* unfamiliar-device verification;
* recovery flow;
* network failure;
* loading state;
* repeated submission.

Tests must verify that authentication state is reflected correctly throughout the application.

---

# 13. Authorization-Aware UI Testing

The frontend may adapt its interface according to the user's permissions.

Examples:

```text id="bqfj4j"
Permission:
Inventory View = Allowed
Inventory Adjustment = Denied
```

Expected UI may:

* show inventory;
* hide or disable adjustment controls.

However, the test must also verify the corresponding API behavior separately.

Frontend UI restrictions are usability behavior, not the authoritative security boundary.

---

# 14. Branch-Aware UI Testing

Branch context is a critical frontend state.

Tests must verify:

* current branch display;
* branch selection;
* allowed branch list;
* unauthorized branch absence;
* branch-specific data refresh;
* branch switching;
* branch-specific forms;
* branch-specific reports;
* branch-specific inventory;
* branch-specific orders.

Example:

```text id="uw7zyl"
Branch 1 selected
        ↓
Branch 1 data displayed
```

Switching to Branch 2 must not leave stale Branch 1 information visible as if it belonged to Branch 2.

---

# 15. Tenant-Aware UI Testing

Frontend state must correctly represent the active business context.

Tests must verify:

* current business context;
* navigation;
* data loading;
* cached data;
* reports;
* search;
* branch lists;
* employee lists.

When business context changes, protected data from the previous context must not remain visible through stale frontend state.

---

# 16. Navigation Testing

Navigation tests must verify:

* valid routes;
* invalid routes;
* protected routes;
* role-dependent navigation;
* branch-dependent navigation;
* redirects;
* browser back/forward;
* refresh;
* deep links;
* session expiration during navigation.

Tests must ensure that a protected page does not become accessible merely by manually entering its route.

The actual authorization remains server-side.

---

# 17. POS UI Testing

POS is one of the highest-priority frontend areas.

Critical POS behavior includes:

```text id="i4v2pj"
Cashier Login
      ↓
Correct Branch
      ↓
Cash Session Open
      ↓
Product Selection
      ↓
Order Creation
      ↓
Order Modification
      ↓
Order Acceptance
      ↓
Payment
      ↓
Order Completion
      ↓
Cash / Financial Update
```

Frontend tests must verify that each transition is correctly reflected in the UI.

---

# 18. POS Product Selection Testing

Tests must cover:

* product display;
* active/inactive products;
* category selection;
* search;
* quantity changes;
* unavailable products;
* low-stock indicators where shown;
* product images where configured;
* price display;
* branch-specific availability.

The UI must not allow a visibly unavailable product to appear as successfully added without the appropriate backend validation.

---

# 19. POS Order Modification Testing

Tests must cover:

* adding products;
* removing products;
* quantity changes;
* recipe component modification where allowed;
* discounts;
* order type;
* customer delivery information;
* comments;
* recalculation.

Example:

```text id="g1j2y6"
Recipe component removed
        ↓
Price recalculated
        ↓
Order total updated
```

The UI must not display a stale total after a valid order modification.

---

# 20. POS Order State Testing

Order states displayed by the frontend must correspond to the backend state.

Tests should cover:

* created;
* accepted;
* preparing;
* ready;
* completed;
* cancelled;
* refunded where applicable.

If item-level status is supported, tests must also verify:

* individual item status;
* mixed item states;
* status visibility;
* status transitions.

The frontend must not invent a completed state when the backend operation failed.

---

# 21. Payment UI Testing

Payment is a critical frontend boundary.

Tests must cover:

* correct total;
* payment method;
* successful payment;
* failed payment;
* timeout;
* repeated payment attempt;
* duplicate submission;
* cancellation;
* payment confirmation;
* final order state.

A repeated click must not create a misleading second success state.

The backend remains authoritative for payment state.

---

# 22. Cash Session UI Testing

Tests must cover:

* session opening;
* customer-facing 3-digit number;
* cash count;
* session state;
* handover;
* closing;
* shortage indication;
* correction state;
* privileged reopen state.

The UI must distinguish:

```text id="z8qz74"
Customer-facing session number
```

from:

```text id="jwm0w3"
Persistent database/session identity
```

The frontend must display the correct value for each use case.

---

# 23. Inventory UI Testing

Inventory screens must be tested for:

* stock quantity;
* product type;
* branch;
* warehouse;
* FIFO-related information where exposed;
* low-stock state;
* stock receipt;
* adjustment;
* discrepancy;
* search;
* filtering;
* pagination.

Tests must verify that a successful backend inventory operation produces the correct UI state.

Failed operations must not leave the interface showing the operation as completed.

---

# 24. Recipe UI Testing

Recipe UI tests must cover:

* recipe creation;
* component selection;
* component quantity;
* recipe editing;
* recipe approval;
* archived recipes;
* restricted recipe visibility;
* recipe version display;
* semi-finished dependencies.

Example:

```text id="0xg4jz"
Recipe:
Lavash
 ├── Meat Filling
 └── Sauce
```

The UI must represent the dependency structure correctly.

---

# 25. Semi-Finished Product UI Testing

Tests must verify that semi-finished products are distinguishable from raw ingredients and ready products where the UI exposes product type.

Tests should cover:

* product type selection;
* recipe composition;
* production;
* source;
* stock display;
* dependency visualization where supported.

The UI must not imply that a semi-finished product is a raw ingredient when the business model treats them differently.

---

# 26. Employee and Permission UI Testing

Employee-management interfaces must be tested for:

* employee creation;
* role selection;
* branch assignment;
* permission assignment;
* permission templates;
* permission changes;
* permission revocation;
* effective permission display.

Tests must verify that the interface accurately represents the resulting authorization state.

A UI that shows "Allowed" while the backend correctly denies the operation represents a frontend defect.

---

# 27. Reports UI Testing

Reports must be tested for:

* date selection;
* branch selection;
* filters;
* loading;
* empty results;
* populated results;
* errors;
* pagination;
* export;
* selected-day reports.

Tests must verify that changing a filter refreshes the displayed data correctly.

The UI must not mix data from:

* different branches;
* different businesses;
* different dates;
* previous queries.

---

# 28. Search and Filter Testing

Search/filter behavior must cover:

* empty search;
* exact search;
* partial search;
* no results;
* multiple filters;
* filter reset;
* pagination after filtering;
* sorting;
* rapid input changes;
* failed requests.

Tests must verify that stale responses do not overwrite newer search results.

---

# 29. Pagination Testing

Pagination tests must cover:

* first page;
* middle page;
* last page;
* empty page;
* changing page size;
* filtering followed by pagination;
* sorting followed by pagination;
* refreshed data.

The frontend must correctly handle the backend pagination contract defined by the API.

---

# 30. Loading State Testing

Every important asynchronous operation must have an appropriate loading behavior.

Tests must verify:

* loading indicator;
* disabled duplicate submission where required;
* preserved context;
* loading completion;
* loading failure.

Loading indicators must not remain indefinitely after a failed request.

---

# 31. Error State Testing

Error states must be treated as normal UI states.

Tests must cover:

* validation errors;
* forbidden;
* not found;
* conflict;
* server errors;
* network failure;
* timeout;
* offline state;
* synchronization failure.

The UI must:

* communicate the problem clearly;
* avoid claiming success;
* preserve recoverable user input where appropriate;
* provide an appropriate recovery action;
* avoid exposing sensitive technical information.

---

# 32. Empty State Testing

Empty data is different from an error.

Tests must distinguish:

```text id="5wq7t8"
No products exist
```

from:

```text id="x4q2bc"
Products failed to load
```

The UI must not display an empty state when the actual reason is a failed request.

---

# 33. Notification and Alert Testing

Tests must cover:

* success notifications;
* error notifications;
* warnings;
* subscription alerts;
* stock alerts;
* salary alerts;
* refund alerts;
* inventory variance alerts;
* branch loss alerts.

Notifications must correspond to actual backend events and must not be displayed as successful completion when the underlying operation failed.

---

# 34. Offline UI Testing

Offline mode is a first-class frontend state.

Tests must verify:

* offline indicator;
* available offline functionality;
* unavailable functionality;
* locally saved operations;
* synchronization status;
* pending operations;
* synchronization success;
* synchronization failure;
* rejected operations;
* recovery after reconnection.

Example:

```text id="e6p5l4"
Connection Lost
      ↓
Offline Indicator
      ↓
Supported operation
      ↓
Local persistence
      ↓
Pending Sync
      ↓
Connection Restored
      ↓
Synchronization
      ↓
Final State
```

The UI must never display an operation as permanently synchronized before synchronization has actually succeeded.

---

# 35. Synchronization UI Testing

Tests must cover synchronization states such as:

```text id="z2n6wp"
Pending
Syncing
Synchronized
Failed
Rejected
Requires Attention
```

The exact state names may follow the frontend design system, but the underlying business meanings must remain distinguishable.

Tests must verify that a failed synchronization does not disappear from the user's view as if it succeeded.

---

# 36. Offline Conflict UI Testing

When a synchronization conflict requires user-visible handling, tests must verify:

* conflict notification;
* affected operation;
* safe explanation;
* available resolution options;
* no accidental duplicate operation;
* final state after resolution.

The UI must not silently overwrite authoritative server state.

---

# 37. Responsive UI Testing

Responsive behavior must be tested for supported screen classes.

Typical classes may include:

* desktop;
* laptop;
* tablet;
* supported POS display sizes.

Tests should verify:

* navigation;
* tables;
* forms;
* dialogs;
* POS controls;
* reports;
* inventory screens;
* recipe editors.

Responsive behavior must preserve usability and critical functionality.

---

# 38. Accessibility Testing

Accessibility is part of frontend correctness.

Tests should cover:

* keyboard navigation;
* focus management;
* form labels;
* accessible names;
* error association;
* dialog focus;
* sufficient semantic structure;
* status communication;
* disabled controls;
* screen-reader-relevant states where applicable.

Critical POS workflows should remain usable with the supported accessibility behavior defined by the product.

---

# 39. Browser Compatibility Testing

Supported browsers must be explicitly defined by the frontend architecture.

For each supported browser class, critical workflows should verify:

* authentication;
* navigation;
* POS;
* orders;
* inventory;
* recipes;
* reports;
* offline behavior where supported.

Browser-specific defects must not be accepted merely because another browser works.

---

# 40. Frontend State Management Testing

Where the frontend maintains shared state, tests must verify:

* initial state;
* state updates;
* state reset;
* branch change;
* logout;
* permission change;
* synchronization;
* API failure;
* cache invalidation.

A logout or business/branch context change must not leave protected data in an active UI state.

---

# 41. Frontend Cache Testing

Caching must not create stale or cross-scope data exposure.

Tests must verify:

* cache population;
* cache invalidation;
* branch switching;
* business context switching;
* logout;
* permission changes;
* updated records;
* failed refresh.

Example:

```text id="1o7m4a"
Branch 1 data cached
        ↓
Switch to Branch 2
        ↓
Branch 1 data must not appear as Branch 2 data
```

Cache behavior must preserve tenant and branch boundaries.

---

# 42. Duplicate Submission Testing

Critical actions must be tested against repeated user interaction.

Examples:

* payment;
* order acceptance;
* refund;
* inventory adjustment;
* recipe approval;
* employee creation;
* permission change.

Tests must verify that rapid repeated interaction does not produce unintended duplicate operations.

The frontend may prevent duplicate clicks for usability, but backend idempotency remains authoritative.

---

# 43. Confirmation Dialog Testing

Destructive or privileged actions should use appropriate confirmation behavior where defined.

Tests must verify:

* correct action description;
* cancel behavior;
* confirm behavior;
* loading state;
* failure behavior;
* no action after cancellation.

Cancelling a confirmation dialog must produce no business side effect.

---

# 44. File Upload and Import UI Testing

Tests must cover:

* file selection;
* unsupported file;
* invalid format;
* oversized file;
* upload progress where applicable;
* server validation error;
* successful import;
* partial/rejected records;
* retry behavior.

The frontend must not treat file selection as equivalent to successful server-side import.

---

# 45. Export UI Testing

Tests must cover:

* authorized export;
* unauthorized export;
* filters applied to export;
* export loading;
* export failure;
* generated file availability.

The exported dataset must correspond to the authorized scope and selected filters.

---

# 46. Visual Regression Testing

Visual regression testing may be used for stable, high-value interfaces.

Recommended targets include:

* POS;
* main dashboard;
* navigation;
* major forms;
* inventory tables;
* recipe editor;
* reports;
* dialogs.

Visual snapshots should not become the primary testing mechanism for business behavior.

Tests should focus on meaningful visual changes rather than insignificant rendering differences.

---

# 47. Snapshot Testing

Snapshots may be used selectively.

Good candidates:

* stable presentation structures;
* complex static component output;
* defined design-system components.

Poor candidates:

* highly dynamic business screens;
* frequently changing data;
* entire application pages;
* snapshots used instead of behavioral assertions.

A snapshot should not be the only evidence that a critical business workflow works correctly.

---

# 48. Frontend Test Data

Frontend tests should use deterministic data.

Test data should include:

* normal products;
* unavailable products;
* multiple branches;
* multiple employees;
* different roles;
* different permissions;
* orders in different states;
* inventory with low stock;
* recipes with multiple components;
* semi-finished products;
* financial states;
* offline operations;
* API failures.

Tests must avoid depending on production data.

---

# 49. Mocking and Test Doubles

Frontend tests may use:

* mocked API responses;
* fake services;
* controlled state;
* deterministic timers;
* controlled browser APIs.

Mocking should represent meaningful external behavior.

Tests must not over-mock the component's own behavior.

For example, a component that should react to a `403 Forbidden` response should receive a realistic forbidden response rather than a mock that directly sets an internal "forbidden" state.

---

# 50. Time and Timer Testing

Frontend behavior involving time must be deterministic.

Examples:

* subscription expiration;
* session timeout;
* notification timing;
* order elapsed time;
* synchronization retry;
* report date selection.

Tests should control time rather than using arbitrary delays.

Tests must not depend on:

```text id="90s3hk"
sleep(1000)
```

as evidence that an asynchronous operation completed.

---

# 51. Critical Frontend E2E Suite

The frontend E2E suite should include at minimum:

### Authentication

1. Login.
2. Invalid login.
3. Logout.
4. Session expiration.
5. Device verification where applicable.

### POS

6. Open cash session.
7. Create order.
8. Add products.
9. Modify order.
10. Accept order.
11. Complete payment.
12. Verify final order state.
13. Close cash session.

### Inventory

14. View stock.
15. Receive stock.
16. Verify updated stock.
17. Perform authorized adjustment.
18. Verify unauthorized adjustment is blocked.

### Recipes

19. Create/edit recipe with permission.
20. Verify restricted recipe behavior.
21. Approve recipe.
22. Verify recipe appears in the expected menu scope.

### Permissions

23. Login as restricted employee.
24. Verify restricted UI.
25. Attempt protected operation directly.
26. Verify operation is rejected.

### Branch Isolation

27. Switch between permitted branches.
28. Verify branch-specific data.
29. Attempt unauthorized branch access.

### Offline

30. Enter offline state.
31. Perform supported operation.
32. Verify pending synchronization.
33. Restore connection.
34. Verify synchronization result.

### Reports

35. Open selected-day report.
36. Apply filters.
37. Verify displayed data.

These tests should remain limited to the most business-critical workflows.

---

# 52. Frontend Test Pyramid

Frontend testing should generally follow:

```text
                 E2E
              /       \
        Workflow / Critical UI
          Integration Tests
       /                    \
 Component / Integration / API Boundary
       \                    /
              Unit Tests
```

The majority of frontend tests should be fast unit/component/integration tests.

E2E tests should cover critical workflows rather than every possible UI variation.

---

# 53. Frontend Test Selection

A frontend change should trigger tests according to risk.

Examples:

| Change                | Minimum Testing                      |
| --------------------- | ------------------------------------ |
| Formatter             | Unit                                 |
| Button behavior       | Component                            |
| Form                  | Component + integration              |
| API data handling     | Integration                          |
| Permission-aware page | Integration + authorization boundary |
| POS payment UI        | Integration + E2E                    |
| Navigation            | Integration + selected E2E           |
| Offline UI            | Integration + offline E2E            |
| Major dashboard       | Component + integration + visual     |
| Global state          | Integration + affected E2E           |
| Authentication flow   | Integration + E2E                    |
| Branch context        | Integration + isolation E2E          |

The complete test suite should be selected according to change impact.

---

# 54. Flaky Frontend Test Management

Frontend tests are especially vulnerable to timing-related flakiness.

Tests must avoid:

* arbitrary sleeps;
* uncontrolled network timing;
* random data;
* shared browser state;
* test-order dependencies;
* uncontrolled animations;
* external services.

Tests should wait for observable conditions rather than elapsed time.

A flaky security or POS E2E test must not simply be disabled to make CI pass.

---

# 55. Frontend E2E Isolation

E2E tests must isolate:

* user session;
* browser state;
* business context;
* branch context;
* test data;
* local storage;
* cookies;
* cached state;
* offline state.

A previous test must not determine whether the next test succeeds.

---

# 56. Frontend Performance Testing

Frontend performance testing should cover critical workflows without turning every UI test into a performance test.

Important areas include:

* POS product selection;
* large product lists;
* large order lists;
* inventory tables;
* reports;
* recipe editors;
* search;
* pagination;
* navigation;
* initial application loading.

Performance optimization must not compromise:

* authorization;
* state correctness;
* data integrity;
* offline behavior;
* user-visible accuracy.

---

# 57. Frontend Security Testing Relationship

Frontend tests must verify security-sensitive UI behavior, but they cannot prove complete security.

For example:

```text id="j7v4d9"
Button hidden
```

is a frontend behavior.

```text id="f0e8w7"
Unauthorized API operation rejected
```

is a security boundary.

Both should be tested, but they must not be confused.

The authoritative security tests are defined in:

`14_Authentication_Authorization_and_Security_Testing.md`

---

# 58. Frontend Offline Testing Relationship

Frontend offline tests verify user-visible behavior.

The underlying synchronization correctness is defined in:

`10_Offline_and_Synchronization_Testing.md`

Frontend tests should verify:

* offline indication;
* available actions;
* pending state;
* synchronization state;
* conflict/error presentation.

Synchronization tests must additionally verify server-side correctness and idempotency.

---

# 59. Frontend Defect Classification

Frontend defects should be classified according to their impact.

### Critical

Examples:

* payment UI shows success when payment failed;
* unauthorized operation appears completed;
* branch data displayed under another branch;
* offline operation is falsely shown as synchronized;
* order state is incorrectly shown as completed.

### High

Examples:

* important workflow cannot complete;
* incorrect inventory state displayed;
* permission-controlled UI exposes sensitive functionality;
* report shows incorrect business data.

### Medium

Examples:

* incorrect validation message;
* incorrect filtering;
* broken non-critical navigation;
* incorrect visual state.

### Low

Examples:

* minor visual inconsistency;
* spacing;
* non-critical presentation issue.

Severity must reflect business and security impact, not only visual appearance.

---

# 60. Regression Testing

Every important frontend defect should produce a regression test.

Examples:

```text id="jmx7fl"
Bug:
Payment button could be clicked twice and displayed two successes.

Regression:
Rapid repeated payment interaction must result in one valid payment state.
```

```text id="0c4qak"
Bug:
Branch switch displayed previous branch inventory.

Regression:
Switch branches and verify the old branch data is removed or replaced correctly.
```

```text id="3dbx7v"
Bug:
Offline operation displayed as synchronized before server confirmation.

Regression:
Offline operation must remain pending until synchronization succeeds.
```

---

# 61. CI Quality Gates

Frontend CI should include:

### Fast gate

* unit tests;
* component tests;
* frontend lint/type checks where applicable;
* basic accessibility checks.

### Integration gate

* API boundary behavior;
* permission-aware UI;
* branch-aware UI;
* important forms;
* state management.

### E2E gate

* authentication;
* critical POS;
* payment;
* inventory;
* permissions;
* branch isolation;
* offline critical workflows.

### Release gate

* critical frontend regression suite;
* supported browser checks;
* accessibility checks;
* selected visual regression checks;
* critical E2E suite.

Critical failures must block release.

---

# 62. Change Impact Testing

Frontend test review is required when changing:

* global navigation;
* authentication;
* authorization UI;
* branch selector;
* business context;
* POS;
* payment;
* order state;
* inventory;
* recipes;
* employee permissions;
* reports;
* offline behavior;
* synchronization;
* shared state;
* API contracts;
* caching;
* routing;
* design-system components.

Global components require broader regression testing because a small change can affect many workflows.

---

# 63. Frontend Testing Anti-Patterns

The following practices are prohibited or strongly discouraged:

### Testing implementation details

Example:

```text id="n4b9z2"
Assert internal state variable equals X
```

when the actual requirement is a visible behavior.

### Testing only happy paths

A successful API response is not enough.

### Treating UI hiding as security

A hidden button does not protect an API.

### Excessive E2E

Every small component should not require a full browser workflow.

### Excessive snapshots

Large snapshots become difficult to maintain and provide weak business evidence.

### Arbitrary sleeps

Timing delays should not be used as synchronization.

### Shared browser state

Tests must not depend on previous tests.

### Ignoring errors

Error states are part of normal application behavior.

### Ignoring offline mode

Offline behavior is a defined product capability and requires dedicated testing.

### Disabling flaky security tests

Flakiness must be diagnosed and fixed rather than hidden.

---

# 64. Frontend Testing Invariants

The following are mandatory invariants.

### UI Correctness

1. The UI reflects the authoritative backend result.
2. Failed operations are not displayed as successful.
3. Loading states do not become permanent after recoverable failure.
4. Empty states are distinguishable from errors.
5. Important state transitions are visible to the user.

### Authentication

6. Protected screens require the appropriate authentication state.
7. Logout removes protected frontend state.
8. Expired authentication is handled correctly.

### Authorization

9. Permission-aware UI reflects the user's effective permissions.
10. Hidden UI controls are not treated as security enforcement.
11. Unauthorized backend responses are handled safely.
12. Permission changes are reflected according to the defined consistency model.

### Tenant and Branch

13. UI data is associated with the correct business context.
14. UI data is associated with the correct branch context.
15. Switching context does not leak stale protected data.
16. Search and reports respect the current scope.

### POS

17. Order totals reflect the current order state.
18. Payment UI reflects the authoritative payment state.
19. Duplicate interaction does not create misleading duplicate success.
20. Cash-session state is represented correctly.

### Inventory and Recipes

21. Stock state displayed by the UI reflects the latest authoritative state.
22. Recipe modifications update dependent UI values correctly.
23. Inventory failures do not appear as successful changes.

### Offline

24. Offline state is visible.
25. Pending operations are distinguishable from synchronized operations.
26. Failed synchronization is not presented as successful synchronization.
27. Rejected operations remain understandable to the user.

### Accessibility and Reliability

28. Critical workflows are keyboard/accessibility testable according to supported requirements.
29. Supported screen sizes preserve critical functionality.
30. Frontend tests remain deterministic and isolated.

---

# 65. Acceptance Criteria

This document is considered correctly implemented when:

* frontend unit testing is defined;
* component testing is defined;
* frontend integration testing is defined;
* API boundary behavior is tested;
* authentication UI is tested;
* authorization-aware UI is tested;
* branch and tenant context are tested;
* forms and validation are tested;
* POS workflows have dedicated coverage;
* payment UI has dedicated coverage;
* inventory and recipe UI behavior is tested;
* reports and filters are tested;
* loading, empty, and error states are tested;
* offline and synchronization UI is tested;
* responsive behavior is tested;
* accessibility is included;
* browser compatibility is covered for supported browsers;
* frontend state and cache behavior are tested;
* duplicate submission behavior is tested;
* critical E2E workflows are defined;
* visual regression is used selectively;
* frontend security behavior is distinguished from server-side security enforcement;
* critical frontend tests run in CI;
* critical frontend regressions block release;
* flaky tests are investigated rather than hidden.

---

# 66. Final Frontend Testing Rule

Frontend testing is not complete merely because pages render correctly.

The frontend must prove that users can safely and predictably interact with the system:

```text id="v4y6m1"
User Action
    ↓
UI State
    ↓
Client Validation
    ↓
API Request
    ↓
Backend Result
    ↓
Frontend State Update
    ↓
User-Visible Result
```

For offline operations:

```text id="l6o3d5"
User Action
    ↓
Offline State
    ↓
Local Operation
    ↓
Pending Synchronization
    ↓
Server Synchronization
    ↓
Authoritative Result
    ↓
Final UI State
```

The final acceptance condition is:

> **The frontend is correctly tested only when critical user interactions produce the correct visible behavior, failed operations are represented honestly, authorization and scope are reflected correctly, offline states are distinguishable, POS workflows are reliable, and the UI never substitutes client-side behavior for authoritative backend security or business integrity.**

